from lib.py3270 import Emulator
import time
import logging
import os
import re

# Cache de la última lista de tareas (ALL TASKS) para usarla en la UI
_last_all_tasks = []

delayScreen=1.5

def _settle(delay: float = 0.5):
    """Pequeña espera para que el host 'pinte' la siguiente pantalla.

    Sustituye a antiguas capturas TXT de depuración que incluían un sleep implícito.
    """
    try:
        try:
            e.wait_for_field()
        except Exception:
            pass
        time.sleep(delay)
    except Exception:
        # No queremos que un fallo aquí rompa el flujo
        pass

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
            logging.info("Pantalla menú de tareas")

            # Listar tareas -> opción 2
            time.sleep(retardo2)
            e.wait_for_field()
            e.send_string("2")
            e.send_enter()
            logging.info("Pantalla menú listar tareas")

            # Listar todas las tareas -> opción 3
            time.sleep(retardo2)
            e.wait_for_field()
            e.send_string("3")
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


        
            logging.info("Volviendo a main menu...")
            return_main_menu()
            
            # [DEBUG desactivado] Antes se guardaba una captura en TXT solo para depuración.
            # pantalla("Emulador_login_fin.txt")
            _settle(0.5)

            
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
        # No cerramos la conexión si el login fue OK, para que el resto de acciones (assign/view/refresh)
        # puedan reutilizar la misma sesión TN3270. El cierre se realiza explícitamente en exit_tasks().
        try:
            if login == 0 and 'e' in globals() and e:
                logging.info("Sesión TN3270 permanece abierta para operaciones posteriores")
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

def dump_screen_debug(prefix: str = "debug_screen"):
    """Depuración sin artefactos .txt.

    Anteriormente generaba un fichero TXT con timestamp mediante `pantalla(...)`.
    Se ha desactivado la creación de archivos de texto para evitar residuos de depuración.
    Se mantiene un log informativo en su lugar.
    """
    try:
        ts = time.strftime("%Y%m%d-%H%M%S")
        # fname = f"{prefix}_{ts}.txt"  # [DEBUG desactivado] No se crea fichero
        logging.info("[DEBUG] Captura omitida (sin .txt) para prefix=%s ts=%s", prefix, ts)
    except Exception:
        logging.exception("No se pudo registrar el evento de depuración")

def capture_all_tasks_pages(save_file: str = "pantalla_lista_todas_las_tareas.txt", max_pages: int = 200) -> str:
    """Captura todas las páginas del listado 'ALL TASKS', pulsando ENTER hasta el final.

    - Comienza desde la pantalla actual del listado (opción 3 ya seleccionada).
    - Avanza con ENTER hasta encontrar la línea 'TOTAL TASKS'.
    - Escribe todas las líneas concatenadas en save_file.
    - Tras capturar la última página, pulsa ENTER para volver al menú.

    Devuelve la ruta del archivo generado con el volcado completo.
    """
    # Acumularemos solo las líneas de tareas para evitar duplicados y ruido de menú
    task_lines: list[str] = []
    seen_ids: set[int] = set()
    re_task = re.compile(r"^\s*TASK\s*#\s*(\d+)\s*:")
    try:
        for _ in range(max_pages):
            # Leer pantalla actual y acumular
            try:
                screen_text = _get_screen_text()
            except Exception:
                logging.exception("No se pudo leer la pantalla actual de ALL TASKS")
                screen_text = ""

            # Si hemos vuelto al menú intermedio, re-seleccionar opción 3
            if "VIEW TASKS" in screen_text and "LIST OF ALL TASKS" not in screen_text:
                try:
                    e.send_string("3")
                    e.send_enter()
                    e.wait_for_field()
                    # Refrescar el contenido ya en la lista para esta iteración
                    screen_text = _get_screen_text()
                except Exception:
                    logging.exception("No se pudo re-seleccionar 'ALL TASKS' desde el menú")

            # Extraer y acumular únicamente las líneas de tareas, evitando duplicados por id
            if screen_text:
                for ln in screen_text.splitlines():
                    m = re_task.match(ln)
                    if m:
                        try:
                            tid = int(m.group(1))
                        except Exception:
                            tid = None
                        if tid is not None and tid not in seen_ids:
                            seen_ids.add(tid)
                            task_lines.append(ln)

            # ¿Estamos en la última página? (aparece 'TOTAL TASKS')
            if "TOTAL TASKS" in screen_text:
                # Guardar todo y salir; después hay que aceptar con ENTER para volver
                try:
                    with open(save_file, "w", encoding="utf-8") as f:
                        f.write("\n".join(task_lines))
                except Exception:
                    logging.exception("No se pudo escribir el volcado de ALL TASKS en %s", save_file)

                # Salir de la pantalla de resumen
                try:
                    time.sleep(1)

                    e.send_enter()
                except Exception:
                    pass
                try:
                    e.wait_for_field()
                except Exception:
                    time.sleep(0.2)
                return save_file

            # No es la última página: avanzar
            try:
                e.send_enter()
            except Exception:
                logging.exception("Fallo al enviar ENTER para avanzar en ALL TASKS")
                break
            try:
                e.wait_for_field()
            except Exception:
                time.sleep(0.2)

        # Fallback: guardar lo que tengamos
        try:
            with open(save_file, "w", encoding="utf-8") as f:
                f.write("\n".join(task_lines))
        except Exception:
            logging.exception("No se pudo escribir el volcado parcial de ALL TASKS en %s", save_file)
        return save_file
    except Exception:
        logging.exception("Error inesperado capturando las páginas de ALL TASKS")
        # Intentar dejar algún artefacto para depuración
        try:
            with open(save_file, "w", encoding="utf-8") as f:
                f.write("\n".join(task_lines))
        except Exception:
            pass
        return save_file

def obtener_estructura_tareas(em=None):
    """Placeholder compatible con el snippet: obtiene estructura de la pantalla actual.

    Si quieres un parseo real, puedes combinar get_tasks_general/specific
    navegando los submenús, pero aquí devolvemos una lista vacía o el
    contenido crudo si se quiere enriquecer más adelante.
    """
    try:

        # Guardamos TODAS las páginas del listado "ALL TASKS"
        file_all = capture_all_tasks_pages("pantalla_lista_todas_las_tareas.txt")

        # Parseamos esa pantalla para devolver una estructura útil y la cacheamos
        global _last_all_tasks
        _last_all_tasks = parse_all_tasks(file_all)
        if not _last_all_tasks:
            # Si no hay tareas, guardamos la pantalla actual para depurar
            dump_screen_debug("all_tasks_empty")
        return _last_all_tasks
    except Exception:
        logging.exception("No se pudo obtener la estructura de tareas")
        return []

def _ensure_view_tasks_menu(max_steps: int = 20) -> bool:
    """Asegura que estamos en el menú 'VIEW TASKS' antes de abrir 'ALL TASKS'.

    - Si aparece 'ENTER ANY KEY TO CONTINUE' o 'Press enter to continue', pulsa ENTER.
    - Si aparece 'LIST OF ALL TASKS', pulsa ENTER para avanzar hasta salir (hasta que desaparezca el listado) y volver al menú.
    - Si aparece 'MAIN MENU', escribe '2' para entrar a 'VIEW TASKS'.
    - Devuelve True cuando detecta 'VIEW TASKS' sin el listado.
    """
    try:
        for _ in range(max_steps):
            text = _get_screen_text()
            if "VIEW TASKS" in text and "LIST OF ALL TASKS" not in text:
                return True
            if ("ENTER ANY KEY TO CONTINUE" in text) or ("Press enter to continue" in text):
                try:
                    e.send_enter(); e.wait_for_field()
                except Exception:
                    time.sleep(0.2)
                continue
            if "LIST OF ALL TASKS" in text:
                try:
                    e.send_enter(); e.wait_for_field()
                except Exception:
                    time.sleep(0.2)
                continue
            if "MAIN MENU" in text:
                try:
                    e.delete_field(); e.send_string("2"); e.send_enter(); e.wait_for_field()
                except Exception:
                    time.sleep(0.2)
                continue
            # Estado desconocido: avanzar
            try:
                e.send_enter(); e.wait_for_field()
            except Exception:
                time.sleep(0.2)
        logging.warning("_ensure_view_tasks_menu: no se alcanzó el menú 'VIEW TASKS'")
        return False
    except Exception:
        logging.exception("Error en _ensure_view_tasks_menu")
        return False

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
    # [DEBUG desactivado] captura sólo para depuración
    # pantalla("assign_tasks_ini.txt")
    _settle(0.5)
 
   
    e.wait_for_field()
    e.send_string("1")
    e.send_enter()
    e.delete_field()

    if tipo=="General":
        
        e.wait_for_field()
        e.send_string("1")
        e.send_enter()
        e.delete_field()
        
        e.wait_for_field()
        e.send_string(fecha)
        e.send_enter()
        e.delete_field()
  
        e.wait_for_field()
        e.send_string(desc)
        e.send_enter()
        e.delete_field()
        # [DEBUG desactivado] captura sólo para depuración
        # pantalla("assign_tasks_general_fin.txt")
        _settle(0.5)
        
    elif tipo=="Especifica":
        
        e.wait_for_field()
        e.send_string("2")
        e.send_enter()
        e.delete_field()
       
        
        e.wait_for_field()
        e.send_string(fecha)
        e.send_enter()
        e.delete_field()
       
        
        e.wait_for_field()
        e.send_string(nombre)
        e.send_enter()
        e.delete_field()
        
        e.wait_for_field()
        e.send_string(desc)
        e.send_enter()
        e.delete_field()
        # [DEBUG desactivado] captura sólo para depuración
        # pantalla("assign_tasks_especifica_fin.txt")
        _settle(0.5)
    
 
    return_main_menu()
    logging.info("Volviendo al menu inicial...")
    
    # [DEBUG desactivado] captura sólo para depuración
    # pantalla("Assign_task_fin.txt")
    _settle(0.5)

    

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

# Parser para la pantalla "ALL TASKS" (opción 3)
def parse_all_tasks(file: str = "pantalla_lista_todas_las_tareas.txt"):
    """Parses the 'ALL TASKS' screen into a list of dicts.

    Formatos esperados por línea (tolerantes a espacios):
      - TASK #n: GENERAL <fecha> ----- <descripcion>
      - TASK #n: SPECIFIC <fecha> <nombre> <descripcion>

    Devuelve una lista de elementos tipo:
      {"id": n, "tipo": "GENERAL"|"SPECIFIC", "fecha": str, "descripcion": str, "nombre": str|None}
    """
    tareas = []
    try:
        with open(file, "r", encoding="utf-8", errors="ignore") as f:
            lineas = [l.rstrip("\n") for l in f.readlines()]

        # Regex base para capturar id, tipo y el resto
        re_base = re.compile(r"^\s*TASK\s*#\s*(\d+)\s*:\s*(GENERAL|SPECIFIC)\s+(.*)$", re.IGNORECASE)
        re_general = re.compile(r"^(\d{2}-\d{2}-\d{4})\s*-+\s*(.*)$")

        for raw in lineas:
            m = re_base.match(raw)
            if not m:
                continue
            task_id = int(m.group(1))
            tipo = m.group(2).upper()
            resto = m.group(3).strip()

            item = {"id": task_id, "tipo": tipo, "fecha": None, "descripcion": "", "nombre": None}

            if tipo == "GENERAL":
                mg = re_general.match(resto)
                if mg:
                    item["fecha"] = mg.group(1)
                    item["descripcion"] = mg.group(2).strip().strip('"').strip("'")
                else:
                    # Fallback: sin separador '-----'
                    partes = resto.split()
                    if partes:
                        item["fecha"] = partes[0]
                        desc = " ".join(partes[1:]).strip()
                        # Eliminar guiones iniciales que puedan formar parte del separador
                        desc = re.sub(r"^\s*-+\s*", "", desc)
                        # Quitar comillas envolventes
                        desc = desc.strip().strip('"').strip("'")
                        item["descripcion"] = desc
            else:  # SPECIFIC
                # Esperamos: <fecha> <nombre> <descripcion>
                partes = resto.split()
                if partes:
                    item["fecha"] = partes[0]
                    if len(partes) >= 2:
                        item["nombre"] = partes[1].strip('"')
                    if len(partes) >= 3:
                        item["descripcion"] = " ".join(partes[2:]).strip('"').strip()

            tareas.append(item)

    except Exception:
        logging.exception("No se pudo parsear la pantalla de ALL TASKS")
    return tareas

def get_last_all_tasks():
    """Devuelve la última lista parseada de 'ALL TASKS' capturada durante emulador()."""
    return list(_last_all_tasks)

def refresh_all_tasks():
    """Renavega al menú de VIEW TASKS -> ALL TASKS y devuelve la lista parseada.

    Asume que la sesión TN3270 está activa y en el menú de tasks.c o similar.
    Deja la sesión en MAIN MENU
    """
    try:
        # Replicar exactamente la secuencia del emulador desde 'Pantalla menú de tareas'
        # time.sleep(delayScreen)
        logging.info("Pantalla menú de tareas (refresh)")

        # 1) Listar tareas -> opción 2
        # time.sleep(delayScreen)
        e.wait_for_field()
        e.send_string("2")
        e.send_enter()
        logging.info("Pantalla menú listar tareas (refresh)")
        # time.sleep(delayScreen)

        # 2) Listar todas -> opción 3
        # time.sleep(delayScreen)
        e.wait_for_field()
        e.send_string("3")
        e.send_enter()
        logging.info("Listar todas las tareas (refresh)")
        # time.sleep(delayScreen)

        # 3) Capturar todas las páginas y parsear
        file_all = capture_all_tasks_pages("pantalla_lista_todas_las_tareas.txt")
        
        global _last_all_tasks
        _last_all_tasks = parse_all_tasks(file_all)

        
        # 4) Regresa al main menu
        return_main_menu()
        # [DEBUG desactivado] captura sólo para depuración
        # pantalla("Refresh_all_task_fin.txt")
        _settle(0.3)

        if not _last_all_tasks:
            dump_screen_debug("after_refresh_empty")
        return _last_all_tasks
    
    

    except Exception:
        logging.exception("No se pudo refrescar la lista de ALL TASKS")
        return []

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
    try:
        if e:
            try:
                e.send_string("3")
                e.send_enter()
                e.delete_field()
            except Exception:
                # Puede no estar en ese menú; intentamos apagar igualmente
                pass
            try:
                e.send_string("off")
                e.send_enter()
                e.delete_field()
            except Exception:
                pass
            time.sleep(0.5)
            try:
                e.terminate()
            except Exception:
                pass
            logging.info("Sesión TN3270 finalizada en exit_tasks()")
    except Exception:
        logging.exception("Error finalizando la sesión en exit_tasks()")


def return_main_menu(max_steps: int = 20):
    global e
    """Asegura que estamos en el menú 'MAIN'

    - Si aparece 'ENTER ANY KEY TO CONTINUE' o 'Press enter to continue', pulsa ENTER.
    - Si aparece 'LIST OF ALL TASKS', pulsa ENTER para avanzar hasta salir (hasta que desaparezca el listado) y volver al menú.
    - Si aparece 'MAIN MENU', devuelve true
    - Si aparece'VIEW TASKS' sin el listado manda 0 y enter.
    """
    try:
        for _ in range(max_steps):
            text = _get_screen_text()
            # logging.info(text)
            if ("MAIN MENU" in text) and ("GENERAL TASKS" not in text) and ("ENTER ANY KEY TO CONTINUE" not in text):
                logging.info("main menu alcanzado")
                return True
            if "VIEW TASKS" in text and "LIST OF ALL TASKS" not in text:
                try:
                   e.wait_for_field(); e.send_string("0");e.send_enter();e.delete_field()
                except Exception:
                    time.sleep(0.2)
                continue
            if ("ENTER ANY KEY TO CONTINUE" in text) or ("Press enter to continue" in text):
                try:
                    e.wait_for_field();e.send_enter()
                except Exception:
                    time.sleep(0.2)
                continue
            if "LIST OF ALL TASKS" in text or "LIST OF GENERAL TASKS" in text or "LIST OF SPECIFIC TASKS" in text:
                try:
                    e.wait_for_field();e.send_enter(); e.delete_field()
                except Exception:
                    time.sleep(0.2)
                continue
            
            # Estado desconocido: avanzar
            try:
                 e.send_string("tasks.c");e.send_enter(); e.wait_for_field();e.delete_field()
            except Exception:
                time.sleep(0.2)
        logging.warning("_ensure_view_main_menu: no se alcanzó el menú 'VIEW TASKS'")
        return False
    except Exception:
        logging.exception("Error en _ensure_view_main_menu")
        return False
    