from flask import Flask, request, jsonify
from flask_cors import CORS
from lib.emulator import emulador, assign_tasks, view_tasks, exit_tasks
import os

app = Flask(__name__)
CORS(app)  # Habilita CORS para toda la aplicación


@app.route('/procesar_datos', methods=['POST'])
def procesar_datos():
    print("PROCESANDO")
    datos = request.json

    opcion = datos["opcion"]
    if opcion=="ASSIGN":
        print("ASSIGN")
        assign_tasks(datos["tipo"], datos["fecha"], datos["desc"], datos["nombre"])
        resultados = {"mensaje": view_tasks(), "status":200}
    elif opcion=="EXIT":
        print("EXIT")
        exit_tasks()
        if os.path.exists("pantalla.txt"):
            os.remove("pantalla.txt")
        resultados = {"mensaje":"Salir", "status":200}
    elif opcion=="EMULADOR":
        print("ENMULADOR")
        emulador()
        resultados = {"mensaje":"Emulador lanzado", "status":200}
    else:
        resultados = {"mensaje":"Opción invalida", "status":304}

    return jsonify(resultados)

if __name__ == '__main__':
    app.run(debug=True)