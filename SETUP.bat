@echo off
chcp 65001 >nul
title Matematikos Mokytojo Asistentas - Pirminis Nustatymas

echo.
echo ==============================================================
echo        MATEMATIKOS MOKYTOJO ASISTENTAS
echo        Pirminis nustatymas
echo ==============================================================
echo.
echo Sis skriptas padės nustatyti sistema pirma karta.
echo.
pause

set "ROOT_DIR=%~dp0"
set "BACKEND_DIR=%ROOT_DIR%backend"
set "FRONTEND_DIR=%ROOT_DIR%frontend"
set "ERROR_FOUND=0"

:: ═══════════════════════════════════════════════════════════════
:: 1. TIKRINAME PRIKLAUSOMYBES
:: ═══════════════════════════════════════════════════════════════

echo.
echo [1/6] Tikrinamos priklausomybes...
echo.

:: Python
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [❌] Python nerastas!
    echo      Atsisiuskite ir idiekite Python 3.11+
    echo      https://www.python.org/downloads/
    echo.
    set "ERROR_FOUND=1"
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo [✅] Python rastas: %PYTHON_VERSION%
)

:: Node.js
where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [❌] Node.js nerastas!
    echo      Atsisiuskite ir idiekite Node.js 18+
    echo      https://nodejs.org/
    echo.
    set "ERROR_FOUND=1"
) else (
    for /f "tokens=*" %%i in ('node --version 2^>^&1') do set NODE_VERSION=%%i
    echo [✅] Node.js rastas: %NODE_VERSION%
)

:: npm
where npm >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [❌] npm nerastas!
    set "ERROR_FOUND=1"
) else (
    for /f "tokens=*" %%i in ('npm --version 2^>^&1') do set NPM_VERSION=%%i
    echo [✅] npm rastas: %NPM_VERSION%
)

if "%ERROR_FOUND%"=="1" (
    echo.
    echo [KLAIDA] Truksta reikaliniu programu!
    echo          Idiekite jas ir paleiskite SETUP.bat is naujo.
    echo.
    pause
    exit /b 1
)

:: ═══════════════════════════════════════════════════════════════
:: 2. SUKURIAME .ENV FAILA
:: ═══════════════════════════════════════════════════════════════

echo.
echo [2/6] Kuriamas .env failas...
echo.

if exist "%ROOT_DIR%.env" (
    echo [INFO] .env failas jau egzistuoja
    echo        Ar norite ji perrasyti? (Y/N)
    set /p OVERWRITE=
    if /i "%OVERWRITE%"=="Y" (
        copy "%ROOT_DIR%.env.example" "%ROOT_DIR%.env" >nul
        echo [✅] .env failas atnaujintas
    ) else (
        echo [INFO] Paliekamas esamas .env failas
    )
) else (
    if exist "%ROOT_DIR%.env.example" (
        copy "%ROOT_DIR%.env.example" "%ROOT_DIR%.env" >nul
        echo [✅] .env failas sukurtas
    ) else (
        echo [❌] .env.example failas nerastas!
        set "ERROR_FOUND=1"
    )
)

:: ═══════════════════════════════════════════════════════════════
:: 3. SUKURIAME KATALOGUS
:: ═══════════════════════════════════════════════════════════════

echo.
echo [3/6] Kuriami reikalingi katalogai...
echo.

if not exist "%ROOT_DIR%database" mkdir "%ROOT_DIR%database"
if not exist "%BACKEND_DIR%\logs" mkdir "%BACKEND_DIR%\logs"
if not exist "%BACKEND_DIR%\uploads" mkdir "%BACKEND_DIR%\uploads"
if not exist "%BACKEND_DIR%\uploads\original" mkdir "%BACKEND_DIR%\uploads\original"
if not exist "%BACKEND_DIR%\uploads\processed" mkdir "%BACKEND_DIR%\uploads\processed"
if not exist "%BACKEND_DIR%\uploads\pages" mkdir "%BACKEND_DIR%\uploads\pages"
if not exist "%BACKEND_DIR%\exports" mkdir "%BACKEND_DIR%\exports"
if not exist "%BACKEND_DIR%\exports\exams" mkdir "%BACKEND_DIR%\exports\exams"

echo [✅] Visi katalogai sukurti

:: ═══════════════════════════════════════════════════════════════
:: 4. BACKEND SETUP
:: ═══════════════════════════════════════════════════════════════

echo.
echo [4/6] Nustatomas backend...
echo.

cd /d "%BACKEND_DIR%"

:: Sukuriame virtual environment
if not exist "venv" (
    echo [INFO] Kuriamas Python virtual environment...
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo [❌] Nepavyko sukurti venv!
        set "ERROR_FOUND=1"
        goto :skip_backend
    )
    echo [✅] Virtual environment sukurtas
) else (
    echo [INFO] Virtual environment jau egzistuoja
)

:: Aktyvuojame venv ir diegiame priklausomybes
echo [INFO] Diegiamos Python priklausomybes...
echo        (Naudojamas requirements-minimal.txt - be numpy/scipy)
echo        (Tai gali uztrukti keletą minuciu...)
call venv\Scripts\activate.bat
pip install --upgrade pip >nul 2>&1
pip install -r requirements-minimal.txt
if %ERRORLEVEL% neq 0 (
    echo [❌] Nepavyko idiegti priklausomybiu!
    set "ERROR_FOUND=1"
) else (
    echo [✅] Python priklausomybes idiegtos
)
deactivate

:skip_backend
cd /d "%ROOT_DIR%"

:: ═══════════════════════════════════════════════════════════════
:: 5. FRONTEND SETUP
:: ═══════════════════════════════════════════════════════════════

echo.
echo [5/6] Nustatomas frontend...
echo.

cd /d "%FRONTEND_DIR%"

if not exist "node_modules" (
    echo [INFO] Diegiamos Node.js priklausomybes...
    echo        (Tai gali uztrukti keletą minuciu...)
    call npm install
    if %ERRORLEVEL% neq 0 (
        echo [❌] Nepavyko idiegti frontend priklausomybiu!
        set "ERROR_FOUND=1"
    ) else (
        echo [✅] Frontend priklausomybes idiegtos
    )
) else (
    echo [INFO] node_modules jau egzistuoja
    echo        Ar norite atnaujinti priklausomybes? (Y/N)
    set /p UPDATE_NPM=
    if /i "%UPDATE_NPM%"=="Y" (
        echo [INFO] Atnaujinamos priklausomybes...
        call npm install
        echo [✅] Priklausomybes atnaujintos
    )
)

cd /d "%ROOT_DIR%"

:: ═══════════════════════════════════════════════════════════════
:: 6. DUOMENU BAZES INICIALIZACIJA
:: ═══════════════════════════════════════════════════════════════

echo.
echo [6/6] Inicializuojama duomenu baze...
echo.

if not exist "%ROOT_DIR%database\math_teacher.db" (
    echo [INFO] Kuriama duomenu baze...
    cd /d "%BACKEND_DIR%"
    call venv\Scripts\activate.bat

    :: Paleidziame Alembic migracijas
    alembic upgrade head 2>nul
    if %ERRORLEVEL% neq 0 (
        echo [INFO] Alembic migracijos nepavyko, bandoma sukurti DB tiesiogiai...
        python -c "from database import init_db; import asyncio; asyncio.run(init_db())" 2>nul
    )

    deactivate
    cd /d "%ROOT_DIR%"

    if exist "%ROOT_DIR%database\math_teacher.db" (
        echo [✅] Duomenu baze sukurta
    ) else (
        echo [INFO] Duomenu baze bus sukurta pirmo paleidimo metu
    )
) else (
    echo [INFO] Duomenu baze jau egzistuoja
)

:: ═══════════════════════════════════════════════════════════════
:: BAIGTA
:: ═══════════════════════════════════════════════════════════════

echo.
echo ==============================================================

if "%ERROR_FOUND%"=="1" (
    echo   NUSTATYMAS BAIGTAS SU KLAIDOMIS
    echo ==============================================================
    echo.
    echo Kai kurios dalys nepavyko. Patikrinkite klaidas auksciau.
    echo.
) else (
    echo   NUSTATYMAS SEKMINGAI BAIGTAS!
    echo ==============================================================
    echo.
    echo   Kas toliau?
    echo.
    echo   1. Paleiskite START.bat
    echo   2. Atidarykite Nustatymus programoje
    echo   3. Iveskite API raktus:
    echo      - Google Gemini API (BUTINA)
    echo      - WolframAlpha (rekomenduojama)
    echo.
    echo   API raktai:
    echo   - Gemini: https://aistudio.google.com/
    echo   - Wolfram: https://developer.wolframalpha.com/
    echo.
)

echo ==============================================================
echo.
pause
