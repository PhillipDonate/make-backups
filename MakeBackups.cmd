@echo off

set destination="%USERPROFILE%\Desktop"

call BackupFolder.cmd "%USERPROFILE%\OneDrive\Documents" %destination%
if errorlevel 1 goto :Error
call BackupFolder.cmd "%USERPROFILE%\Local Files\Passwords.xlxs" %destination%
if errorlevel 1 goto :Error

:Success
echo.
echo Press any key or wait 10 seconds...
timeout /t 10 >nul
exit /b 0

:Error
echo.
pause
exit /b 1
