from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins="http://localhost:8080")  # Permite solo solicitudes desde http://localhost:8080

@app.route('/mi_ruta_api')
def mi_funcion_api():
    # Tu lógica para procesar la solicitud de la API aquí
    data = {"mensaje": "¡Solicitud API exitosa!"}
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
