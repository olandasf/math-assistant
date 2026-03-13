@echo off
chcp 65001 >nul
title Matematikos Mokytojo Asistentas - Sistemos Patikrinimas

echo.
echo ==============================================================
echo        MATEMATIKOS MOKYTOJO ASISTENTAS
echo        Sistemos patikrinimas
echo ==============================================================
echo.

set "ROOT_DIR=%~dp0"
set "BACKEND_DIR=%ROOT_DIR%backend"
set "FRONTEND_DIR=%ROOT_DIR%frontend"
set "ISSUES=0"

:: ═══════════════════════════════════════════════════════════════
:: 1. PRIKLAUSOMYBES
:: ═══════════════════════════════════════════════════════════════

echo [1] Tikrinamos priklausomybes...
echo.

where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [❌] Python nerastas
    set /a ISSUES+=1
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do echo [✅] Python: %%i
)

where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [❌] Node.js nerastas
    set /a ISSUES+=1
) else (
    for /f "tokens=*" %%i in ('node --version 2^>^&1') do echo [✅] Node.js: %%i
)

where npm >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [❌] npm nerastas
    set /a ISSUES+=1
) else (
    for /f "tokens=*" %%i in ('npm --version 2^>^&1') do echo [✅] npm: %%i
)

:: ═══════════════════════════════════════════════════════════════
:: 2. FAILAI IR KATALOGAI
:: ═══════════════════════════════════════════════════════════════

echo.
echo [2] Tikrinami failai ir katalogai...
echo.

if exist "%ROOT_DIR%.env" (
    echo [✅] .env failas rastas
) else (
    echo [❌] .env failas nerastas
    set /a ISSUES+=1
)

if exist "%ROOT_DIR%database" (
    echo [✅] database/ katalogas rastas
) else (
    echo [❌] database/ katalogas nerastas
    set /a ISSUES+=1
)

if exist "%ROOT_DIR%database\math_teacher.db" (
    for %%A in ("%ROOT_DIR%database\math_teacher.db") do set DB_SIZE=%%~zA
    echo [✅] Duomenu baze rasta (%%DB_SIZE%% bytes)
) else (
    echo [⚠️] Duomenu baze nerasta (bus sukurta automatiskai)
)

:: ═══════════════════════════════════════════════════════════════
:: 3. BACKEND
:: ═══════════════════════════════════════════════════════════════

echo.
echo [3] Tikrinamas backend...
echo.

if exist "%BACKEND_DIR%\venv" (
    echo [✅] Backend venv rastas

    :: Tikriname ar yra reikalingi paketai
    cd /d "%BACKEND_DIR%"
    call venv\Scripts\activate.bat 2>nul

    python -c "import fastapi" 2>nul
    if %ERRORLEVEL% neq 0 (
        echo [❌] FastAPI nerastas venv
        set /a ISSUES+=1
    ) else (
        echo [✅] FastAPI idiegtas
    )

    python -c "import sqlalchemy" 2>nul
    if %ERRORLEVEL% neq 0 (
        echo [❌] SQLAlchemy nerastas venv
        set /a ISSUES+=1
    ) else (
        echo [✅] SQLAlchemy idiegtas
    )

    python -c "import google.generativeai" 2>nul
    if %ERRORLEVEL% neq 0 (
        echo [❌] Google Generative AI nerastas venv
        set /a ISSUES+=1
    ) else (
        echo [✅] Google Generative AI idiegtas
    )

    deactivate 2>nul
    cd /d "%ROOT_DIR%"
) else (
    echo [❌] Backend venv nerastas
    set /a ISSUES+=1
)

if exist "%BACKEND_DIR%\main.py" (
    echo [✅] main.py rastas
) else (
    echo [❌] main.py nerastas
    set /a ISSUES+=1
)

if exist "%BACKEND_DIR%\requirements.txt" (
    echo [✅] requirements.txt rastas
) else (
    echo [❌] requirements.txt nerastas
    set /a ISSUES+=1
)

:: ═══════════════════════════════════════════════════════════════
:: 4. FRONTEND
:: ═══════════════════════════════════════════════════════════════

echo.
echo [4] Tikrinamas frontend...
echo.

if exist "%FRONTEND_DIR%\node_modules" (
    echo [✅] node_modules rastas
) else (
    echo [❌] node_modules nerastas
    set /a ISSUES+=1
)

if exist "%FRONTEND_DIR%\package.json" (
    echo [✅] package.json rastas
) else (
    echo [❌] package.json nerastas
    set /a ISSUES+=1
)

if exist "%FRONTEND_DIR%\index.html" (
    echo [✅] index.html rastas
) else (
    echo [❌] index.html nerastas
    set /a ISSUES+=1
)

if exist "%FRONTEND_DIR%\vite.config.ts" (
    echo [✅] vite.config.ts rastas
) else (
    echo [❌] vite.config.ts nerastas
    set /a ISSUES+=1
)

:: ═══════════════════════════════════════════════════════════════
:: 5. PORTAI
:: ═══════════════════════════════════════════════════════════════

echo.
echo [5] Tikrinami portai...
echo.

netstat -an | findstr "127.0.0.1:8000" | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo [⚠️] Port 8000 jau naudojamas (Backend)
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
        echo     PID: %%a
    )
) else (
    echo [✅] Port 8000 laisvas (Backend)
)

netstat -an | findstr "127.0.0.1:5173" | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo [⚠️] Port 5173 jau naudojamas (Frontend)
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5173" ^| findstr "LISTENING"') do (
        echo     PID: %%a
    )
) else (
    echo [✅] Port 5173 laisvas (Frontend)
)

:: ═══════════════════════════════════════════════════════════════
:: 6. KATALOGAI
:: ═══════════════════════════════════════════════════════════════

echo.
echo [6] Tikrinami darbo katalogai...
echo.

if exist "%BACKEND_DIR%\logs" (
    echo [✅] logs/ katalogas rastas
) else (
    echo [⚠️] logs/ katalogas nerastas
)

if exist "%BACKEND_DIR%\uploads" (
    echo [✅] uploads/ katalogas rastas
) else (
    echo [⚠️] uploads/ katalogas nerastas
)

if exist "%BACKEND_DIR%\exports" (
    echo [✅] exports/ katalogas rastas
) else (
    echo [⚠️] exports/ katalogas nerastas
)

:: ═══════════════════════════════════════════════════════════════
:: REZULTATAI
:: ═══════════════════════════════════════════════════════════════

echo.
echo ==============================================================

if "%ISSUES%"=="0" (
    echo   SISTEMA PARUOSTA DARBUI!
    echo ==============================================================
    echo.
    echo   Viskas veikia gerai. Galite paleisti START.bat
    echo.
) else (
    echo   RASTOS PROBLEMOS: %ISSUES%
    echo ==============================================================
    echo.
    echo   Rekomenduojama paleisti SETUP.bat
    echo.
)

echo ==============================================================
echo.
pause
