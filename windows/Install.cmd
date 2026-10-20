@echo off
chcp 65001 >nul
set PYTHONUTF8=1
"%~dp0runtime\python.exe" "%~dp0app\install.py"
pause
