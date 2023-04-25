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

PORT = 5057
t = 1
is_ring = False         # check if ring exists

def new_client(ip, port):
        return msgpackrpc.Client(msgpackrpc.Address(ip, port))

def hash(str):
        return int(hashlib.md5(str.encode()).hexdigest(), 16) & ((1 << 32) - 1)

def wait(t):
        print("wait {} sec...".format(t))
        time.sleep(t)

# get self.ip
result = subprocess.run(['curl', 'http://checkip.amazonaws.com'], stdout=subprocess.PIPE)
my_node_ip = result.stdout.decode().strip()
my_hashed_ip = int(hash(my_node_ip))
print(type(my_node_ip))
print(f'My IP address:{my_node_ip}')
print(type(my_node_ip))

# Start Chord node
os.system(f"/home/ec2-user/chord {my_node_ip} 5057 &")

# Start file server
# directory = '/home/ec2-user/files'
# command = f'nohup python3 -m http.server 5058 --directory {directory} > server.log 2>&1 &'
# process = subprocess.Popen(command, shell=True)
os.system("python3 -m uploadserver 5058 --directory /home/ec2-user/files &")

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

size = len(response['Reservations'])
instance_ips = []
for i in range(size):
    instance_ips.append(response['Reservations'][i]['Instances'][0]['PublicIpAddress'])
    
print(f'group size : {size}')
print(instance_ips)

# hashed_ips
hashed_ips = [int(hash(instance_ip)) for instance_ip in instance_ips]
# find minimum of hashed_ip
min_ip = 0
if size == 1:
        min_ip = hashed_ips[0]
elif size == 2:
        min_ip = min(hashed_ips[0], hashed_ips[1])
else:
        min_ip = min(hashed_ips[0], hashed_ips[1])
        for i in range(size):
                if min_ip > hashed_ips[i]:
                        min_ip = hashed_ips[i]
print(f'My hashed ip : {my_hashed_ip}, min ip : {min_ip}')

# join or create chord ring system
my_chord_client = new_client(my_node_ip, 5057)

# test self node create successfully
try:
        my_chord_client.call("get_info")
        print('get_info test success')
except:
        print('get_info test fail')

# wait(t)
# check if any chord node exists then join, otherwise create a chord ring
for i in range(size):
        existing_node_ip = instance_ips[i]
        if my_node_ip == existing_node_ip:
                continue
        try:
                existing_chord_client = new_client(existing_node_ip, 5057)
                existing_chord_client.call("get_info")
                print('info got')
                my_chord_client.call("join", existing_chord_client.call("get_info"))
                print('good')
                is_ring = True
                break
        except:
                print('no chord yet')

if is_ring == False:
        print('no ring yet', end = ' ')
        if my_hashed_ip == min_ip:
                print('create')
                try:
                        my_chord_client.call("create")
                        print('good')
                except:
                        print('???')
        else:
                print('wait for join')
                wait(t*2)
                for i in range(size):
                        existing_node_ip = instance_ips[i]
                        if my_node_ip == existing_node_ip:
                                continue
                        try:
                                existing_chord_client = new_client(existing_node_ip, 5057)
                                existing_chord_client.call("get_info")
                                print('info got')
                                my_chord_client.call("join", existing_chord_client.call("get_info"))
                                print('good')
                                is_ring = True
                                break
                        except:
                                print('???')

print('done')