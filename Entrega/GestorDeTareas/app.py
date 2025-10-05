"""
Aplicación Flask para gestionar tareas con integración TN3270.

Este módulo define la app de Flask, sus rutas y la lógica de arranque
en modo ventana embebida (pywebview) o, en su defecto, servidor local
con apertura del navegador. Se han añadido docstrings, utilidades y
una estructura más clara sin alterar el comportamiento original.
"""

from __future__ import annotations

import atexit
import logging
import os
import webbrowser
from typing import Any, List

from flask import Flask, render_template, request
from lib.emulator import (
    assign_tasks,
    dump_screen_debug,
    emulador,
    exit_tasks,
    get_last_all_tasks,
    refresh_all_tasks,
    view_tasks,  # noqa: F401 (se importa por API pública, aunque no se use aquí)
    pantalla,    # noqa: F401 (se mantiene por compatibilidad)
)

# Parámetros de ejecución
HOST = "127.0.0.1"
PORT = 5000
WINDOW_TITLE = "Gestor de tareas (ws3270)"

# Carga opcional de pywebview
try:  # pragma: no cover - dependiente del entorno
    import webview  # type: ignore
    _WEBVIEW_AVAILABLE = True
except Exception:  # pragma: no cover
    webview = None  # type: ignore
    _WEBVIEW_AVAILABLE = False


def _configure_logging() -> None:
    """Configura logging a fichero más salida a consola (INFO por defecto)."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.FileHandler("app.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def _remove_file(path: str) -> None:
    """Elimina un archivo si existe, ignorando errores."""
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        logging.getLogger(__name__).debug("No se pudo eliminar %s", path)


app = Flask(__name__, template_folder="templates", static_folder="static")
_configure_logging()


def _on_application_exit() -> None:
    """Acciones de limpieza al cerrar la aplicación."""
    # Mantener la semántica original: intentar cerrar sesión TN3270
    exit_tasks()
    # Retirar artefacto temporal si aparece
    _remove_file("pantalla.txt")


# Registrar la limpieza al final de la ejecución del proceso
atexit.register(_on_application_exit)

@app.route('/')
def index():
    """Pantalla de inicio (formulario de login)."""
    return render_template("index_inicio.html")

@app.route('/ini', methods=['POST'])
def ini():
    """Procesa el login e inicia el flujo principal en el host TN3270.

    Respuesta de `emulador`:
      0 -> login OK, mostrar tareas
      1 -> credenciales/permiso/conexión incorrectos
      2 -> usuario ya en uso
     -1 -> otro error
    """
    username = request.form["usuario"]
    password = request.form["contrasena"]
    logging.info("Intento de login para usuario: %s", username)

    try:
        result = emulador(username, password)
    except Exception:
        logging.exception("Fallo inesperado en emulador")
        return render_template("index_inicio_error.html")

    if result == 0:
        logging.info("Login correcto, mostrando tareas")
        # Tras el login, emulador() ya ha navegado a ALL TASKS y parseado la lista
        data = get_last_all_tasks()
        return render_template("tareas.html", data=data)
    elif result == 1:
        logging.warning("Login rechazado o fallo de conexión")
        return render_template("index_inicio_error.html")
    elif result == 2:
        logging.warning("Usuario en uso; render ocupada")
        return render_template("index_inicio_ocupado.html")
    else:
        logging.error("Código de retorno inesperado de emulador: %r", result)
        return render_template("index_inicio_error.html")

@app.route('/assignGeneral', methods=['POST'])
def assignGeneral():
    """Asigna una tarea general y vuelve al listado actualizado."""
    tipo = "General"
    fecha = request.form["fechaGeneral"]
    desc = request.form["descripcionGeneral"]
    # Aunque la UI no pide nombre para generales, permitimos recibirlo opcionalmente
    nombre = request.form.get("nombreGeneral", "")

    assign_tasks(tipo, fecha, desc, nombre)
    data = refresh_all_tasks()
    if not data:
        dump_screen_debug("after_assign_general_empty")
    return render_template("tareas.html", data=data)

@app.route('/assignEspecifica', methods=['POST'])
def assignEspecifica():
    """Asigna una tarea específica y vuelve al listado actualizado."""
    tipo = "Especifica"
    fecha = request.form["fechaEspecifica"]
    desc = request.form["descripcionEspecifica"]
    nombre = request.form["nombreEspecifica"]
    logging.info(
        "Asignando tarea especifica: FECHA=%s, NOMBRE=%s  DESCRIPCION=%s",
        fecha,
        nombre,
        desc,
    )
    assign_tasks(tipo, fecha, desc, nombre)
    data = refresh_all_tasks()
    if not data:
        dump_screen_debug("after_assign_specific_empty")
    return render_template("tareas.html", data=data)

@app.route('/exit', methods=['POST'])
def exit():
    """Finaliza la sesión TN3270 y vuelve al inicio."""
    exit_tasks()
    _remove_file("pantalla.txt")
    return render_template("index_inicio.html")

@app.route('/refresh', methods=['POST'])
def refresh():
    """Refresca el listado de tareas (ALL TASKS) y lo muestra en pantalla."""
    try:
        data = refresh_all_tasks()
        if not data:
            dump_screen_debug("after_refresh_empty")
        return render_template("tareas.html", data=data)
    except Exception:
        logging.exception("Fallo inesperado en refresh")
        return render_template("tareas.html", data=get_last_all_tasks())

if __name__ == "__main__":
    # Mantener el mismo orden y semántica que la versión original
    if _WEBVIEW_AVAILABLE:
        try:
            window = webview.create_window(WINDOW_TITLE, app, width=1920, height=1080)  # type: ignore
            webview.start()  # type: ignore
        except Exception:
            logging.exception("Fallo al iniciar pywebview; usando navegador por defecto")
            app.run(host=HOST, port=PORT, debug=False, threaded=True)
            try:
                webbrowser.open(f"http://{HOST}:{PORT}")
            except Exception:
                pass
    else:
        logging.info("pywebview no disponible; iniciando servidor Flask y abriendo navegador")
        try:
            webbrowser.open(f"http://{HOST}:{PORT}")
        except Exception:
            pass
        app.run(host=HOST, port=PORT, debug=False, threaded=True)
