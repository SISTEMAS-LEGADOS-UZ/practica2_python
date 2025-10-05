@echo off
setlocal ENABLEDELAYEDEXPANSION

:: Lanzador portable: descarga Python embebido, instala pip y dependencias localmente, y ejecuta la app
set ROOT_DIR=%~dp0
pushd "%ROOT_DIR%"

set PY_DIR=%ROOT_DIR%python-embed
set PY_EXE=%PY_DIR%\python.exe
set REQ_PATH=%ROOT_DIR%GestorDeTareas
set PIP_EXE=%PY_DIR%\Scripts\pip.exe
set GETPIP=%PY_DIR%\get-pip.py

:: Detectar arquitectura (x64/x86)
set ARCH=x64
if "%PROCESSOR_ARCHITECTURE%"=="x86" (
    set ARCH=x86
)
if defined PROCESSOR_ARCHITEW6432 (
    set ARCH=x64
)

echo Preparando entorno portable, por favor espere...

:: Crear carpeta destino
if not exist "%PY_DIR%" mkdir "%PY_DIR%"

:: Descargar Python embebido si no existe
if not exist "%PY_EXE%" (
    echo Descargando Python embebido...
    set PY_URL=https://www.python.org/ftp/python/3.12.6/python-3.12.6-embed-amd64.zip
    if "%ARCH%"=="x86" set PY_URL=https://www.python.org/ftp/python/3.12.6/python-3.12.6-embed-win32.zip
    powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Invoke-WebRequest -UseBasicParsing -Uri '!PY_URL!' -OutFile '!PY_DIR!\python-embed.zip' } catch { Write-Error $_; exit 1 }" || goto :error
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Add-Type -AssemblyName System.IO.Compression.FileSystem; [IO.Compression.ZipFile]::ExtractToDirectory('!PY_DIR!\python-embed.zip','!PY_DIR!')" || goto :error
        del /q "!PY_DIR!\python-embed.zip" >nul 2>&1
)

    :: Habilitar 'import site' y asegurar '.' en sys.path para Python embebido
    if exist "%PY_DIR%\python312._pth" (
        powershell -NoProfile -ExecutionPolicy Bypass -Command "(Get-Content -Raw '%PY_DIR%\python312._pth') -replace '#import site','import site' | Set-Content -NoNewline '%PY_DIR%\python312._pth'" || goto :error
        powershell -NoProfile -ExecutionPolicy Bypass -Command "$c=Get-Content -Raw '%PY_DIR%\python312._pth'; if($c -notmatch '(?m)^\.$'){ Add-Content -Path '%PY_DIR%\python312._pth' -Value '.' }" || goto :error
        powershell -NoProfile -ExecutionPolicy Bypass -Command "$c=Get-Content -Raw '%PY_DIR%\python312._pth'; if($c -notmatch '(?m)^Lib$'){ Add-Content -Path '%PY_DIR%\python312._pth' -Value 'Lib' }" || goto :error
        powershell -NoProfile -ExecutionPolicy Bypass -Command "$c=Get-Content -Raw '%PY_DIR%\python312._pth'; if($c -notmatch '(?m)^Lib\\site-packages$'){ Add-Content -Path '%PY_DIR%\python312._pth' -Value 'Lib\\site-packages' }" || goto :error
        powershell -NoProfile -ExecutionPolicy Bypass -Command "$c=Get-Content -Raw '%PY_DIR%\python312._pth'; if($c -notmatch [regex]::Escape('%REQ_PATH%')){ Add-Content -Path '%PY_DIR%\python312._pth' -Value '%REQ_PATH%' }" || goto :error
    )

:: Instalar/Actualizar pip (forzar reinstalación para evitar inconsistencias)
echo Instalando/actualizando pip...
    if not exist "%GETPIP%" (
        powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Invoke-WebRequest -UseBasicParsing -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%GETPIP%' } catch { Write-Error $_; exit 1 }" || goto :error
    )
    "%PY_EXE%" "%GETPIP%" --no-warn-script-location --upgrade || goto :error

:: Asegurar que Scripts existe y pip está disponible
if not exist "%PY_DIR%\Scripts" mkdir "%PY_DIR%\Scripts" >nul 2>&1

:: Instalar herramientas de build y dependencias
echo Preparando pip/setuptools/wheel...
"%PY_EXE%" -m pip install --no-warn-script-location --upgrade pip setuptools wheel || (
    echo Fallback: reinstalando pip con get-pip.py...
    "%PY_EXE%" "%GETPIP%" --no-warn-script-location --upgrade || goto :error
    "%PY_EXE%" -m pip install --no-warn-script-location --upgrade pip setuptools wheel || goto :error
)
echo Instalando dependencias de requirements.txt...
"%PY_EXE%" -m pip install --no-warn-script-location -r "%REQ_PATH%\requirements.txt" || goto :error

:: Establecer PATH para que ws3270.exe sea encontrado (ya está junto a GestorDeTareas)
set PATH=%ROOT_DIR%GestorDeTareas;%PY_DIR%;%PY_DIR%\Scripts;%PATH%
set PYTHONPATH=%REQ_PATH%;%PYTHONPATH%

:: Ejecutar la aplicación en nueva ventana con logs en vivo
echo Iniciando Gestor de tareas (ws3270)...
start "Gestor de Tareas (logs)" /D "%REQ_PATH%" cmd /k ""%PY_EXE%" app.py"
echo Ventana de la aplicacion lanzada. Puede cerrar esta consola.
popd
endlocal
exit /b 0

:error
echo.
echo Ocurrio un error durante la preparacion o la ejecucion.
echo Revise app.log si existe, y la salida anterior para detalles.
popd
endlocal
exit /b 1