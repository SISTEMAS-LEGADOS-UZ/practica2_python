from flask import Flask, render_template, request
from lib.emulator import emulador, assign_tasks, view_tasks, exit_tasks
import os
import webview

app = Flask(__name__)
window = webview.create_window('Gestor de tareas (x3270)', app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ini', methods=['POST'])
def ini():
   emulador()
   return render_template('tareas.html')

@app.route('/assignGeneral', methods=['POST'])
def assignGeneral():
    tipo = "General"
    fecha = request.form['fechaGeneral']
    desc = request.form['descripcionGeneral']
    nombre = ""

    print(f'TIPO: {tipo}, FECHA: {fecha}, DESCRIPCION: {desc}, NOMBRE: {nombre}')
    assign_tasks(tipo, fecha, desc, nombre)
    data = view_tasks()
    print(data)
    return render_template('tareas.html', data=data)

@app.route('/assignEspecifica', methods=['POST'])
def assignEspecifica():
    tipo = "Especifica"
    fecha = request.form['fechaEspecifica']
    # fecha = fecha.replace("-", "")
    desc = request.form['descripcionEspecifica']
    nombre = request.form['nombreEspecifica']

    print(f'TIPO: {tipo}, FECHA: {fecha}, DESCRIPCION: {desc}, NOMBRE: {nombre}')
    assign_tasks(tipo, fecha, desc, nombre)
    data = view_tasks()
    # data = []
    print(data)
    return render_template('tareas.html', data=data)

@app.route('/exit', methods=['POST'])
def exit():
    exit_tasks()
    if os.path.exists("pantalla.txt"):
        os.remove("pantalla.txt")
    return render_template('index.html')

if __name__ == '__main__':
    # app.run(debug=True)
    webview.start()
