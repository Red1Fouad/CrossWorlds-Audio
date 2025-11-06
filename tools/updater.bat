@echo off
setlocal

:: This script is called by the main application to perform an update.
:: It waits for the main application to exit, then copies the new files over.
::
:: %1: The process ID (PID) of the main application to wait for.
:: %2: The source directory of the extracted update.
:: %3: The destination directory (the root of the application).
:: %4: The executable to relaunch after the update.

echo Waiting for the application to close...
:: Tasklist is a reliable way to wait for a process to terminate.
:waitloop
tasklist /FI "PID eq %1" | find "%1" > nul
if not errorlevel 1 (
    timeout /t 1 /nobreak > nul
    goto waitloop
)

echo Application closed. Starting update...
:: Use xcopy to recursively copy all files and folders, overwriting existing ones.
xcopy /E /Y /I "%~2" "%~3"

echo Update complete. Relaunching application...
start "" "%~3\%4"

endlocal