@echo off

rem Archive type to use.  Expecting 7z or zip
set MB_ARCHIVE_TYPE=7z

rem Destination path for archives
set MB_DESTINATION=E:\Backups_NameHere

rem Temporary staging path for creating archives before
rem copying to destination.  Use this if the destination
rem is on slow or unreliable storage, such as a network
rem share or USB drive.  Leave unset to skip staging

set MB_STAGING=%TEMP%\Backups_NameHere

rem A list of paths to archive individually
set MB_SOURCES=^
    "%ONEDRIVE%\KeePass" ^
    "%ONEDRIVE%\Documents"
