from py3270 import Emulator
from flask import Flask, request, jsonify
import sys, os, time

e = Emulator(visible=True)
app = Flask(__name__)

@app.route('/', methods=['POST'])
def procesar_datos():
    datos = request.json
    
    opcion = datos["opcion"]
    if opcion=="ASSIGN":
        assign_tasks(datos)
        resultados = view_tasks()
    elif opcion=="EXIT":
        exit_tasks()
        resultados = 0

    return jsonify(resultados)

# Guardar lo que se lee por pantalla en un fichero 
def pantalla(filename="pantalla.txt"):
    time.sleep(0.5)
    screen_content = ''
    for row in range(1, 43 + 1):
        line = e.string_get(row, 1, 79)
        screen_content += line + '\n'
    archivo = open(filename, "w")
    archivo.write(screen_content)
    archivo.close()

def read_line(line, file="pantalla.txt"):
    # Abre el archivo en modo lectura
    with open(file, "r") as archivo:
        lineas = archivo.readlines()  # Lee todas las líneas del archivo

        if 0 <= line < len(lineas):
            linea_deseada = lineas[line]
            return linea_deseada.strip()  # strip() elimina los caracteres de nueva línea
        else:
            return 0

def get_tasks_general():
    resultado = []
    for num_line in range(1, 43 + 1):
        line=read_line(num_line,"./sl-pr-2/pantalla.txt")
        print(line)
        if line!=0:
            if line.find("TOTAL TASK")!=-1:
                return resultado
            else:
                partes = line.split(" ")
                temp = {"fecha":partes[4],"descripcion":partes[6]}
                resultado.append(temp)

def get_tasks_specific():
    resultado = []
    for num_line in range(1, 43 + 1):
        line=read_line(num_line,"./sl-pr-2/pantalla.txt")
        print(line)
        if line!=0:
            if line.find("TOTAL TASK")!=-1:
                return resultado
            else:
                partes = line.split(" ")
                temp = {"fecha":partes[4],"nombre":partes[5],"descripcion":partes[6]}
                resultado.append(temp)

# Opción ASSIGN TASKS
def assign_tasks(datos):
    e.send_string("1")
    e.send_enter()

    if datos["Tipo"]=="General":
        e.send_string("1")
        e.send_enter()
        e.send_string(datos["fecha"])
        e.send_enter()
        e.send_string(datos["descripcion"])
        e.send_enter()

    elif datos["Tipo"]=="Especifico":
        e.send_string("2")
        e.send_enter()
        e.send_string(datos["nombre"])
        e.send_enter()
        e.send_string(datos["descripcion"])
        e.send_enter()
    
    e.send_string("3")
    e.send_enter()

# Opción VIEW TASKS
def view_tasks():
    resultado=[]
    e.send_string("2")
    e.send_enter()
    e.exec_command(b"Clear")
    e.send_string("1")
    e.send_enter()
    pantalla()
    resultado = resultado.append(get_tasks_general())
    e.exec_command(b"Clear")
    e.send_string("2")
    e.send_enter()
    pantalla()
    resultado = resultado.append(get_tasks_specific())
    return resultado


# Opción EXIT TASKS
def exit_tasks():
    e.send_string("3")
    e.send_enter()

if __name__ == '__main__':
    app.run()
