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

def new_client(ip, port):
        return msgpackrpc.Client(msgpackrpc.Address(ip, port))

def hash(str):
        print('HASH')
        return int(hashlib.md5(str.encode()).hexdigest(), 16) & ((1 << 32) - 1)

def wait(t):
        print("wait {} sec...".format(t))
        time.sleep(t)

t = 2
# get self.ip
result = subprocess.run(['curl', 'http://checkip.amazonaws.com'], stdout=subprocess.PIPE)
my_node_ip = result.stdout.decode().strip()
my_hashed_ip = hash(my_node_ip)
print(type(my_node_ip))

wait(t)

client = new_client(my_node_ip, 5057)
self = client.call("get_info")
print(f'self : {self}')
successor = client.call("get_successor", 0)
predecessor = client.call("get_predecessor")

print(f'successor : {successor}')
print(f'predecessor : {predecessor}')

if successor[0] == b'': print('successor null')
if predecessor[0] == b'': print('predecessor null')