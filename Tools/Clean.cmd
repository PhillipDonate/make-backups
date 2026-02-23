@echo off
@setlocal

del /q *-crash-report.xml 2>nul
del /q MakeBackups.zip 2>nul
del /q MakeBackups.exe 2>nul
rmdir /s /q MakeBackups.build 2>nul
rmdir /s /q MakeBackups.dist 2>nul
rmdir /s /q MakeBackups.onefile-build 2>nul
rmdir /s /q __pycache__ 2>nul
