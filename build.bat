@echo off
echo Building CrossWorlds Music Editor...

rd /s /q "dist\CrossWorlds Music Editor" 2>nul
rd /s /q "dist\CrossWorlds_Audio" 2>nul
rd /s /q "build" 2>nul

pyinstaller mod_builder.spec --clean

if exist "dist\CrossWorlds Music Editor\_internal\tools" (
    rd /s /q "dist\CrossWorlds Music Editor\tools" 2>nul
    xcopy /e /i /y "dist\CrossWorlds Music Editor\_internal\tools" "dist\CrossWorlds Music Editor\tools\"
    rd /s /q "dist\CrossWorlds Music Editor\_internal\tools"
)

echo Building updater...
pyinstaller updater.py --onefile --name updater --distpath "dist\CrossWorlds Music Editor" --workpath "build" 2>nul

echo Done! Output in dist\CrossWorlds Music Editor\
pause