import threading
import queue
import cv2  # OpenCV for image processing
import numpy as np
from mpi4py import MPI  # MPI for distributed computing
import boto3
import sys

# from io import BytesIO

class WorkerThread(threading.Thread):
    def __init__(self, task_queue):
        threading.Thread.__init__(self)
        self.task_queue = task_queue
        self.comm = MPI.COMM_WORLD
        self.rank = self.comm.Get_rank()
        # self.comm.send('from slave' , dest=0)

        if self.rank != 0:  # Check if it's not the master node
            session = boto3.Session(
                aws_access_key_id='AKIAQ3EGVEQVPCS7DYM5',  # Replace with your actual key
                aws_secret_access_key='AJKxvyffvusrXGOyDw3KVi6pz/njYBnore0mlxyE',  # Replace with your actual secret key
                region_name='eu-central-1'
            )
            self.s3_client = session.client('s3')

    def run(self):
        while True:
            task = self.task_queue.get()
            if task is None:
                self.task_queue.task_done()
                break
            image_path, operation = task
            result = self.process_image(image_path, operation)
            # result= 'hello world'
            self.send_result(result)
            # self.task_queue.task_done()

    def process_image(self, image_path, operation):
        # Load the image from S3 bucket
        bucket_name = 'test-s3-bucket-v145677344566'  # The bucket name
        response = self.s3_client.get_object(Bucket=bucket_name, Key=image_path)
        image_data = response['Body'].read()
        # Convert bytes data to a numpy array and then to an image
        image_np = np.frombuffer(image_data, dtype=np.uint8)
        img = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

        # Perform the specified operation
        if operation == 'edge_detection':
            result = cv2.Canny(img, 100, 200)
        elif operation == 'color_inversion':
            result = cv2.bitwise_not(img)
        else:
            result = img  # Default: return the original image if no operation specified

        return result

    def send_result(self, result):
        # Send the result to the master node if not the master
        if self.rank != 0:
            self.comm.send(result, dest=0)
    
task_queue = queue.Queue()
print('Hello again')
while True:
    # Only create and start worker threads if it's a slave node
    if MPI.COMM_WORLD.Get_rank() != 0:
        # Start threads based on the number of processors this node should use
        for i in range(MPI.COMM_WORLD.Get_size() - 1):
            WorkerThread(task_queue).start()

        # Example tasks loading (this should actually be managed by the master node)
        # Here tasks would be dynamically added to the queue
