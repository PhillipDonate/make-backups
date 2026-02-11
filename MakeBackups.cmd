@echo off

set zipper=%~dp0\7za.exe
set destination=E:\Backups_NameHere
set staging=%TEMP%\Backups_NameHere

if not exist %destination% (
    echo Could not find backups folder.  Do you need to connect the USB drive?
    goto :Error
)

call :WipeStaging
mkdir "%staging%" 2>nul
if errorlevel 1 (
    echo Could not create temporary staging folder.
    goto :Error
)

for %%S in (
    "%ONEDRIVE%\KeePass"
    "%ONEDRIVE%\Documents"
) do (
    call BackupFolder.cmd %%S "%staging%"
    if errorlevel 1 goto :Error
)

for %%F in ("%staging%\*") do (
    echo.
    echo Moving %%~nxF to %destination% ...
    move /Y "%%F" "%destination%" >nul
    if errorlevel 1 goto :Error   
)

echo.
echo Testing all backups at %destination% ...
echo.

set TEST_ARCHIVE_FAIL=0

for %%F in ("%destination%\*.zip" "%destination%\*.7z") do (
    %zipper% t "%destination%\%%~nxF" >nul 2>&1
    if errorlevel 1 (
        set TEST_ARCHIVE_FAIL=1
        echo [FAIL] %%~nxF
    ) else (
        echo [ OK ] %%~nxF
    )
)

if "%TEST_ARCHIVE_FAIL%"=="1" goto :Error

:Success
call :WipeStaging
call :BeepSuccess
echo.
echo All done!  Press any key or wait 10 seconds...
timeout /t 10 >nul
exit /b 0

:Error
call :WipeStaging
call :BeepError
echo.
echo Something went wrong.  Check errors above!
echo.
pause
exit /b 1

:BeepSuccess
powershell -c "[console]::beep(700,80); [console]::beep(900,80); [console]::beep(1100,120)"
exit /b

:BeepError
powershell -c "[console]::beep(500,120); [console]::beep(350,150); [console]::beep(250,180)"
exit /b

:WipeStaging
rmdir /s /q "%staging%" 2>nul
exit /b
