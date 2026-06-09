@echo off
set "MainDir=Extracted_Files"

if not exist "%MainDir%" mkdir "%MainDir%"

for %%a in (*.zip) do (
    powershell -command "Expand-Archive -Path '%%a' -DestinationPath '%MainDir%\%%~na' -Force"
)
pause