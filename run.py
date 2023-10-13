from flask import Flask, render_template, request, redirect
from lib.emulator import emulador, assign_tasks, view_tasks, exit_tasks
import os

app = Flask(__name__)

@app.route('/')
def formulario():
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
    return redirect("http://localhost:5000")


# @app.route('/procesar', methods=['POST'])
# def procesar():
#     nombre = request.form['nombre']
#     desc = request.form['desc']
    
#     # Puedes hacer lo que necesites con los datos, como almacenarlos en una base de datos
#     # o realizar algún procesamiento adicional

#     # Aquí, simplemente los imprimimos en la consola
#     print(f'Nombre: {nombre}, Descripción: {desc}')

#     data = [
#         {"nombre": nombre, "desc": desc}
#     ]
    
#     return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
