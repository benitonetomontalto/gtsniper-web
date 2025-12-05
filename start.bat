@echo off
echo.
echo ========================================
echo   GT SNIPER - Multi-Broker System
echo ========================================
echo.

REM Tentar encontrar Python
where python >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Python encontrado
    python main.py
    goto :end
)

where python3 >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Python3 encontrado
    python3 main.py
    goto :end
)

where py >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Py launcher encontrado
    py main.py
    goto :end
)

echo [ERRO] Python nao encontrado!
echo.
echo Por favor instale Python 3.11+ de:
echo https://www.python.org/downloads/
echo.
echo Ou instale via Microsoft Store
pause
goto :end

:end
