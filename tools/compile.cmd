@echo off
setlocal

py -m nuitka --standalone --output-filename=makebackups.exe main.py
