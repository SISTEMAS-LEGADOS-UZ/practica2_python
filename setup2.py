from distutils.core import setup
import py2exe

setup(
    console=[
        {
            "script": "app.py",  # Reemplaza con el nombre de tu archivo principal
        }
    ],
    options={
        "py2exe": {
            "includes": ["flask", "webview", "lib.py3270"],  # Lista de módulos que necesitas incluir
        }
    },
)
