from lib.py3270 import Emulator
import time
import logging
import os

delayScreen=1.5

def read_line(line, file="pantalla.txt"):
    # Abre el archivo en modo lectura
    with open(file, "r") as archivo:
        lineas = archivo.readlines()  # Lee todas las líneas del archivo

        if 0 <= line < len(lineas):
            linea_deseada = lineas[line]
            return linea_deseada.strip()  # strip() elimina los caracteres de nueva línea
        else:
            return 0

def _get_screen_text():
    """Lee el contenido de la pantalla actual como una cadena."""
    lines = []
    for row in range(1, 43 + 1):
        try:
            line = e.string_get(row, 1, 79)
        except Exception:
            line = ""
        lines.append(line)
    return "\n".join(lines)

def emulador(mylogin, mypass):
    """Implementa el flujo solicitado: conexión, login, navegación a tasks.c y listado de todas las tareas.

    Retorna:
      0 -> login correcto y flujo ejecutado
      1 -> no autorizado / contraseña incorrecta / fallo conexión
      2 -> usuario en uso
     -1 -> error no controlado
    """
    global e
    host = "155.210.152.51:3270"

    # Parámetros de espera del snippet
    retardo1 = 2
    retardo2 = 1
    login = -1

    try:
        # Preparar PATH para ws3270.exe (está en la carpeta padre de lib)
        logging.info("[TN3270] Preparando ws3270 en PATH y creando Emulator (no visible)")
        try:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
            ws_exe = os.path.join(base_dir, "ws3270.exe")
            if os.path.exists(ws_exe):
                os.environ["PATH"] = base_dir + os.pathsep + os.environ.get("PATH", "")
                logging.info("[TN3270] ws3270 detectado en %s. Añadido al PATH.", base_dir)
            else:
                logging.warning("[TN3270] ws3270.exe no encontrado en %s. Asegura que esté en PATH.", base_dir)
        except Exception:
            logging.exception("[TN3270] No se pudo preparar PATH para ws3270.exe")

        # Crear e inicializar emulador NO visible (en Windows usa Ws3270App)
        e = Emulator()

        # Conectar al emulador
        logging.info("[TN3270] Conectando a %s", host)
        e.connect(host)
        time.sleep(retardo1)
        logging.info("Pantalla de Music Mainframe")

        # Esperar campo inicial y avanzar
        logging.info("Esperando campo inicial...")
        e.wait_for_field()
        e.send_enter()

        logging.info("Pantalla de login")
        time.sleep(retardo2)
        logging.info("Esperando campo de usuario...")
        e.wait_for_field()

        # Usuario
        e.send_string(str(mylogin))
        e.send_enter()

        # Contraseña
        logging.info("Esperando campo de contraseña...")
        e.wait_for_field()
        e.send_string(str(mypass))
        e.send_enter()

        # Verificar inicio de sesión correcto
        time.sleep(retardo2)
        logging.info("Comprobando resultado del login...")
        login = comprobar_salida_login(e)

        if login == 0:
            logging.info("Inicio de sesión exitoso")
            logging.info("Pantalla de espera -> ENTER")
            e.wait_for_field()
            e.send_enter()

            logging.info("Pantalla de comandos; ejecutando tasks.c")
            time.sleep(retardo2)
            e.wait_for_field()
            e.send_string("tasks.c")
            e.send_enter()

            # Menú tareas
            time.sleep(retardo2)
            logging.info("Pantalla menú de tareas")

            # Listar tareas -> opción 2
            time.sleep(retardo2)
            e.wait_for_field()
            e.send_string("2")
            e.send_enter()
            logging.info("Pantalla menú listar tareas")
            time.sleep(retardo2)

            # Listar todas las tareas -> opción 2
            time.sleep(retardo2)
            e.wait_for_field()
            e.send_string("2")
            e.send_enter()
            logging.info("Listar todas las tareas")

            time.sleep(retardo2)
            # Guardar pantalla en HTML si es posible; si no, fallback a txt envuelto en <pre>
            filename_html = "pantalla_lista_todas_las_tareas.html"
            try:
                if hasattr(e, "save_screen"):
                    e.save_screen(filename_html)
                else:
                    raise AttributeError("save_screen no disponible")
            except Exception:
                try:
                    # Captura a txt y vuelca como HTML simple
                    pantalla("pantalla_lista_todas_las_tareas.txt")
                    with open("pantalla_lista_todas_las_tareas.txt", "r", encoding="utf-8", errors="ignore") as f_in, \
                         open(filename_html, "w", encoding="utf-8") as f_out:
                        f_out.write("<html><body><pre>\n")
                        f_out.write(f_in.read())
                        f_out.write("\n</pre></body></html>")
                except Exception:
                    logging.exception("No se pudo guardar la pantalla de listado de tareas")

            # Obtención y procesamiento opcional (placeholders compatibles con el snippet)
            lista_tareas = obtener_estructura_tareas(e)
            procesar_tareas(lista_tareas)

            return 0
        elif login == 1:
            logging.warning("Error: Usuario no autorizado o contraseña incorrecta")
            try:
                e.terminate()
            except Exception:
                pass
            return 1
        elif login == 2:
            logging.warning("Error: Usuario ya en uso")
            try:
                e.terminate()
            except Exception:
                pass
            return 2

    except Exception as ex:
        logging.exception("Error durante la ejecución de emulador(): %s", ex)
        try:
            if 'e' in globals() and e:
                e.terminate()
        except Exception:
            pass
        return -1
    finally:
        # Cerrar la conexión de forma correcta si el login fue OK
        try:
            if login == 0 and 'e' in globals() and e:
                time.sleep(retardo1)
                e.terminate()
                logging.info("Conexión terminada correctamente")
        except Exception:
            pass

def inicio_correcto():
    line=e.string_get(7,2,24)
    # print("Linea 1: ",line)
    if line=="Userid is not authorized":
        return 1
    line=e.string_get(7,2,18)
    # print("Linea 2: ",line)
    if line=="Password incorrect":
        return 1
    line=e.string_get(1,1,16)
    # print("Linea 3: ",line)
    if line.rstrip()=="Userid is in use":
        return 2
    return 0

def comprobar_salida_login(em=None):
    """Equivalente a inicio_correcto() pero con firma compatible con el snippet."""
    try:
        _e = em if em is not None else e
        if _e is None:
            return 1
        # Reutilizamos la lógica existente
        line=_e.string_get(7,2,24)
        if line=="Userid is not authorized":
            return 1
        line=_e.string_get(7,2,18)
        if line=="Password incorrect":
            return 1
        line=_e.string_get(1,1,16)
        if line.rstrip()=="Userid is in use":
            return 2
        return 0
    except Exception:
        logging.exception("Error comprobando la salida del login")
        return 1

def pantalla(filename="pantalla.txt"):
    time.sleep(0.5)
    screen_content = ''
    for row in range(1, 43 + 1):
        line = e.string_get(row, 1, 79)
        screen_content += line + '\n'
    archivo = open(filename, "w")
    archivo.write(screen_content)
    archivo.close()

def obtener_estructura_tareas(em=None):
    """Placeholder compatible con el snippet: obtiene estructura de la pantalla actual.

    Si quieres un parseo real, puedes combinar get_tasks_general/specific
    navegando los submenús, pero aquí devolvemos una lista vacía o el
    contenido crudo si se quiere enriquecer más adelante.
    """
    try:
        pantalla("pantalla_lista_todas_las_tareas.txt")
        # Retornar estructura vacía por defecto (no usada por la app Flask actual)
        return []
    except Exception:
        logging.exception("No se pudo obtener la estructura de tareas")
        return []

def procesar_tareas(lista_tareas):
    """Placeholder: registra el conteo de tareas; pensado para desarrollo local."""
    try:
        logging.info("procesar_tareas(): %d elementos", len(lista_tareas) if lista_tareas is not None else 0)
    except Exception:
        pass

# Opción ASSIGN TASKS
def assign_tasks(tipo:str, fecha:str, desc:str, nombre:str):
    desc = '"' + desc.replace(" ", " ") + '"'
    nombre = '"' + nombre.replace(" ", " ") + '"'
    
    logging.info(f'Asignando tarea especifica: FECHA={fecha}, NOMBRE={nombre}  DESCRIPCION={desc} TIPO={tipo}')
   
    e.wait_for_field()
    e.send_string("1")
    logging.info("send string 1 check")
    e.send_enter()
    logging.info("send enter 1 check")
    e.delete_field()

    if tipo=="General":
        e.send_string("1")
        e.send_enter()
        e.delete_field()
        
        e.send_string(fecha)
        e.send_enter()
        e.delete_field()
        
        e.send_string(desc)
        e.send_enter()
        e.delete_field()

    elif tipo=="Especifica":
        
        e.wait_for_field()
        logging.info("Asignando tarea específica")
        e.send_string("2")
        logging.info("send string check")
        e.send_enter()
        logging.info("send enter check")
        e.delete_field()
        logging.info("delete field check")
        
        e.wait_for_field()
        e.send_string(fecha)
        logging.info("send string fecha check") 
        e.send_enter()
        logging.info("send enter fecha check")
        e.delete_field()
        logging.info("delete field fecha check")
        
        e.wait_for_field()
        e.send_string(nombre)
        logging.info("send string nombre check")
        e.send_enter()
        logging.info("send enter nombre check")
        e.delete_field()
        logging.info("delete field nombre check")
        
        e.wait_for_field()
        e.send_string(desc)
        logging.info("send string desc check")
        e.send_enter()
        logging.info("send enter desc check")
        e.delete_field()
        logging.info("delete field desc check")
    
    e.wait_for_field()
    e.send_string("3")
    logging.info("send string 3 check")
    e.send_enter()
    logging.info("send enter 3 check")
    e.delete_field()
    logging.info("delete field 3 check")

def get_tasks_general(file="pantalla.txt"):
    resultado = []
    for num_line in range(0, 43 + 1):
        line=read_line(num_line,file)
        if line!=0:
            if line.find("TOTAL TASK")!=-1:
                return resultado
            else:
                partes = line.split(" ")
                # print("PARTES: ",partes)
                if partes[0]=="TASK":
                    temp = {"fecha":partes[3],"descripcion":partes[5].strip('"')}
                    resultado.append(temp)
    # print("GENERAL: ", resultado)
    return resultado

def get_tasks_specific(file="pantalla.txt"):
    resultado = []
    for num_line in range(0, 43 + 1):
        line=read_line(num_line,file)
        # print(line)
        if line!=0:
            if line.find("TOTAL TASK")!=-1:
                return resultado
            else:
                partes = line.split(" ")
                # print("PARTES: ",partes)
                if partes[0]=="TASK":
                    temp = {"fecha":partes[3],"nombre":partes[4].strip('"'),"descripcion":partes[5].strip('"')}
                    resultado.append(temp)
    # print("SPECIFIC: ", resultado)
    return resultado

# Opción VIEW TASKS
def view_tasks():
    resultado=[]
    e.send_string("2")
    e.send_enter()
    e.delete_field()
    e.send_clear()
    e.send_string("1")
    e.send_enter()
    e.delete_field()
    pantalla()
    # print("AQUÍ 1")
    general = get_tasks_general()
    e.send_clear()
    e.send_string("2")
    e.send_enter()
    e.delete_field()
    pantalla()
    # print("AQUÍ 2")
    e.send_string("3")
    specific = get_tasks_specific()
    # print("AQUÍ 3")
    e.send_enter()
    e.delete_field()
    resultado = general + specific
    # print("General: ", general, "\nEspecifica: ", specific, "\nRESULTADO: ",resultado)
    return resultado

# Opción EXIT TASKS
def exit_tasks():
    global e
    e.send_string("3")
    e.send_enter()
    e.delete_field()
    e.send_string("off")
    e.send_enter()
    e.delete_field()
    time.sleep(0.5)
    e.terminate()
