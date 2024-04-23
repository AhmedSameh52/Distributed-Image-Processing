from mpi4py import MPI
import boto3
from queue import Queue
import threading

# Initialize MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()  # Total number of processes

# This code is intended to run only on the master node
if rank == 0:
    # AWS S3 Client Setup
    session = boto3.Session(
        aws_access_key_id='AKIAQ3EGVEQVPCS7DYM5',
        aws_secret_access_key='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',
        region_name='eu-central-1'  # Assuming you want to create the bucket in the Frankfurt region
    )
    s3_client = session.client('s3')
    bucket_name = 'test-s3-bucket-v145677344566'  # Specify your bucket name

    # Fetch a list of images from S3 bucket or define it statically
    response = s3_client.list_objects_v2(Bucket=bucket_name)
    images = [content['Key'] for content in response.get('Contents', []) if content['Key'].endswith('.jpg')]

    # Define operations to perform on images
    operations = ['edge_detection', 'color_inversion']  # Extendable list of operations

    # Task distribution
    tasks = [(image, op) for image in images for op in operations]
    task_queue = Queue()

    # Load tasks into the queue
    for task in tasks:
        task_queue.put(task)

    # Distribute tasks to worker nodes
    for i in range(1, size):  # Start from 1 because rank 0 is the master
        if not task_queue.empty():
            task = task_queue.get()
            comm.send(task, dest=i, tag=11)
        else:
            break

    # Collect results from worker nodes
    results = []
    for i in range(1, size):
        result = comm.recv(source=i, tag=11)
        results.append(result)

    # Process results or save them
    print("Collected results:", results)

    # Notify workers to shut down when done
    for i in range(1, size):
        comm.send(None, dest=i, tag=11)

else:
    # Placeholder for worker initialization if needed here
    pass
