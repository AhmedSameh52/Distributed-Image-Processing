import boto3

def rename_s3_object(bucket_name, old_key, new_key):
    session = boto3.Session(
    aws_access_key_id='AKIAQ3EGVEQVPCS7DYM5',
    aws_secret_access_key='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',
    region_name='eu-central-1'  # Assuming you want to create the bucket in the Frankfurt region
)
    # Create an S3 client
    s3_client = session.client('s3')
    
    # Copy the object to the new key within the same bucket
    copy_source = {
        'Bucket': bucket_name,
        'Key': old_key
    }
    s3_client.copy(copy_source, bucket_name, new_key)
    
    # Delete the original object
    s3_client.delete_object(Bucket=bucket_name, Key=old_key)
    print(f"Object '{old_key}' has been renamed to '{new_key}' in bucket '{bucket_name}'.")


# Example usage
bucket_name = 'test-s3-bucket-v145677344566'  # Replace with your bucket name
old_key = 'mohamed-beta2a1.jpg'  # Replace with the current object key you want to rename
new_key = 'renamed_image.jpg'  # Replace with the new object key name

rename_s3_object(bucket_name, old_key, new_key)
