@echo off

:: Check Python version
python -c "import sys; min_v=(3,10); max_v=(3,13); current=sys.version_info[:2]; exit(0 if min_v <= current < max_v else 1)" 2>nul
if errorlevel 1 (
    python -c "import sys; print(f'Error: Python version must be >= 3.10 and < 3.13 (current: {sys.version_info[0]}.{sys.version_info[1]})')"
    exit /b 1
)

:: Remove existing virtual environment if it exists
if exist venv (
    echo Removing existing virtual environment...
    rmdir /s /q venv
)

:: Create virtual environment
echo Creating virtual environment...
python -m venv venv

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

:: Clean pip cache
echo Cleaning pip cache...
pip cache purge

:: Install dependencies
echo Installing dependencies...
pip install --no-cache-dir -r requirements.txt

:: Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file...
    (
        echo ANTHROPIC_API_KEY=
        echo OPENAI_API_KEY=
        echo LANGCHAIN_TRACING_V2=true
        echo LANGCHAIN_API_KEY=
        echo LANGCHAIN_PROJECT=crewai
    ) > .env
    echo Please add your API keys to the .env file
)

echo Setup complete! Virtual environment is activated.
echo To deactivate the virtual environment, run: deactivate
echo Don't forget to add your API keys to the .env file 