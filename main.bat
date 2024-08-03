@echo off

:: Check for python
where python >nul 2>nul
if %errorlevel% == 0 (
    set PYTHON_CMD=python
) else (
    :: Check for python3
    where python3 >nul 2>nul
    if %errorlevel% == 0 (
        set PYTHON_CMD=python3
    ) else (
        :: Check for py
        where py >nul 2>nul
        if %errorlevel% == 0 (
            set PYTHON_CMD=py
        ) else (
            echo No suitable Python installation found.
            pause
            exit /b
        )
    )
)

:: Run the Python script
%PYTHON_CMD% main.py
pause