#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Update package list and upgrade existing packages
sudo apt-get update
sudo apt-get upgrade -y

# Install system dependencies
sudo apt-get install -y \
    python3-dev \
    python3-pillow \
    libatlas-base-dev \
    libopenjp2-7-dev \
    libtiff5 \
    libfreetype6-dev \
    libjpeg-dev \
    libopenjp2-7 \
    libilmbase-dev \
    libopenexr-dev \
    libgstreamer1.0-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    git \
    python3-venv

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Clone and install rpi-rgb-led-matrix
git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
cd rpi-rgb-led-matrix

# Checkout specific version if RGB_MATRIX_VERSION is set
if [ ! -z "$RGB_MATRIX_VERSION" ]; then
    git checkout $RGB_MATRIX_VERSION
fi

make build-python PYTHON=$(which python3)
sudo make install-python PYTHON=$(which python3)
cd ..

echo "Setup completed successfully!"
echo "To activate the virtual environment, run: source venv/bin/activate"