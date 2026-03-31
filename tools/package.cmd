@echo off
setlocal

set Files=main.dist\*,example_config_full.py,example_config_simple.py,LICENSE,README.md,ok.wav,error.wav

set ArchiveName=makebackups.zip
del /q %ArchiveName% 2>nul

powershell Compress-Archive -Path %Files% -DestinationPath %ArchiveName%
echo Done!
