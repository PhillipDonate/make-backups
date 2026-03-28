@echo off
@setlocal

del /q *-crash-report.xml 2>nul
del /q MakeBackups.zip 2>nul
del /q MakeBackups.exe 2>nul
rmdir /s /q __pycache__ 2>nul
for /d %%d in (*.dist *.build *.onefile-build) do rmdir /s /q "%%d" 2>nul
