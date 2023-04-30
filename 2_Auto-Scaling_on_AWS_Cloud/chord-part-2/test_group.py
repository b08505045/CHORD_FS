#!/usr/bin/python3

import os
import sys
import requests
import msgpackrpc
import hashlib
import boto3
import time
import subprocess
import socket

def hash(str):
        print('HASH')
        return int(hashlib.md5(str.encode()).hexdigest(), 16) & ((1 << 32) - 1)

# get instances' id from suto-scaling group
autoscaling_client = boto3.client('autoscaling', region_name='eu-central-1')
response = autoscaling_client.describe_auto_scaling_groups(
        AutoScalingGroupNames=[
        'fuhming1468',
        'fuhming'
    ]
)
instances = response['AutoScalingGroups'][0]['Instances']
size = len(instances)

print(f'group size : {size}')
instance_ids = [i['InstanceId'] for i in instances]
print(instance_ids)

# get instances' ip
instance_ips = []
ec2_client = boto3.client('ec2', region_name='eu-central-1')
for i in instances:
    ip = ec2_client.describe_instances(
        InstanceIds = [
            i["InstanceId"]
        ]
    )['Reservations'][0]['Instances'][0]['PublicIpAddress']
    instance_ips.append(ip)

size = len(instance_ips)
print(f'group size : {size}')
print(instance_ips)