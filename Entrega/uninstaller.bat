@echo off
setlocal

:: Ruta donde se creará el entorno virtual
set VENV_PATH=.\env

:: Eliminar el entorno virtual
echo Eliminando entorno virtual...
rmdir /s /q "%VENV_PATH%"
echo Eliminado

pause
endlocal