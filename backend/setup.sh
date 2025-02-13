#!/bin/bash

# Check Python version
python_version=$(python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
min_version="3.10"
max_version="3.13"

version_check=$(python -c "
import sys
min_v = tuple(map(int, '$min_version'.split('.')))
max_v = tuple(map(int, '$max_version'.split('.')))
current = sys.version_info[:2]
print(1 if min_v <= current < max_v else 0)
")

if [ "$version_check" -eq 0 ]; then
    echo "Error: Python version must be >= $min_version and < $max_version (current: $python_version)"
    exit 1
fi

# Remove existing virtual environment if it exists
if [ -d "venv" ]; then
    echo "Removing existing virtual environment..."
    rm -rf venv
fi

# Create virtual environment
echo "Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Clean pip cache
echo "Cleaning pip cache..."
pip cache purge

# Install dependencies
echo "Installing dependencies..."
pip install --no-cache-dir -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOL
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=
LANGCHAIN_PROJECT=crewai
EOL
    echo "Please add your API keys to the .env file"
fi

echo "Setup complete! Virtual environment is activated."
echo "To deactivate the virtual environment, run: deactivate"
echo "Don't forget to add your API keys to the .env file" 