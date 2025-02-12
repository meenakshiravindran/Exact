#!/bin/bash

# Update package lists
echo "Updating package lists..."
sudo apt-get update -y

# Install texlive
echo "Installing texlive..."
sudo apt-get install -y texlive

# Check if pip is installed
if ! command -v pip &> /dev/null
then
    echo "pip is not installed. Installing pip..."
    sudo apt-get install -y python3-pip
fi

# Check if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
else
    echo "Error: requirements.txt not found!"
    exit 1
fi

echo "Installation completed successfully."
