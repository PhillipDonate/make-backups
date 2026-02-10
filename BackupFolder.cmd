@echo off

set archive_type=zip
set zipper=%~dp0\7za.exe

set source_path=%~1
set target_dir=%~2

if not defined source_path goto :Usage
if not defined target_dir goto :Usage

if not exist "%source_path%" (
    echo %source_path% not found
    goto :Error
)

if not exist "%target_dir%\" (
    echo %target_dir% is not a folder
    goto :Error
)

if not exist %zipper% (
    echo %zipper% not found
    goto :Error
)

for %%A in ("%source_path%") do set archive_name=%%~nA

set raw=%date%
set yyyy=%raw:~10,4%
set mm=%raw:~4,2%
set dd=%raw:~7,2%
set today=%yyyy%-%mm%-%dd%

set archive_path=%target_dir%\%archive_name% %today%.%archive_type%

if exist "%archive_path%" (
    echo The file %archive_path% already exists. Delete it if you want to recreate it.
    goto :Error
)

%zipper% a -mx9 "%archive_path%" "%source_path%"
if errorlevel 1 goto :Error
goto :Success

:Usage
echo Usage:
echo %0 source_path target_dir
goto :Error

:Error
exit /b 1

:Success
exit /b 0
