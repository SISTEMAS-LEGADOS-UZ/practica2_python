@echo off
setlocal

echo Preparando entorno, por favor espere

:: Ruta completa a tu requirements.txt
set REQ_PATH=.\GestorDeTareas

:: Ruta donde se creará el entorno virtual
set VENV_PATH=.\..\env

:: Ruta al pip del entorno virtual
set PIP="%VENV_PATH%\Scripts\pip.exe"


:: Crear el entorno virtual
python -m venv "%VENV_PATH%"

:: Activar el entorno virtual
echo Creando entorno virtual en %VENV_PATH% ...
call "%VENV_PATH%\Scripts\activate.bat"

:: Instalar las dependencias de tu aplicación
echo Instalando dependencias ...
%PIP% install -r "%REQ_PATH%\requirements.txt" > nul 2>&1

:: Ejecutar la aplicación Flask y esperar a que termine
cd GestorDeTareas
echo Lanzando Gestor de tareas (x3270) ...
start /wait python ".\app.py"

:: Eliminar el entorno virtual
echo Eliminando entorno virtual
rmdir /s /q "%VENV_PATH%"

endlocal