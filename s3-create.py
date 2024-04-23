import boto3

# Establish a session with your AWS credentials
session = boto3.Session(
    aws_access_key_id='AKIAQ3EGVEQVPCS7DYM5',
    aws_secret_access_key='AJKxvyffvusrXGOyDw3KVi6pz/njYBnore0mlxyE',
    region_name='eu-central-1'  # Assuming you want to create the bucket in the Frankfurt region
)

# Create an S3 client using the established session
s3_client = session.client('s3')

# Bucket name must be unique for all S3 users
bucket_name = 'test-s3-bucket-v145677344566'

# Specify the bucket configuration using the region associated with the session
location = {'LocationConstraint': session.region_name}

# Create the bucket
s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)



print(f"Bucket '{bucket_name}' created successfully in region '{session.region_name}'.")

