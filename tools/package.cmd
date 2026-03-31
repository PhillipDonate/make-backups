@echo off
setlocal

REM https://www.microsoft.com/en-us/wdsi/filesubmission

set Files=makebackups.exe example_config_full.py example_config_simple.py LICENSE README.md ok.wav error.wav
set ArchiveName=makebackups.zip

del /q %ArchiveName% 2>nul
tar -caf %ArchiveName% %Files%

echo Done!
