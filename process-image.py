import cv2  # OpenCV for image processing
import numpy as np
import boto3
import sys
import os
from flask import Flask, request, jsonify
import requests



def init():
    session = boto3.Session(
                aws_access_key_id='AKIAQ3EGVEQVPCS7DYM5', 
                aws_secret_access_key='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', 
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
            result = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        elif image_parameter == '180':
            result = cv2.rotate(image, cv2.ROTATE_180)
        elif image_parameter == '270':
            result = cv2.rotate(image,cv2.ROTATE_90_COUNTERCLOCKWISE)
    elif operation == 'resize':
        parameter = int(image_parameter)
        result = cv2.resize(image, (parameter, parameter))
    else:
        result = image  
    
    return result

def upload_photo_to_s3(processed_image,s3_bucket,image_key,s3_client):
    image_key = image_key.replace('.jpg', '', 1)
    processed_image_name = image_key + '_processed.jpg'
    image_path = '/home/ubuntu/'+processed_image_name
    cv2.imwrite(processed_image_name,processed_image)
    s3_client.upload_file(image_path, s3_bucket, processed_image_name)
    os.remove(image_path)


app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the Load Balanced EC2 instance!"

@app.route('/data', methods=['GET', 'POST'])
def data():
    if request.method == 'POST':
        content = request.json

        # Parse content
        image_key = content.get('imagekey', 'none')
        image_operation = content.get('imageoperation', 'none')
        image_parameter = content.get('imageparameter', 'none')
        s3_client = init()
        bucket_name = 'test-s3-bucket-v145677344566'  
        image = get_image_from_bucket(s3_client, image_key)
        processed_image = process_image(image_operation, image ,image_parameter)
        upload_photo_to_s3(processed_image,bucket_name,image_key,s3_client)
        instance_id = requests.get('http://169.254.169.254/latest/meta-data/instance-id').text
        return jsonify({"received": content,"Instance ID": instance_id}), 201
    else:
        return jsonify({"message": "Send me some data!"})


@app.route('/health')
def healthcheck():
    # Perform any necessary health checks here
    # Return a successful response if the application is healthy
    return 'OK', 200

    
if __name__ == "__main__":
    # Run the Flask app
    app.run(host='0.0.0.0', port=80)

    
    
