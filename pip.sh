#!/bin/bash

echo "nameserver 8.8.8.8" | sudo tee -a /etc/resolv.conf

# Update package lists and upgrade the system
sudo apt-get update && sudo apt-get upgrade -y

# Install Python3 and pip
sudo apt-get install python3-pip -y

echo 'Python installed'
# Upgrade pip to the latest version
# sudo -H pip3 install --upgrade pip
# echo 'upgraded'

# Install Boto3
sudo -H pip3 install boto3
echo 'boto3 installed'

#Install opencv
sudo -H pip3 install opencv-python

#Install Numpy
sudo -H pip3 install numpy

#Install mpi4py
sudo apt-get -y install openmpi-bin openmpi-common libopenmpi-dev
sudo -H pip3 install mpi4py
echo 'MPI installed'

# Install openGL
sudo apt-get -y install libgl1-mesa-glx

# Verify installation
python3 -c "import boto3; print(boto3.__version__)"


