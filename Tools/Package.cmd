@echo off
setlocal

set Files=MakeBackups.exe ExampleConfig.py ok.wav error.wav
set ArchiveName=MakeBackups.zip
set zip=tar

del /q %ArchiveName% 2>nul
%zip% -cf %ArchiveName% %Files%

:Error
exit /b 1
