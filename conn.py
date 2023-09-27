import subprocess

# Ruta al ejecutable de x3270 (puede variar según la ubicación de la instalación)
ruta_x3270 = "C:\WINDOWS\system32\conhost.exe"  # Reemplaza con la ruta correcta

# Comando para ejecutar x3270 con la configuración deseada
comando_x3270 = [ruta_x3270, "-script", "scrap.py"]

# # Ejecuta el emulador x3270
# try:
#     subprocess.run(comando_x3270, check=True)
# except subprocess.CalledProcessError as e:
#     print("Error al ejecutar x3270:", e)


try:
    # Ejecuta el emulador x3270 y captura la salida
    proceso = subprocess.Popen(comando_x3270, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    salida, errores = proceso.communicate()

    # Verifica si hubo errores en la ejecución
    if proceso.returncode != 0:
        print("Error al ejecutar x3270. Errores:")
        print(errores)
    else:
        print("Salida del emulador x3270:")
        print(salida)
except Exception as e:
    print("Error al ejecutar x3270:", str(e))