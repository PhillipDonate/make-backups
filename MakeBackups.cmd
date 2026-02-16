@echo off
setlocal

set zipper=%~dp0\7za.exe
call MakeBackupsConfig.cmd

if not exist %MB_DESTINATION% (
    echo Could not find backups folder.  Do you need to connect the USB drive?
    goto :Error
)

call :WipeMB_STAGING
mkdir "%MB_STAGING%" 2>nul
if errorlevel 1 (
    echo Could not create temporary MB_STAGING folder.
    goto :Error
)

for %%S in (%MB_SOURCES%) do (
    call MakeBackupArchive.cmd %%S "%MB_STAGING%"
    if errorlevel 1 goto :Error
)

echo.
echo Moving backups to %MB_DESTINATION% ...
echo.

for %%F in ("%MB_STAGING%\*") do (
    echo %%~nxF
    move /Y "%%F" "%MB_DESTINATION%" >nul
    if errorlevel 1 goto :Error   
)

echo.
echo Testing all backups at %MB_DESTINATION% ...
echo.

set TEST_ARCHIVE_FAIL=0

for %%F in ("%MB_DESTINATION%\*.zip" "%MB_DESTINATION%\*.7z") do (
    %zipper% t "%MB_DESTINATION%\%%~nxF" >nul 2>&1
    if errorlevel 1 (
        set TEST_ARCHIVE_FAIL=1
        echo [FAIL] %%~nxF
    ) else (
        echo [ OK ] %%~nxF
    )
)

if "%TEST_ARCHIVE_FAIL%"=="1" goto :Error

:Success
call :WipeMB_STAGING
call :BeepSuccess
echo.
echo All done!  Press any key or wait 10 seconds...
timeout /t 10 >nul
exit /b 0

:Error
call :WipeMB_STAGING
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

:WipeMB_STAGING
rmdir /s /q "%MB_STAGING%" 2>nul
exit /b
