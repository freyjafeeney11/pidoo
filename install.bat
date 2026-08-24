@echo off
echo 🐾 Installing Pidoo for Windows...
echo.

REM 1. Check for Ollama
where ollama >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] Ollama is not installed. 
    echo Please download and install it first from: https://ollama.com/download/windows
    echo Once installed, run this installer again.
    pause
    exit /b
) else (
    echo ✅ Ollama is already installed.
)

REM 2. Start Ollama in the background and pull the model
echo Pulling the brain (llama3.2:3b)... this might take a minute...
start /b ollama serve >nul 2>&1
timeout /t 3 /nobreak >nul
ollama pull llama3.2:3b

REM 3. Create a hidden directory for Pidoo in the user's home folder
if not exist "%USERPROFILE%\.pidoo" mkdir "%USERPROFILE%\.pidoo"

REM 4. Set up a Python Virtual Environment and install dependencies
echo Setting up Python environment...
python -m venv "%USERPROFILE%\.pidoo\venv"
"%USERPROFILE%\.pidoo\venv\Scripts\pip" install -r requirements.txt

REM 5. Copy the main script to the hidden folder
copy /y pidoo.py "%USERPROFILE%\.pidoo\" >nul

REM 6. Create an executable batch script
echo @echo off > "%USERPROFILE%\.pidoo\pidoo.bat"
echo "%USERPROFILE%\.pidoo\venv\Scripts\python.exe" "%USERPROFILE%\.pidoo\pidoo.py" %%* >> "%USERPROFILE%\.pidoo\pidoo.bat"

echo.
echo 🎉 Pidoo is successfully installed!
echo.
echo [IMPORTANT]: To run Pidoo from anywhere by just typing "pidoo", 
echo you need to add "%USERPROFILE%\.pidoo" to your Windows PATH variable.
echo.
echo For now, you can start Pidoo by typing this exact command and pressing Enter:
echo "%USERPROFILE%\.pidoo\pidoo.bat"
echo.
pause