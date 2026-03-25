@echo off
chcp 65001 >nul
title Matematikos Mokytojo Asistentas - Paleidimas

echo.
echo ==============================================================
echo        MATEMATIKOS MOKYTOJO ASISTENTAS
echo        Paleidziama sistema...
echo ==============================================================
echo.

set "ROOT_DIR=%~dp0"
set "BACKEND_DIR=%ROOT_DIR%backend"
set "FRONTEND_DIR=%ROOT_DIR%frontend"
set "ERROR_FOUND=0"

echo [1/7] Tikrinamos priklausomybes...

where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [KLAIDA] Python nerastas! Idiekite Python 3.11+
    echo          Atsisiuskite: https://www.python.org/downloads/
    set "ERROR_FOUND=1"
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo [OK] Python rastas: %PYTHON_VERSION%
)

where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [KLAIDA] Node.js nerastas! Idiekite Node.js 18+
    echo          Atsisiuskite: https://nodejs.org/
    set "ERROR_FOUND=1"
) else (
    for /f "tokens=*" %%i in ('node --version 2^>^&1') do set NODE_VERSION=%%i
    echo [OK] Node.js rastas: %NODE_VERSION%
)

where npm >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [KLAIDA] npm nerastas! Idiekite Node.js su npm
    set "ERROR_FOUND=1"
) else (
    echo [OK] npm rastas
)

if "%ERROR_FOUND%"=="1" (
    echo.
    echo [KLAIDA] Truksta reikaliniu programu! Idiekite jas ir bandykite vel.
    pause
    exit /b 1
)

echo.
echo [2/7] Tikrinami failai ir katalogai...

if not exist "%ROOT_DIR%.env" (
    echo [ISPEJIMAS] .env failas nerastas! Kopijuojamas is .env.example...
    if exist "%ROOT_DIR%.env.example" (
        copy "%ROOT_DIR%.env.example" "%ROOT_DIR%.env" >nul
        echo [OK] .env failas sukurtas. Nepamirskite nustatyti API raktus!
    ) else (
        echo [KLAIDA] .env.example failas nerastas!
        set "ERROR_FOUND=1"
    )
) else (
    echo [OK] .env failas rastas
)

if not exist "%BACKEND_DIR%\venv" (
    echo [ISPEJIMAS] Backend venv nerastas! Paleiskite SETUP.bat
    set "ERROR_FOUND=1"
) else (
    echo [OK] Backend venv rastas
)

if not exist "%FRONTEND_DIR%\node_modules" (
    echo [ISPEJIMAS] Frontend node_modules nerastas! Paleiskite SETUP.bat
    set "ERROR_FOUND=1"
) else (
    echo [OK] Frontend node_modules rastas
)

if not exist "%ROOT_DIR%database" mkdir "%ROOT_DIR%database"
if not exist "%BACKEND_DIR%\logs" mkdir "%BACKEND_DIR%\logs"
if not exist "%BACKEND_DIR%\uploads" mkdir "%BACKEND_DIR%\uploads"
if not exist "%BACKEND_DIR%\uploads\original" mkdir "%BACKEND_DIR%\uploads\original"
if not exist "%BACKEND_DIR%\uploads\processed" mkdir "%BACKEND_DIR%\uploads\processed"
if not exist "%BACKEND_DIR%\uploads\pages" mkdir "%BACKEND_DIR%\uploads\pages"
if not exist "%BACKEND_DIR%\exports" mkdir "%BACKEND_DIR%\exports"
if not exist "%BACKEND_DIR%\exports\exams" mkdir "%BACKEND_DIR%\exports\exams"
echo [OK] Visi reikalingi katalogai sukurti

if "%ERROR_FOUND%"=="1" (
    echo.
    echo [KLAIDA] Rastos problemos! Paleiskite SETUP.bat pirma.
    pause
    exit /b 1
)

echo.
echo [3/7] Stabdomi seni procesai...

for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING" 2^>nul') do (
    echo [INFO] Stabdomas backend (PID: %%a)
    taskkill /F /PID %%a >nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000" ^| findstr "LISTENING" 2^>nul') do (
    echo [INFO] Stabdomas frontend (PID: %%a)
    taskkill /F /PID %%a >nul 2>&1
)

timeout /t 2 /nobreak >nul
echo [OK] Seni procesai sustabdyti

echo.
echo [4/7] Tikrinama duomenu baze...

if not exist "%ROOT_DIR%database\math_teacher.db" (
    echo [INFO] Duomenu baze nerasta. Bus sukurta automatiskai...
) else (
    echo [OK] Duomenu baze rasta
)

echo.
echo [5/7] Paleidziamas backend serveris...

echo @echo off > "%ROOT_DIR%_run_backend.bat"
echo chcp 65001 ^>nul >> "%ROOT_DIR%_run_backend.bat"
echo title Backend Server - Port 8000 >> "%ROOT_DIR%_run_backend.bat"
echo cd /d "%BACKEND_DIR%" >> "%ROOT_DIR%_run_backend.bat"
echo call venv\Scripts\activate.bat >> "%ROOT_DIR%_run_backend.bat"
echo python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload >> "%ROOT_DIR%_run_backend.bat"

start "Backend Server" "%ROOT_DIR%_run_backend.bat"

echo [INFO] Laukiama kol backend pasileis...
set "BACKEND_READY=0"
for /L %%i in (1,1,30) do (
    timeout /t 1 /nobreak >nul
    netstat -an | findstr "127.0.0.1:8000" | findstr "LISTENING" >nul 2>&1
    if not errorlevel 1 (
        set "BACKEND_READY=1"
        goto :backend_ready
    )
)

:backend_ready
if "%BACKEND_READY%"=="1" (
    echo [OK] Backend serveris paleistas!
) else (
    echo [ISPEJIMAS] Backend galbut dar nepasileid?. Tikrinkite Backend Server langa.
)

echo.
echo [6/7] Paleidziamas frontend serveris...

echo @echo off > "%ROOT_DIR%_run_frontend.bat"
echo chcp 65001 ^>nul >> "%ROOT_DIR%_run_frontend.bat"
echo title Frontend Server - Port 3000 >> "%ROOT_DIR%_run_frontend.bat"
echo cd /d "%FRONTEND_DIR%" >> "%ROOT_DIR%_run_frontend.bat"
echo npm run dev >> "%ROOT_DIR%_run_frontend.bat"

start "Frontend Server" "%ROOT_DIR%_run_frontend.bat"

echo [INFO] Laukiama kol frontend pasileis...
set "FRONTEND_READY=0"
for /L %%i in (1,1,20) do (
    timeout /t 1 /nobreak >nul
    netstat -an | findstr "0.0.0.0:3000" | findstr "LISTENING" >nul 2>&1
    if not errorlevel 1 (
        set "FRONTEND_READY=1"
        goto :frontend_ready
    )
)

:frontend_ready
if "%FRONTEND_READY%"=="1" (
    echo [OK] Frontend serveris paleistas!
) else (
    echo [ISPEJIMAS] Frontend galbut dar nepasileid?. Tikrinkite Frontend Server langa.
)

echo.
echo [7/7] Sistema paleista!
echo.
echo ==============================================================
echo   SISTEMA SEKMINGAI PALEISTA!
echo ==============================================================
echo.
echo   Frontend:  http://localhost:3000
echo   Backend:   http://localhost:8000
echo   API Docs:  http://localhost:8000/docs
echo.
echo   SVARBU:
echo   - Nepamirskite nustatyti API raktus (Nustatymai)
echo   - Uzdarykite Backend/Frontend langus noredami sustabdyti
echo   - Arba paleiskite STOP.bat
echo.
echo ==============================================================
echo.

timeout /t 3 /nobreak >nul
start "" "http://localhost:3000"

echo Spauskite bet kuri klavisa, kad uzdarytumete si langa...
echo (Backend ir Frontend liks veikti fone)
pause >nul