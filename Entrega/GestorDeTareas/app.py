from flask import Flask, render_template, request
from lib.emulator import emulador, assign_tasks, view_tasks, exit_tasks, get_last_all_tasks, dump_screen_debug, refresh_all_tasks,pantalla
import os
import webview
import atexit
import logging

app = Flask(__name__, template_folder='templates')
window = webview.create_window('Gestor de tareas (ws3270)', app, width=1920, height=1080)

# Logging básico a archivo para diagnosticar problemas en producción
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Función que se ejecutará al cerrar la aplicación
def on_application_exit():
    exit_tasks()  # Ejecuta tu función antes de cerrar la aplicación
    if os.path.exists("pantalla.txt"):
        os.remove("pantalla.txt")

# Registra la función on_application_exit para que se ejecute al cerrar la aplicación
atexit.register(on_application_exit)

@app.route('/')
def index():
    return render_template('index_inicio.html')

@app.route('/ini', methods=['POST'])
def ini():
    last_user = request.form['usuario']
    last_passwd = request.form['contrasena']
    logging.info('Intento de login para usuario: %s', last_user)
    try:
        e = emulador(last_user, last_passwd)
       
        
    except Exception:
        logging.exception('Fallo inesperado en emulador')
        return render_template('index_inicio_error.html')

    if e == 0:
        logging.info('Login correcto, mostrando tareas')
        # Tras el login, emulador() ya ha navegado a ALL TASKS y parseado la lista
        
        data = get_last_all_tasks()
        return render_template('tareas.html', data=data)
    elif e == 1:
        logging.warning('Login rechazado o fallo de conexión')
        return render_template('index_inicio_error.html')
    elif e == 2:
        logging.warning('Usuario en uso; render ocupada')
        return render_template('index_inicio_ocupado.html')
    else:
        logging.error('Código de retorno inesperado de emulador: %r', e)
        return render_template('index_inicio_error.html')

@app.route('/assignGeneral', methods=['POST'])
def assignGeneral():
    tipo = "General"
    fecha = request.form['fechaGeneral']
    desc = request.form['descripcionGeneral']
    nombre = ""
    
    # print(f'TIPO: {tipo}, FECHA: {fecha}, DESCRIPCION: {desc}, NOMBRE: {nombre}')
    assign_tasks(tipo, fecha, desc, nombre)
    data = refresh_all_tasks()
    if not data:
        dump_screen_debug("after_assign_general_empty")
    # print(data)
    return render_template('tareas.html', data=data)

@app.route('/assignEspecifica', methods=['POST'])
def assignEspecifica():
    tipo = "Especifica"
    fecha = request.form['fechaEspecifica']
    desc = request.form['descripcionEspecifica']
    nombre = request.form['nombreEspecifica']
    logging.info(f'Asignando tarea especifica: FECHA={fecha}, NOMBRE={nombre}  DESCRIPCION={desc}')
    # print(f'TIPO: {tipo}, FECHA: {fecha}, DESCRIPCION: {desc}, NOMBRE: {nombre}')
    assign_tasks(tipo, fecha, desc, nombre)
    data = refresh_all_tasks()
    if not data:
        dump_screen_debug("after_assign_specific_empty")
    # print(data)
    return render_template('tareas.html', data=data)

@app.route('/exit', methods=['POST'])
def exit():
    exit_tasks()
    if os.path.exists("pantalla.txt"):
        os.remove("pantalla.txt")
    return render_template('index_inicio.html')

@app.route('/refresh', methods=['POST'])
def refresh():
    try:
       
        data = refresh_all_tasks()
        if not data:
            dump_screen_debug("after_refresh_empty")
        return render_template('tareas.html', data=data)
    except Exception:
        logging.exception('Fallo inesperado en refresh')
        return render_template('tareas.html', data=get_last_all_tasks())

if __name__ == '__main__':
    webview.start()
