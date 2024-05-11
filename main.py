import boto3
import threading
import time
from configure_ec2 import configure_ec2_instance
from upload_script_ec2 import upload_script_ec2

awsInstances = {}
keyName = 'D:/myEC2Key.pem'
def init():
    session = boto3.Session(
    aws_access_key_id='AKIAQ3EGVEQVPCS7DYM5',
    aws_secret_access_key='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',
    region_name='eu-central-1'
)
    client = session.client('elbv2')
    ec2 = session.resource('ec2')
    ec2_client = session.client('ec2')
    return client,ec2,ec2_client

def create_ec2_instance(target_group_arn):
    client,ec2,ec2_client = init()


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

    # Wait until the instance is reachable (SSH ready)
    waiter = ec2_client.get_waiter('instance_status_ok')
    waiter.wait(InstanceIds=[instance.id])

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
    # Register the new instance to the target group

    awsInstances = get_instance_health_dict(target_group_arn)


    print("Instance registered to target group:", response)


def get_instance_health_dict(target_group_arn):
    client,_,_ = init()

    # Call describe_target_health to get the health status of instances in the target group
    response = client.describe_target_health(TargetGroupArn=target_group_arn)

    # Dictionary to hold instance health status
    health_dict = {}

    # Process the response
    for target_health_description in response['TargetHealthDescriptions']:
        # Add the target ID and its health state to the dictionary
        health_dict[target_health_description['Target']['Id']] = target_health_description['TargetHealth']['State']

    return health_dict

def check_and_scale(target_group_arn, threshold,check_interval):
    while True:
        client,_,_ = init()
        response = client.describe_target_health(TargetGroupArn=target_group_arn)

        unhealthy_count = sum(1 for target in response['TargetHealthDescriptions']
                            if target['TargetHealth']['State'] != 'healthy')

        print(f"Unhealthy instances count: {unhealthy_count}")

        if unhealthy_count >= threshold:
            print("Unhealthy instance count is below the threshold. Creating an EC2 instance...")
            create_ec2_instance(target_group_arn)
        else:
            print("No need to create a new instance. The number of unhealthy instances is not below the threshold.")
        time.sleep(check_interval)  # Wait before checking again




if __name__ == '__main__':

    check_interval = 300
    target_group_arn = 'arn:aws:elasticloadbalancing:eu-central-1:058264462378:targetgroup/target-test/59420089f07fdfcf'
    # thread = threading.Thread(target=check_and_scale, args=(target_group_arn,1,check_interval))
    # thread.start()
    create_ec2_instance(target_group_arn)




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