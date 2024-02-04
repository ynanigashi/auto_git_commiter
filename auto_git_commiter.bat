@echo off
cd /d %~dp0
python .\main.py
IF %ERRORLEVEL% EQU -1 (
    goto :EOF
)
pause

:EOF