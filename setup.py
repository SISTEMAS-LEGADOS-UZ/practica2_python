import sys
from cx_Freeze import setup, Executable

# Reemplaza 'app.py' con el nombre de tu archivo principal
main_script = 'app.py'

# Opciones de configuración para cx_Freeze
build_exe_options = {
    'packages': ['flask'],
    'include_files': ['templates', 'lib'],  # Añade aquí cualquier directorio o archivo adicional que necesites
}

# Define el ejecutable
exe = Executable(
    script=main_script,
    base=None,
    icon='icon.png',  # Ruta al icono de la aplicación (opcional)
)

# Configuración de la aplicación
setup(
    name='GestorTareas',
    version='1.0',
    description='Descripción de tu aplicación',
    options={'build_exe': build_exe_options},
    executables=[exe],
)
