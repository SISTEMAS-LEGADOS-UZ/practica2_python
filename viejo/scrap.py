# Importa el módulo wc3270 para acceder a las funciones específicas de x3270
import wc3270 as wc

# Crea una instancia de la sesión de x3270
session = wc.Session()

# Conecta al sistema 3270 especificando la dirección IP y el puerto
session.connect('155.210.152.51:3270')

# Esperar a que aparezca el prompt de inicio de sesión
# session.wait('Login:')

# Enviar el nombre de usuario
# session.string('tu_usuario')

# Enviar una nueva línea (intro)
# session.enter()

# Esperar a que aparezca el prompt de contraseña
#session.wait('Password:')

# Enviar la contraseña
#session.string('tu_contraseña')

# Enviar una nueva línea (intro)
#session.enter()

# Esperar a que se cargue la pantalla principal del sistema
#session.wait('Main Menu:')

# Enviar un comando y esperar su resultado
#session.string('comando1')
#session.enter()

# Capturar la salida del comando
output = session.wait_for_text('Tendria que ser el login', timeout=10)  # Cambia "Texto_de_salida_del_comando1" al texto que esperas como salida

print("OUTPUT:", output)
# Realizar más interacciones si es necesario

# Cerrar la sesión
session.disconnect()
