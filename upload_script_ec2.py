import paramiko
import boto3
from paramiko import SSHClient
from scp import SCPClient
# Connection details

username = 'ubuntu'
key_filename = 'D:/myEC2Key.pem'

def upload_script_ec2(ip_address, key_filename):
    username = 'ubuntu'
    # Initialize SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip_address, username=username, key_filename=key_filename)
    scp = SCPClient(ssh.get_transport())

    try:
        scp = SCPClient(ssh.get_transport())
        print("SCP client established.")

        print("Uploading worker-thread.py...")
        scp.put('process-image.py', '/home/ubuntu/process-image.py')
        print("worker-thread.py uploaded.")

        scp.close()
        print("SCP client closed.")

        # Make scripts executable and execute them
        commands = [
            # 'ssh-keygen -t rsa -b 2048',
            # 'cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys',
            # 'sudo rm /home/ubuntu/hostfile',
            # 'echo "18.195.6.19 slots=1" >> hostfile',
            # 'mpirun -np 1 --hostfile /home/ubuntu/hostfile python3 /home/ubuntu/master-thread.py'   
            # 'mpiexec -n 1 python3 /home/ubuntu/test-mpi.py'
            'sudo chmod a+x /home/ubuntu/process-image.py',
            'sudo python3 /home/ubuntu/process-image.py'
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

            # 'export OMPI_MCA_btl_tcp_if_include=eth0',
            # 'mpiexec -n 1 python3 /home/ubuntu/test-mpi.py'
            # 'mpiexec --host localhost,3.71.203.243 -n 1 --verbose python3 /home/ubuntu/test-mpi.py',
            # 'ping 3.71.203.243'
            # 'python3 /home/ubuntu/worker-thread.py'