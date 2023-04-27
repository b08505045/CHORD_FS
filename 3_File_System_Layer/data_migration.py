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

t = 5
path = '/home/ec2-user/files'

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
print(f'ndoe hash : {my_hashed_ip}')

my_chord_client = new_client(my_node_ip, 5057)

while True:
        wait(t)
        print('run !')
        files = os.listdir(path)    # get all current files on the node
        if len(files) == 0: 
               print('no file yet')
        
        for file in files:
                if os.path.isfile(os.path.join(path, file)):
                        print(file)
        for file in files:
                h = hash(file)
                print(f' file hash : {h}', end = ',')
                node = my_chord_client.call("find_successor", h)
                node_ip = node[0].decode()
                # need to migrate data
                if node_ip != my_node_ip:
                        print(f' migrate data to {node_ip}')
                        # migrate data
                        os.system("python3 /home/ec2-uer/chord-part-2/upload.py " + (path + '/' + file) + ' ' + node_ip)
                        # delete data on local
                        os.remove(path + '/' + file)
                else: print(' no migration')


                      
               

