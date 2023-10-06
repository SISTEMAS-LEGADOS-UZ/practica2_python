from lib.py3270 import Emulator
import time
import ctypes


def minimize_window():
    ctypes.windll.user32.keybd_event(0x12, 0, 0, 0)  # Presiona la tecla Alt
    ctypes.windll.user32.keybd_event(0x20, 0, 0, 0)  # Presiona la tecla Espacio
    ctypes.windll.user32.keybd_event(0x20, 0, 2, 0)  # Suelta la tecla Espacio
    ctypes.windll.user32.keybd_event(0x12, 0, 2, 0)  # Suelta la tecla Alt
    ctypes.windll.user32.keybd_event(0x28, 0, 0, 0)  # Presiona la tecla flecha abajo
    ctypes.windll.user32.keybd_event(0x28, 0, 2, 0)  # Suelta la tecla flecha abajo
    ctypes.windll.user32.keybd_event(0x28, 0, 0, 0)  # Presiona la tecla flecha abajo
    ctypes.windll.user32.keybd_event(0x28, 0, 2, 0)  # Suelta la tecla flecha abajo
    ctypes.windll.user32.keybd_event(0x0D, 0, 0, 0)  # Presiona la tecla Enter
    ctypes.windll.user32.keybd_event(0x0D, 0, 2, 0)  # Suelta la tecla Enter
    


def emulador():
    global e, terminate
    # Main
    host = "155.210.152.51"
    port = "3270"
    mylogin = 'GRUPO_03'
    mypass = 'secreto6'
    delayScreen=0.5
    
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
def assign_tasks(tipo, fecha, desc, nombre):
    e.send_string("1")
    e.send_enter()

    if tipo=="General":
        e.send_string("1")
        e.send_enter()
        e.send_string(fecha)
        e.send_enter()
        e.send_string(desc)
        e.send_enter()

    elif tipo=="Especifico":
        e.send_string("2")
        e.send_enter()
        e.send_string(fecha)
        e.send_enter()
        e.send_string(nombre)
        e.send_enter()
        e.send_string(desc)
        e.send_enter()
    
    e.send_string("3")
    e.send_enter()

def read_line(line, file="pantalla.txt"):
    # Abre el archivo en modo lectura
    with open(file, "r") as archivo:
        lineas = archivo.readlines()  # Lee todas las líneas del archivo

        if 0 <= line < len(lineas):
            linea_deseada = lineas[line]
            return linea_deseada.strip()  # strip() elimina los caracteres de nueva línea
        else:
            return 0

def get_tasks_general():
    resultado = []
    for num_line in range(1, 43 + 1):
        line=read_line(num_line,"pantalla.txt")
        if line!=0:
            if line.find("TOTAL TASK")!=-1:
                return resultado
            else:
                partes = line.split(" ")
                print("PARTES: ",partes)
                temp = {"fecha":partes[3],"descripcion":partes[5]}
                resultado.append(temp)
    return resultado

def get_tasks_specific():
    resultado = []
    for num_line in range(1, 43 + 1):
        line=read_line(num_line,"pantalla.txt")
        print(line)
        if line!=0:
            if line.find("TOTAL TASK")!=-1:
                return resultado
            else:
                partes = line.split(" ")
                temp = {"fecha":partes[4],"nombre":partes[5],"descripcion":partes[6]}
                resultado.append(temp)
    return resultado

# Opción VIEW TASKS
def view_tasks():
    resultado=[]
    e.send_string("2")
    e.send_enter()
    e.send_clear()
    e.send_string("1")
    e.send_enter()
    pantalla()
    print("AQUÍ 1")
    general = get_tasks_general()
    e.send_clear()
    e.send_string("2")
    e.send_enter()
    pantalla()
    print("AQUÍ 2")
    e.send_string("3")
    specific = get_tasks_specific()
    print("AQUÍ 3")
    e.send_enter()
    resultado = general + specific
    print("RESULTADO: ",resultado)
    return resultado

# Opción EXIT TASKS
def exit_tasks():
    global e
    e.send_string("3")
    e.send_enter()
    e.send_string("off")
    e.send_enter()
    time.sleep(0.5)
    e.terminate()
