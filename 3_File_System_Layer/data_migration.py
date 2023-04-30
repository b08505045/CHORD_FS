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

t = 20
path = '/home/ec2-user/files'

def new_client(ip, port):
        return msgpackrpc.Client(msgpackrpc.Address(ip, port))

def hash(str):
        return int(hashlib.md5(str.encode()).hexdigest(), 16) & ((1 << 32) - 1)

def wait(t):
        print("wait {} sec...".format(t))
        time.sleep(t)

print('data migration:')
# get self.ip
result = subprocess.run(['curl', 'http://checkip.amazonaws.com'], stdout=subprocess.PIPE)
my_node_ip = result.stdout.decode().strip()
# get node's hash
my_client = new_client(my_node_ip, 5057)
node = my_client.call("get_info")
hashed_node = node[2]
print(f"node's ip : {my_node_ip}, hash : {hashed_node}")

my_chord_client = new_client(my_node_ip, 5057)

while True:
        wait(t)
        print('run !')
        files = os.listdir(path)    # get all current files on the node
        if len(files) == 0: 
               print('no file yet')
        print(files)

        for file in files:
                h = hash(file)
                try:
                        node = my_chord_client.call("find_successor", h)
                except:
                        print('find_successor error')
                node_ip = node[0].decode()
                # need to migrate data
                if node_ip != my_node_ip:
                        print(f'{file} hash : {h}, migrate to {node_ip} (hash : {node[2]})')
                        # migrate data
                        try:
                                os.system("sudo python3 /home/ec2-user/chord-part-2/upload.py " + (path + '/' + file) + ' ' + node_ip)
                                # delete data on local
                                os.remove(path + '/' + file)
                                print('migrate done')
                        except:
                                print('migrate error')
                else: print(f'{file} hash : {h}, no migration')


                      
               

