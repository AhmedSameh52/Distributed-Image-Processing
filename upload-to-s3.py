import boto3

session = boto3.Session(
    aws_access_key_id='AKIAQ3EGVEQVPCS7DYM5',
    aws_secret_access_key='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',
    region_name='eu-central-1'  # Assuming you want to create the bucket in the Frankfurt region
)

# Create an S3 client using the established session
s3_client = session.client('s3')

# Bucket name must be unique for all S3 users
bucket_name = 'test-s3-bucket-v145677344566'
file_name1 = 'D:/test-case-5.jpg'
object_name = 'test-case-5.jpg'
s3_client.upload_file(file_name1, bucket_name, object_name)
