@echo off
echo Building CrossWorlds_Audio...

rd /s /q "dist\CrossWorlds_Audio" 2>nul
rd /s /q "build\mod_builder" 2>nul

pyinstaller mod_builder.spec --clean

if exist "dist\CrossWorlds_Audio\_internal\tools" (
    rd /s /q "dist\CrossWorlds_Audio\tools" 2>nul
    xcopy /e /i /y "dist\CrossWorlds_Audio\_internal\tools" "dist\CrossWorlds_Audio\tools\"
    rd /s /q "dist\CrossWorlds_Audio\_internal\tools"
)

echo Done! Output in dist\CrossWorlds_Audio\
pause