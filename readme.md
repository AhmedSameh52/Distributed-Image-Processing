# Distributed Image Processing Application

## Project Overview
This project is a distributed image processing application designed to run on AWS infrastructure. It allows for efficient processing of images across multiple instances, making use of AWS services such as EC2, S3, and ELB.

## Project Configuration
To configure and run the application, follow these steps:

1. **Clone Repository**: Clone the project from the GitHub repository [Distributed-Image-Processing](https://github.com/AhmedSameh52/Distributed-Image-Processing).

2. **Folder Structure**: After cloning the repository, you'll find the following folders and files:
    - **Fonts**: Contains fonts used in the GUI.
    - **Images**: Holds images used in the GUI.
    - **Useful Scripts**: Contains Python scripts for various tasks like uploading to S3, creating EC2 instances, etc.
    - **main.py, process-image.py, upload_script_ec2.py, configure_ec2.py**: These Python files are essential for the project's functionality.
    - **pip.sh**: A bash shell script used to configure EC2 instances after creation.
    - **requirements.txt**: Holds the required Python packages. Install these packages using the command `pip install -r requirements.txt`.

    ```bash
    pip install -r requirements.txt
    ```

3. **Configuration**: Modify the `config.py` file to set the following variables:
    - `keyName`: Path from your local computer to the `.pem` key installed from AWS.
    - `bucket_name`: Name of the S3 bucket created to upload images.
    - `aws_access_key_id` and `aws_secret_access_key`: Keys obtained from the AWS console.
    - `region_name`: Specify the AWS region used when creating EC2, S3, and ELB.
    - `load_balancer_url`: Add the URL of the load balancer.
    - `vm_ami_id`: Add the AMI ID used when creating an EC2 instance.
    - `target_group_arn`: Add the target group link to check for instance health.

## Running the Application
Once configured, run the `main.py` file to start the application. Ensure that all necessary AWS resources are set up correctly for seamless operation.

## Note
You can see a demo video here [Google Drive Video](https://drive.google.com/drive/folders/1IEMALqrVMr1BUECnW1fHSr6ODSSbomgh)
