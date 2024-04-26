import paramiko
import boto3
from paramiko import SSHClient
from scp import SCPClient
# Connection details
ip_address = '3.64.147.215'
username = 'ubuntu'
key_filename = 'D:/myEC2Key.pem'

# Initialize SSH client
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(ip_address, username=username, key_filename=key_filename)
scp = SCPClient(ssh.get_transport())

try:
    scp = SCPClient(ssh.get_transport())
    print("SCP client established.")

    # Upload the Python script
    print("Uploading pip.sh...")
    scp.put('D:/Ain Shams/Spring 24 Senior 1/Distributed/Distributed-Image-Processing/pip.sh', '/home/ubuntu/pip.sh')
    print("pip.sh uploaded.")
    

    scp.close()
    print("SCP client closed.")

    # Make scripts executable and execute them
    commands = [
        'chmod +x /home/ubuntu/pip.sh',
        '/home/ubuntu/pip.sh',  # Execute the install script
    ]

    for command in commands:
        print(f"Executing: {command}")
        # Execute the command
        stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
    
        # Read the output as it becomes available
        for line in iter(stdout.readline, ""):
            print(line, end="")  # Print each line of the stdout
        
        # Check for any errors
        errors = stderr.read().decode()
        if errors:
            print("ERRORS:")
            print(errors)
    
        # Ensure the command has completed
        stdout.channel.recv_exit_status()

finally:
    # Close the SSH connection
    ssh.close()
