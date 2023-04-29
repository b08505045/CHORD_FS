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
path = '/home/ec2-user/files'

def new_client(ip, port):
        return msgpackrpc.Client(msgpackrpc.Address(ip, port))

def hash(str):
        print('HASH')
        return int(hashlib.md5(str.encode()).hexdigest(), 16) & ((1 << 32) - 1)

def wait(t):
        print("wait {} sec...".format(t))
        time.sleep(t)

# get self.ip
result = subprocess.run(['curl', 'http://checkip.amazonaws.com'], stdout=subprocess.PIPE)
my_node_ip = result.stdout.decode().strip()
filename = hash(my_node_ip)
print(type(my_node_ip))
print(f'My IP address:{my_node_ip}')

# Start Chord node
os.system(f"/home/ec2-user/chord-part-2/chord {my_node_ip} 5057 &")
# Start file server
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

# join or create chord ring system
wait(t)
my_chord_client = new_client(my_node_ip, 5057)

# test self node create successfully

try:
    self = my_chord_client.call("get_info")
    print(f'get self.info test success : {self}')
except:
    print('get_info test fail')


# check if any chord node exists then join, otherwise create a chord ring
for i in range(size):
        existing_node_ip = instance_ips[i]
        if my_node_ip == existing_node_ip:
                continue
        try:
                existing_chord_client = new_client(existing_node_ip, 5057)
                existing_chord = existing_chord_client.call("get_info")
                print("info got")
                existing_chord_successor = existing_chord_client.call("get_successor", 0)
                # current existing_chord isn't in ring
                if existing_chord_successor[0] == b'':
                        print('not in the ring')
                        continue
                # current existing_chord in ring
                else:
                        print(f'find chord in the ring : {existing_chord}')
                        my_chord_client.call("join", existing_chord)
                        print('good')
                        is_ring = True
                        break
        except:
                print('no chord yet')

# create a ring
if is_ring == False:
        print('no ring yet, create one')
        try:
                my_chord_client.call("create")
                print('good')
        except:
                print('???')
print('done')