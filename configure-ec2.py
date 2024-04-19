import paramiko
import boto3
from paramiko import SSHClient
from scp import SCPClient
# Connection details
ip_address = '18.153.79.185'
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
    scp.put('D:/pip.sh', '/home/ubuntu/pip.sh')
    print("pip.sh uploaded.")
    

    scp.close()
    print("SCP client closed.")

    # Make scripts executable and execute them
    commands = [
        'chmod +x /home/ubuntu/pip.sh',
        '/home/ubuntu/pip.sh',  # Execute the install script
    ]

    for command in commands:
        stdin, stdout, stderr = ssh.exec_command(command)
        stdout.channel.recv_exit_status()  # This line ensures the command completes before moving to the next one
        output = stdout.read().decode()
        errors = stderr.read().decode()

        if output:
            print(f"Output from {command}: {output}")
        if errors:
            print(f"Errors from {command}: {errors}")

finally:
    # Close the SSH connection
    ssh.close()
