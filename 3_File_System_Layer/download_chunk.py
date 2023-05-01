#!/usr/bin/python3

import sys
import requests
import msgpackrpc
import hashlib
import time

t = 2

def new_client(ip, port):
	return msgpackrpc.Client(msgpackrpc.Address(ip, port))

def hash(str):
	return int(hashlib.md5(str.encode()).hexdigest(), 16) & ((1 << 32) - 1)

def wait(t):
        print("wait {} sec...".format(t))
        time.sleep(t)

# read filename & ip
filename = sys.argv[1]
ip = sys.argv[2]
chunk_number = 0

client = new_client(ip, 5057)
chunk = []
# find chunk's location
while True:
    # name = filename_chunk_i.txt
    name = f'{filename[:-4]}_chunk_{chunk_number}.txt'
    h = hash(name)
    print("Hash of {} is {}".format(name, h))
    for i in range(3):
           try:
                 node = client.call("find_successor", h)
                 node_ip = node[0].decode()
                 break  
           except:
                 print('error, re-search')
                 wait(t)

    print(f"Try downloading {name} (hash : {h}) from http://{node_ip} (hash : {node[2]})")
    response = requests.get("http://{}:5058/{}".format(node_ip, name))
    # if no chunk then terminate
    if response.status_code == 404:
          print('404')
          break
    else:
          chunk.append(response.content)
    chunk_number += 1

with open(filename, "wb") as f:
      for chunk_i in chunk:
            f.write(chunk_i)
