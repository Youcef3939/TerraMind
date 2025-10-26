@echo off
REM TerraMind setup script for windows
REM THE AI for sustainable agriculture platform

echo setting up TerraMind, THE AI for sustainable agriculture
echo ========================================================

REM check if python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo python is required but not installed. please install python 3.8+ and try again
    pause
    exit /b 1
)

REM check if node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo node.js is required but not installed. please install node.js 16+ and try again
    pause
    exit /b 1
)

echo python and node.js are installed

REM create necessary directories
echo creating project directories...
if not exist "reports" mkdir reports
if not exist "data" mkdir data
if not exist "models" mkdir models
if not exist "logs" mkdir logs

REM backend setup
echo setting up Python backend...
cd backend

REM create virtual environment
python -m venv venv
call venv\Scripts\activate.bat

REM install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

echo backend dependencies installed

REM frontend setup
echo setting up react frontend...
cd ..\frontend

REM install node.js dependencies
npm install

echo frontend dependencies installed

REM create environment file
echo creating environment configuration...
cd ..\backend
if not exist ".env" (
    copy env.example .env
    echo created .env file. please update with your API keys:
    echo    - OPENWEATHER_API_KEY
    echo    - SENTINEL_HUB_KEY
    echo    - LANDSAT_API_KEY
)

cd ..

REM create startup scripts
echo creating startup scripts...

REM backend startup script
echo @echo off > start_backend.bat
echo cd backend >> start_backend.bat
echo call venv\Scripts\activate.bat >> start_backend.bat
echo uvicorn main:app --reload --host 0.0.0.0 --port 8000 >> start_backend.bat

REM frontend startup script
echo @echo off > start_frontend.bat
echo cd frontend >> start_frontend.bat
echo npm start >> start_frontend.bat

echo.
echo 🎉 TerraMind setup completed!
echo.
echo next steps:
echo 1. update backend\.env with your API keys
echo 2. start the backend: start_backend.bat
echo 3. start the frontend: start_frontend.bat
echo 4. open http://localhost:3000 in your browser
echo.
echo API documentation: http://localhost:8000/docs
echo.
echo happy farming with TerraMind!
pause