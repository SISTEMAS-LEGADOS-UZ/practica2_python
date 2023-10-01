from py3270 import Emulator
import sys, os, time

from pantalla import pantalla_principal

# Funciones
    # Guardar lo que se lee por pantalla en un fichero 
def pantalla(filename="pantalla.txt"):
    screen_content = ''
    for row in range(1, 43 + 1):
        line = e.string_get(row, 1, 79)
        screen_content += line + '\n'
    archivo = open(filename, "w")
    archivo.write(screen_content)
    archivo.close()

    # Buscar un string concreto en un fichero
    # Devuelve la linea en la que se encuentra la cadena. 0 si no la encuentra.
def find_string(string, filename="pantalla.txt"):
    with open(filename, 'r') as file:
        lines = file.readlines()
        for i, line in enumerate(lines, start=1):
            if string in line:
                return i
        return 0

# Main
host = "155.210.152.51"
port = "3270"
mylogin = 'GRUPO_03'
mypass = 'secreto6'
delay=20
delayScreen=0.5
e = Emulator(visible=True)
e.connect(host + ':' + port)

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

# Pantalla principal (tareas)
time.sleep(delayScreen)
pantalla()
line = find_string("1.ASSIGN TASKS  2.VIEW TASKS  3.EXIT")

if line==0:
    print("No en la pantalla principal")
    e.terminate()

boton = pantalla_principal()

if boton==1: # 1.ASSIGN TASKS
    e.wait_for_field()
    e.send_string('1')
    e.send_enter()
elif boton ==2: # 2.VIEW TASKS
    e.wait_for_field()
    e.send_string('2')
    e.send_enter()
elif boton==0: # 3.EXIT
    e.wait_for_field()
    e.send_string('3')
    e.send_enter()

time.sleep(delay)
e.terminate()