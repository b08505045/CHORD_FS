#!/usr/bin/python3

import sys
import requests
import msgpackrpc
import hashlib
import time

# chunk_size = 33
chunk_size = 5 * 1024 *1024

def new_client(ip, port):
	return msgpackrpc.Client(msgpackrpc.Address(ip, port))

def hash(str):
	return int(hashlib.md5(str.encode()).hexdigest(), 16) & ((1 << 32) - 1)

filename = sys.argv[1]
ip = sys.argv[2]

filepath = filename
slashs = [i for i, c in list(enumerate(filepath)) if c == '/']
if len(slashs) != 0:
	filename = filename[max(slashs) + 1:]

print(f'filename : {filename}')

client = new_client(ip, 5057)

# upload chunk
with open(filepath, 'rb') as f:
    chunk_number = 0
    while True:
        chunk = f.read(chunk_size)
        if not chunk:
            break
        
        # name = filename_chunk_i.txt
        name = f'{filename[:-4]}_chunk_{chunk_number}.txt'
        files = {'files': (f'{name}', chunk)}
        # print(files)
        
        h = hash(name)
        print("Hash of {} is {}".format(name, h))
        
        for i in range(3):
              try:
                    node = client.call("find_successor", h)
                    print(node)
                    node_ip = node[0].decode()
                    break
              except:
                    print('find_successor error')
        print(f"Uploading {name} (hash : {h}) to http://{node_ip} (hash : {node[2]})")
        response = requests.post('http://{}:5058/upload'.format(node_ip), files=files)
        
        chunk_number += 1