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
ec2_client = boto3.client('ec2', region_name='eu-central-1')
response = ec2_client.describe_instances(
        InstanceIds=instance_ids
)

print(response)
size = len(response['Reservations'])
instance_ips = []
for i in range(size):
    instance_ips.append(response['Reservations'][i]['Instances'][0]['PublicIpAddress'])

print(f'group size : {size}')
print(instance_ips)