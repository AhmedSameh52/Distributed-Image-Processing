import boto3

# Creating a session with specified AWS credentials and region
session = boto3.Session(
    aws_access_key_id='AKIAQ3EGVEQVPCS7DYM5',
    aws_secret_access_key='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',
    region_name='eu-north-1'
)

# Creating an EC2 resource from the session
ec2 = session.resource('ec2')

# Create a new EC2 instance
instances = ec2.create_instances(
    ImageId='ami-0705384c0b33c194c',  # Ensure this AMI ID is available in 'eu-central-1'
    MinCount=1,
    MaxCount=1,
    InstanceType='t3.micro',
    KeyName='myKeyPairSweden'  # Ensure you have this key pair in 'eu-central-1'
)
