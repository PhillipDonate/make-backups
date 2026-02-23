@echo off
setlocal

set Files=MakeBackups.exe 7za.exe Config.py
set ArchiveName=MakeBackups.zip
set zip=7za.exe

if not exist "%zip%" (
    echo %zip% not found
    goto :Error
)

del /q %ArchiveName% 2>nul
%zip% a %ArchiveName% %Files%

:Error
exit /b 1
