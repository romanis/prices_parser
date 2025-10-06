#!/bin/bash
# Installation script for Retail Price Scraper

echo "======================================"
echo "Retail Price Scraper - Installation"
echo "======================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oP '(?<=Python )\d+\.\d+')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then 
    echo "✓ Python $python_version detected (>= 3.8 required)"
else
    echo "✗ Python 3.8 or higher is required"
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "✗ Failed to install dependencies"
    exit 1
fi

# Create output directory
echo ""
echo "Creating output directory..."
mkdir -p output
echo "✓ Output directory created"

# Make scripts executable
echo ""
echo "Making scripts executable..."
chmod +x main.py
chmod +x selenium_scraper.py
chmod +x example_usage.py
echo "✓ Scripts are now executable"

# Installation complete
echo ""
echo "======================================"
echo "Installation completed successfully!"
echo "======================================"
echo ""
echo "To get started:"
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Run the scraper:"
echo "   python main.py"
echo ""
echo "3. Or try the examples:"
echo "   python example_usage.py"
echo ""
echo "For more information, see README.md"
echo ""

