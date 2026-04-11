@echo off
setlocal

if not defined PYTHON_MANAGER_DEFAULT set PYTHON_MANAGER_DEFAULT=3.13
py -m nuitka --standalone --output-filename=makebackups.exe main.py
