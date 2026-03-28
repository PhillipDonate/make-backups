@echo off
setlocal

py -m nuitka --onefile --windows-console-mode=disable --output-filename=MakeBackups.exe Main.py
