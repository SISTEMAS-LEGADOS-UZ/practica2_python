from lib.py3270 import Emulator
import time

delayScreen=0.5

def read_line(line, file="pantalla.txt"):
    # Abre el archivo en modo lectura
    with open(file, "r") as archivo:
        lineas = archivo.readlines()  # Lee todas las líneas del archivo

        if 0 <= line < len(lineas):
            linea_deseada = lineas[line]
            return linea_deseada.strip()  # strip() elimina los caracteres de nueva línea
        else:
            return 0

def emulador(mylogin, mypass):
    global e, active_window
    # Main
    host = "155.210.152.51"
    port = "3270"
    # mylogin = 'GRUPO_03'
    # mypass = 'secreto6'

    e = Emulator(visible=True)
    e.connect(host + ':' + port)
    time.sleep(delayScreen)

    # Patalla inicio
    time.sleep(delayScreen)
    e.send_enter()

    # Pantalla Login
    time.sleep(delayScreen)
    ## Usuario
    e.wait_for_field()
    e.send_string(mylogin)
    e.send_enter()
    ## Contraseña
    e.wait_for_field()
    e.send_string(mypass)
    e.send_enter()

    # Chequear correcto inicio de sesion
    time.sleep(delayScreen)
    inicio = inicio_correcto()
    # print(inicio)
        
    if inicio==0:
        # Pantalla previa a comandos
        time.sleep(delayScreen)
        e.wait_for_field()
        e.send_enter()
        time.sleep(delayScreen)
        e.wait_for_field()
        e.send_string('PA1')
        e.send_enter()

        # Pantalla comandos
        time.sleep(delayScreen)
        e.wait_for_field()
        e.send_string('tareas.c')
        e.send_enter()
        return 0
    elif inicio==1:
        e.terminate()
        return 1
    elif inicio==2:
        e.terminate()
        return 2

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

# Guardar lo que se lee por pantalla en un fichero 
def pantalla(filename="pantalla.txt"):
    time.sleep(0.5)
    screen_content = ''
    for row in range(1, 43 + 1):
        line = e.string_get(row, 1, 79)
        screen_content += line + '\n'
    archivo = open(filename, "w")
    archivo.write(screen_content)
    archivo.close()

# Opción ASSIGN TASKS
def assign_tasks(tipo:str, fecha:str, desc:str, nombre:str):
    desc = '"' + desc.replace(" ", " ") + '"'
    nombre = '"' + nombre.replace(" ", " ") + '"'

    e.send_string("1")
    e.send_enter()
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
        e.send_string("2")
        e.send_enter()
        e.delete_field()
        e.send_string(fecha)
        e.send_enter()
        e.delete_field()
        e.send_string(nombre)
        e.send_enter()
        e.delete_field()
        e.send_string(desc)
        e.send_enter()
        e.delete_field()
    
    e.send_string("3")
    e.send_enter()
    e.delete_field()

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
