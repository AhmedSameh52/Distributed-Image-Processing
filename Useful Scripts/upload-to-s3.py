import boto3

session = boto3.Session(
    aws_access_key_id='AKIAQ3EGVEQVPCS7DYM5',
    aws_secret_access_key='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',
    region_name='eu-central-1'
)

s3_client = session.client('s3')

bucket_name = 'test-s3-bucket-v12345'
file_name1 = 'D:/test-case-5.png'
object_name = 'test-case-5.png'
s3_client.upload_file(file_name1, bucket_name, object_name)

