import requests

import aiohttp
import asyncio

async def send_post_request(session, url, json_data):
    async with session.post(url, json=json_data) as response:
        print(f"POST /data {json_data['imagekey']}: {await response.text()}")

async def main():
    url = 'http://load-balancer-1-797446050.eu-north-1.elb.amazonaws.com/data'
    
    # List of JSON data payloads to be sent
    json_datas = [
        {'imagekey': 'test-case-1.jpg', 'imageoperation': 'grayscale', 'imageparameter': '0'},
        {'imagekey': 'test-case-2.jpg', 'imageoperation': 'blur', 'imageparameter': '0'},
        {'imagekey': 'test-case-3.jpg', 'imageoperation': 'edge_detection', 'imageparameter': '0'},
        {'imagekey': 'test-case-4.jpg', 'imageoperation': 'color_inversion', 'imageparameter': '0'}
        # {'imagekey': 'test-case-5.jpg', 'imageoperation': 'rotate', 'imageparameter': '180'}
    ]
    
    async with aiohttp.ClientSession() as session:
        tasks = [send_post_request(session, url, json) for json in json_datas]
        await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())


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
