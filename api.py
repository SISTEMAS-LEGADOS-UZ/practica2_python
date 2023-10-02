from flask import Flask, request, jsonify
from emulator import emulador, assign_tasks, view_tasks, exit_tasks

app = Flask(__name__)

@app.route('/procesar_datos', methods=['POST'])
def procesar_datos():
    print("PROCESANDO")
    datos = request.json
    
    opcion = datos["opcion"]
    if opcion=="ASSIGN":
        assign_tasks(datos["tipo"], datos["fecha"], datos["desc"], datos["nombre"])
        resultados = view_tasks()
    elif opcion=="EXIT":
        exit_tasks()
        resultados = 0
    elif opcion=="EMULADOR":
        Emulador()
        resultados = "Emulador ejecutado con éxito"
        
    return jsonify(resultados)

def Emulador():
    print("emulador")
    emulador()

if __name__ == '__main__':
    app.run(debug=True)