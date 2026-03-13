@echo off
chcp 65001 >nul
title Sustabdyti Matematikos Mokytojo Asistenta

echo.
echo ==============================================================
echo        SUSTABDOMAS MATEMATIKOS MOKYTOJO ASISTENTAS
echo ==============================================================
echo.

set "ROOT_DIR=%~dp0"
set "STOPPED_COUNT=0"

echo [INFO] Ieskoma veikianciu procesu...
echo.

set "BACKEND_FOUND=0"
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING" 2^>nul') do (
    echo [INFO] Stabdomas backend serveris (PID: %%a)
    taskkill /F /PID %%a >nul 2>&1
    if not errorlevel 1 (
        set "BACKEND_FOUND=1"
        set /a STOPPED_COUNT+=1
    )
)

if "%BACKEND_FOUND%"=="0" (
    echo [INFO] Backend serveris neveikia
)

set "FRONTEND_FOUND=0"
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5173" ^| findstr "LISTENING" 2^>nul') do (
    echo [INFO] Stabdomas frontend serveris (PID: %%a)
    taskkill /F /PID %%a >nul 2>&1
    if not errorlevel 1 (
        set "FRONTEND_FOUND=1"
        set /a STOPPED_COUNT+=1
    )
)

if "%FRONTEND_FOUND%"=="0" (
    echo [INFO] Frontend serveris neveikia
)

for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FO LIST ^| findstr "PID:" 2^>nul') do (
    netstat -ano | findstr "%%a" | findstr ":8000" >nul 2>&1
    if not errorlevel 1 (
        echo [INFO] Stabdomas Python procesas (PID: %%a)
        taskkill /F /PID %%a >nul 2>&1
    )
)

for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq node.exe" /FO LIST ^| findstr "PID:" 2^>nul') do (
    netstat -ano | findstr "%%a" | findstr ":5173" >nul 2>&1
    if not errorlevel 1 (
        echo [INFO] Stabdomas Node.js procesas (PID: %%a)
        taskkill /F /PID %%a >nul 2>&1
    )
)

taskkill /FI "WINDOWTITLE eq Backend Server*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Frontend Server*" /F >nul 2>&1

if exist "%ROOT_DIR%_run_backend.bat" (
    del "%ROOT_DIR%_run_backend.bat" >nul 2>&1
    echo [INFO] Istrintas _run_backend.bat
)

if exist "%ROOT_DIR%_run_frontend.bat" (
    del "%ROOT_DIR%_run_frontend.bat" >nul 2>&1
    echo [INFO] Istrintas _run_frontend.bat
)

timeout /t 2 /nobreak >nul

echo.
echo ==============================================================
if "%STOPPED_COUNT%"=="0" (
    echo   Jokie procesai neveike
) else (
    echo   Sustabdyta procesu: %STOPPED_COUNT%
)
echo ==============================================================
echo.
echo Spauskite bet kuri klavisa, kad uzdarytumete...
pause >nul