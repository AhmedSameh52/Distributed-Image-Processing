import cv2  # OpenCV for image processing
import numpy as np
import boto3
import sys
import os


def init():
    session = boto3.Session(
                aws_access_key_id='AKIAQ3EGVEQVPCS7DYM5',  # Replace with your actual key
                aws_secret_access_key='AJKxvyffvusrXGOyDw3KVi6pz/njYBnore0mlxyE',  # Replace with your actual secret key
                region_name='eu-central-1'
            )
    s3_client = session.client('s3')
    return s3_client

def get_image_from_bucket(s3_client, image_key):
        bucket_name = 'test-s3-bucket-v145677344566'  # The bucket name
        response = s3_client.get_object(Bucket=bucket_name, Key=image_key)
        image_data = response['Body'].read()
        image_np = np.frombuffer(image_data, dtype=np.uint8)
        img = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
        return img

def process_image(operation, image,image_parameter):
    # Perform the specified operation
    if operation == 'edge_detection':
        result = cv2.Canny(image, 100, 200)
    elif operation == 'color_inversion':
        result = cv2.bitwise_not(image)
    elif operation == 'blur':
        result = cv2.GaussianBlur(image, (5, 5), 0)
    elif operation == 'grayscale':
        result = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    elif operation == 'rotate':
        if image_parameter == '90':
            # Rotate the image 90 degrees clockwise
            result = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        elif image_parameter == '180':
            result = cv2.rotate(image, cv2.ROTATE_180)
        elif image_parameter == '270':
            result = cv2.rotate(image,cv2.ROTATE_90_COUNTERCLOCKWISE)
    elif operation == 'resize':
        parameter = int(image_parameter)
        # Resize the image to 256x256
        result = cv2.resize(image, (parameter, parameter))
    else:
        result = image  # Default: return the original image if no operation specified
    
    return result

def upload_photo_to_s3(processed_image,s3_bucket,image_key):
    image_key = image_key.replace('.jpg', '', 1)
    processed_image_name = image_key + '_processed.jpg'
    image_path = '/home/ubuntu/'+processed_image_name
    cv2.imwrite(processed_image_name,processed_image)
    s3_client.upload_file(image_path, s3_bucket, processed_image_name)
    os.remove(image_path)


if __name__ == "__main__":
    image_key = sys.argv[1] #s3 bucket file 
    image_operation = sys.argv[2] #image processing operation
    image_parameter = sys.argv[3]
    s3_client = init()
    bucket_name = 'test-s3-bucket-v145677344566'  
    image = get_image_from_bucket(s3_client, image_key)
    processed_image = process_image(image_operation, image ,image_parameter)
    upload_photo_to_s3(processed_image,bucket_name,image_key)
    
    
    