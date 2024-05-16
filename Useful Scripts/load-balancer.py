import requests

import aiohttp
import asyncio
import boto3

async def send_post_request(session, url, json_data):
    async with session.post(url, json=json_data) as response:
        print(f"POST /data {json_data['imagekey']}: {await response.text()}")

async def main():
    url = 'http://load-balancer-1-910858959.eu-central-1.elb.amazonaws.com/data'
    
    # List of JSON data payloads to be sent
    json_datas = [
        {'imagekey': 'test-case-1.png', 'imageoperation': 'closing', 'imageparameter': '5'},
        {'imagekey': 'test-case-2.png', 'imageoperation': 'contour', 'imageparameter': '0'},
        {'imagekey': 'test-case-5.png', 'imageoperation': 'line_detection', 'imageparameter': '0'},
        {'imagekey': 'test-case-4.png', 'imageoperation': 'opening', 'imageparameter': '5'},
    ]
    
    async with aiohttp.ClientSession() as session:
        tasks = [send_post_request(session, url, json) for json in json_datas]
        await asyncio.gather(*tasks)

if __name__ == '__main__':

    asyncio.run(main())




# def assign_iam_role_to_instance(instance_id, iam_role_name):
    
#     try:
#         # Create EC2 client  Frankfurt -> region_name='eu-central-1
#         ec2_client = boto3.client('ec2', region_name='eu-central-1') # stockholm

#         # Associate IAM role with instance
#         response = ec2_client.associate_iam_instance_profile(
#             IamInstanceProfile={
#                 'Name': iam_role_name
#             },
#             InstanceId=instance_id
#         )

#         print(f"IAM role '{iam_role_name}' successfully assigned to instance '{instance_id}'.")
#         return True
#     except Exception as e:
#         print(f"Error: {str(e)}")
#         return False
    # assign_iam_role_to_instance('i-0b7b503dbe6e15452','s3-full-access')
    # assign_iam_role_to_instance('i-0cc17babdf15b50cb','s3-full-access')

# URL of your Application Load Balancer
# url = 'http://test-load-balancer-1152627953.eu-central-1.elb.amazonaws.com'


# # Sending a POST request with JSON data to the /data endpoint
# data_url = f'{url}/data'
# json_data = {'imagekey': 'test-case-1.jpg',
#              'imageoperation': 'grayscale',
#              'imageparameter': '0'
#              }

# response = requests.post(data_url, json=json_data)
# print('POST /data:', response.text)
# json_data = {'imagekey': 'test-case-2.jpg',
#              'imageoperation': 'blur',
#              'imageparameter': '0'
#              }

# response = requests.post(data_url, json=json_data)
# print('POST /data:', response.text)
# json_data = {'imagekey': 'test-case-3.jpg',
#              'imageoperation': 'edge_detection',
#              'imageparameter': '0'
#              }

# response = requests.post(data_url, json=json_data)
# print('POST /data:', response.text)
# json_data = {'imagekey': 'test-case-4.jpg',
#              'imageoperation': 'color_inversion',
#              'imageparameter': '0'
#              }
# response = requests.post(data_url, json=json_data)
# print('POST /data:', response.text)
