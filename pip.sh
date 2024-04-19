#!/bin/bash

# Update package lists and upgrade the system
sudo apt-get update && sudo apt-get upgrade -y

# Install Python3 and pip
sudo apt-get install python3-pip -y

# Upgrade pip to the latest version
sudo -H pip3 install --upgrade pip

# Install Boto3
sudo -H pip3 install boto3

# Verify installation
python3 -c "import boto3; print(boto3.__version__)"
