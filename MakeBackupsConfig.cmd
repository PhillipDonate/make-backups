@echo off
set MB_ARCHIVE_TYPE=7z
set MB_DESTINATION=E:\Backups_NameHere
set MB_STAGING=%TEMP%\Backups_NameHere

set MB_SOURCES=^
    "%ONEDRIVE%\KeePass" ^
    "%ONEDRIVE%\Documents"
