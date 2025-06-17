import json
import boto3
import time
import urllib.request
import base64


def lambda_handler(event, context):
    print("Received event:", json.dumps(event))
    ec2 = boto3.resource('ec2', region_name=event['region'])

    # Step 1: Launch EC2 instance
    instance = ec2.create_instances(
        ImageId=event['ami_id'],
        InstanceType=event['instance_type'],
        MinCount=1,
        MaxCount=1,
        TagSpecifications=[{
            'ResourceType': 'instance',
            'Tags': [{'Key': 'Name', 'Value': event['instance_name']}]
        }],
        NetworkInterfaces=[{
            'DeviceIndex': 0,
            'AssociatePublicIpAddress': event.get('enable_public_ip', False),
            'SubnetId': event['subnet_id'],
            'Groups': [event['security_group_id']]
        }]
    )[0]

    instance_id = instance.id
    print(f"Instance {instance_id} created.")

    # Step 2: Wait for metadata to become available
    time.sleep(10)

    ec2_client = boto3.client('ec2', region_name=event['region'])
    response = ec2_client.describe_instances(InstanceIds=[instance_id])
    instance_details = response['Reservations'][0]['Instances'][0]

    # Step 3: Get guest OS info from AMI metadata
    ami_id = instance_details['ImageId']
    try:
        image_info = ec2_client.describe_images(ImageIds=[ami_id])['Images'][0]
        guest_os_name = image_info.get('Name') or image_info.get('Description') or 'Unknown'
    except Exception as e:
        print(f"Failed to fetch AMI info: {str(e)}")
        guest_os_name = 'Unknown'

    # Step 4: Build CMDB payload
    name_tag = next((tag['Value'] for tag in instance_details.get('Tags', []) if tag['Key'] == 'Name'), 'Unnamed')
    cmdb_payload = {
        "name": name_tag,
        "state": instance_details['State']['Name'],
        "ip_address": instance_details.get('PublicIpAddress') or instance_details.get('PrivateIpAddress', 'N/A'),
        "vm_inst_id": instance_details['InstanceId'],
        "guest_os_fullname": guest_os_name,
        "object_id": ami_id
    }

    print("CMDB Payload:", cmdb_payload)

    # Step 5: Send payload to ServiceNow CMDB
    snow_url = "https://<<instance_name>>.service-now.com/api/now/table/cmdb_ci_ec2_instance"
    username = "admin"
    password = "******************"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # Using urllib instead of requests (for Lambda default runtime)
    data = json.dumps(cmdb_payload).encode("utf-8")
    request = urllib.request.Request(snow_url, data=data, headers=headers)
    auth = base64.b64encode(f"{username}:{password}".encode()).decode("utf-8")
    request.add_header("Authorization", f"Basic {auth}")

    try:
        with urllib.request.urlopen(request) as response:
            resp_data = response.read().decode()
            print("CMDB Record Created:", resp_data)
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'instance_id': instance_id,
                    'cmdb_sync_status': 'success',
                    'response': json.loads(resp_data)
                })
            }
    except Exception as e:
        print("Error posting to ServiceNow:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({
                'instance_id': instance_id,
                'cmdb_sync_status': 'failed',
                'error': str(e)
            })
        }
