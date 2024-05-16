import boto3
import threading
import time
from configure_ec2 import configure_ec2_instance
from upload_script_ec2 import upload_script_ec2
import io
import aiohttp
import asyncio


awsInstances = {}
logs = []
imagesUploaded= []
numRequests = 0
keyName = 'D:/myEC2Key.pem'
bucket_name = 'test-s3-bucket-v12345'

def init():
    session = boto3.Session(
    aws_access_key_id='AKIAQ3EGVEQVPCS7DYM5',
    aws_secret_access_key='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',
    region_name='eu-central-1'
    )
    client = session.client('elbv2')
    ec2 = session.resource('ec2')
    ec2_client = session.client('ec2')
    s3_client = session.client('s3')
    return client,ec2,ec2_client,s3_client

def create_json_data(image_keys, operation, parameter):
    json_data = []
    for key in image_keys:
        json_data.append({
            'imagekey': key,
            'imageoperation': operation,
            'imageparameter': parameter
        })
    return json_data

async def send_post_request(session, url, json_data):
    async with session.post(url, json=json_data) as response:
        print(f"POST /data {json_data['imagekey']}: {await response.text()}")

async def send_to_load_balancer(image_keys, operation, parameter):
    url = 'http://load-balancer-216628168.eu-central-1.elb.amazonaws.com/data'

    # List of JSON data payloads to be sent
    json_datas = create_json_data(image_keys, operation, parameter)
    async with aiohttp.ClientSession() as session:
        tasks = [send_post_request(session, url, json) for json in json_datas]
        await asyncio.gather(*tasks)

def upload_to_s3():
    _,_,_,s3_client = init()
    for index in range(imagesUploaded):
        object_name = f'test-case-{index+1}.jpg'
        # Convert the PIL image to a BytesIO object
        image_buffer = io.BytesIO()
        imagesUploaded[index].save(image_buffer, format='JPEG')
        image_buffer.seek(0) 
        s3_client.upload_file(image_buffer, bucket_name, object_name)
        logs.insert(0,('Image uploaded to s3!', 'finished'))

def create_ec2_instance(target_group_arn):
    client,ec2,ec2_client,_ = init()

    # Create EC2 instance
    instances = ec2.create_instances(
        ImageId='ami-01e444924a2233b07',  # Ensure this AMI ID is available in 'eu-central-1'
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',
        KeyName='myEC2Key'  # Ensure you have this key pair in 'eu-central-1'
    )
    # Wait for the instance to be in a running state
    instance = instances[0]
    instance.wait_until_running()
    instance_id = instance.id
    logs.insert(0, (f'EC2 Instance with id {instance_id} Created Successfully!','finished'))
    print(logs)
    time.sleep(30)

    # Refresh to get the latest data
    instance.load()
    # Retrieve and print the public IP address
    public_ip_address = instance.public_ip_address

    print(f"EC2 Instance {instance.id} created and running.")
    configure_ec2_instance(public_ip_address,keyName)
    response = client.register_targets(
    TargetGroupArn=target_group_arn,
    Targets=[
        {
            'Id': instance.id,
            'Port': 80  # Specify the port on which the target receives traffic, adjust if needed
        }
    ]
    )
    upload_script_ec2(public_ip_address,keyName)
    print("Instance registered to target group:", response)

def get_number_of_instances_in_target_group(target_group_arn):
    # Initialize the ELBv2 client
    client,_,_,_ = init()

    # Describe target health to get information about targets in the target group
    response = client.describe_target_health(TargetGroupArn=target_group_arn)
    instance_count = len(response['TargetHealthDescriptions'])
    return instance_count


def scale(scale_interval,threshold, target_group):
    global numRequests
    global awsInstances
    while True:
        print ('checking to scale..')
        numVmsRunning = get_number_of_instances_in_target_group(target_group)
        if numRequests % 5 ==0: # 5 requests per vm
            numVms = (numRequests // threshold)
        else:
            numVms = (numRequests // threshold) + 1
        desiredVms = numVms - numVmsRunning
        print(f'numVmsRunning= {numVmsRunning}, numVms = {numVms}, desiredVms = {desiredVms}, numRequests = {numRequests}')
        if desiredVms < 0 :
            desiredVms = desiredVms * -1

            for i in range(desiredVms):
                if numVmsRunning <= 2:
                    break
                terminate_instance(list(awsInstances.keys())[i])

                numVmsRunning = numVmsRunning -1
        else:
            for i in range (desiredVms):
                thread = threading.Thread(target=create_ec2_instance, args=(target_group,))
                thread.start()
        awsInstances = get_instance_health_dict(target_group)
        numRequests = 0
        time.sleep(scale_interval)

def terminate_instance(instance_id):
    # Terminate the instance
    _,ec2,_,_= init()
    instance = ec2.Instance(instance_id)
    instance.terminate()

def get_instance_health_dict(target_group_arn):
    client,_,_,_ = init()

    # Call describe_target_health to get the health status of instances in the target group
    response = client.describe_target_health(TargetGroupArn=target_group_arn)

    # Dictionary to hold instance health status
    health_dict = {}

    # Process the response
    for target_health_description in response['TargetHealthDescriptions']:
        # Add the target ID and its health state to the dictionary
        health_dict[target_health_description['Target']['Id']] = target_health_description['TargetHealth']['State']

    return health_dict

def fault_tolerance(target_group_arn, threshold,check_interval):
    while True:
        client,_,_,_ = init()
        response = client.describe_target_health(TargetGroupArn=target_group_arn)

        healthy_count = sum(1 for target in response['TargetHealthDescriptions']
                            if target['TargetHealth']['State'] == 'healthy')

        print(f"healthy instances count: {healthy_count}")
        awsInstances = get_instance_health_dict(target_group_arn)
        for instance_id, health_state in awsInstances.items():
            if health_state== 'healthy':
                logs.insert(0,(f'EC2 instance {instance_id} is healthy and ready to execute!', 'healthy'))
            else:
                logs.insert(0, (f'EC2 instance {instance_id} went down, Creating another instance..', 'not healthy'))
        if healthy_count < threshold:
            print("Unhealthy instance count is below the threshold. Creating an EC2 instance...")
            for i in range(threshold - healthy_count):
                thread = threading.Thread(target=create_ec2_instance, args=(target_group_arn,))
                thread.start()

        else:
            print("No need to create a new instance. The number of unhealthy instances is not below the threshold.")
        time.sleep(check_interval)  # Wait before checking again




if __name__ == '__main__':
    check_interval = 260
    target_group_arn = 'arn:aws:elasticloadbalancing:eu-central-1:058264462378:targetgroup/target-group-2/1628f616d766de4d'
    awsInstances = get_instance_health_dict(target_group_arn)
    thread = threading.Thread(target=fault_tolerance, args=(target_group_arn,2,check_interval,))
    thread.start()
    thread.join()





# Replace 'your-load-balancer-name' with your actual ELB name
# unhealthy = ''
# if unhealthy:
#     print("Unhealthy Instances:")
#     for instance_id, state in unhealthy:
#         print(f"Instance ID: {instance_id}, State: {state}")
# else:
#     print("All instances are healthy.")




# def get_instance_health_dict(elb_name):
#     client = init()

#     # Call describe_instance_health to get the health status of instances
#     response = client.describe_instance_health(LoadBalancerName=elb_name)

#     # Dictionary to hold instance health status
#     health_dict = {}

#     # Process the response
#     for instance in response['InstanceStates']:
#         # Add the instance ID and state to the dictionary
#         health_dict[instance['InstanceId']] = instance['State']

#     return health_dict