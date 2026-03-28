@echo off
setlocal

REM https://www.microsoft.com/en-us/wdsi/filesubmission

set Files=MakeBackups.exe ExampleConfig.py ok.wav error.wav
set ArchiveName=MakeBackups.zip
set zip=tar

del /q %ArchiveName% 2>nul
%zip% -cf %ArchiveName% %Files%

echo Done!
