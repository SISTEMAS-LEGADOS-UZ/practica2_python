from py3270 import Emulator
import sys, os, time

host = "155.210.152.51"
port = "3270"
mylogin = 'GRUPO_03'
mypass = 'secreto6'
delay=10
delayScreen=2
e = Emulator(visible=True)
e.connect(host + ':' + port)

# Patalla inicio
time.sleep(delayScreen)
e.send_enter()

# Pantalla Login
time.sleep(delayScreen)
# Usuario
e.wait_for_field()
e.send_string(mylogin)
e.send_enter()

# Contraseña
e.wait_for_field()
e.send_string(mypass)
e.send_enter()

# Pantalla previa a comandos
time.sleep(delayScreen)
e.send_enter()
time.sleep(delayScreen)
e.wait_for_field()
cmd = 'PA1'
e.send_string(cmd)
e.send_enter()

# Pantalla comandos
# time.sleep(delayScreen)
# e.wait_for_field()
# e.send_string('tareas.c')

time.sleep(delay)
e.terminate()