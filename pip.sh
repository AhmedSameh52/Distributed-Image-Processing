#!/bin/bash

echo "nameserver 8.8.8.8" | sudo tee -a /etc/resolv.conf

sudo apt-get update && sudo apt-get upgrade -y
sudo apt install -y python3 python3-pip python3-dev
sudo apt install -y python3-opencv
sudo apt install -y python3-boto3
sudo apt install -y python3-flask
sudo apt install -y python3-numpy



# # Update package lists and upgrade the system


# # Install Python3 and pip
# sudo apt-get install python3-pip -y

# echo 'Python installed'
# # Upgrade pip to the latest version
# sudo -H pip3 install --upgrade pip
# # echo 'upgraded'

# # Install Boto3
# sudo -H pip3 install boto3
# echo 'boto3 installed'

# #Install opencv
# sudo -H pip3 install opencv-python

# #Install Numpy
# sudo -H pip3 install numpy

# #Install mpi4py
# sudo apt-get -y install openmpi-bin openmpi-common libopenmpi-dev
# sudo -H pip3 install mpi4py
# echo 'MPI installed'

# #Install flask
# sudo -H pip3 install flask

# # # Install openGL
# # sudo apt-get -y install libgl1-mesa-glx

# # # Verify installation
# # python3 -c "import boto3; print(boto3.__version__)"


