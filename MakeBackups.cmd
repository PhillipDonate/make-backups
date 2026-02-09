@echo off

set zipper=%~dp0\7za.exe
set destination=E:\Backups_NameHere
set staging=%TEMP%\Backups_NameHere

if not exist %destination% (
    echo Could not find backups folder.  Connect the USB drive and try again.
    goto :Error
)

mkdir "%staging%" 2>nul
if errorlevel 1 (
    echo Could not create temporary staging folder.
    goto :Error
)

for %%S in (
    "%USERPROFILE%\OneDrive\KeePass"
    "%USERPROFILE%\OneDrive\Documents"
) do (
    call BackupFolder.cmd %%S "%staging%"
    if errorlevel 1 goto :Error
)

for %%F in ("%staging%\*") do (
    echo.
    echo Moving %%~nxF to USB drive...
    move /Y "%%F" "%destination%" >nul
    if errorlevel 1 goto :Error

    echo Testing %%~nxF...
    %zipper% t "%destination%\%%~nxF" 1>nul
    if errorlevel 1 goto :Error

    echo %%~nxF is OK
)

:Success
rmdir /s /q "%staging%" 2>nul
echo.
call :PlaySound "C:\Windows\Media\tada.wav"
echo All done!  Press any key or wait 10 seconds...
timeout /t 10 >nul
exit /b 0

:Error
rmdir /s /q "%staging%" 2>nul
call :PlaySound "C:\Windows\Media\tada.wav"
echo.
echo Something went wrong.  Check errors above!
pause
exit /b 1

:PlaySound
powershell -c (New-Object Media.SoundPlayer "%~1").PlaySync()
exit /b
