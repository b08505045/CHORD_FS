#!/usr/bin/python3

import msgpackrpc
import time

def new_client(ip, port):
	return msgpackrpc.Client(msgpackrpc.Address(ip, port))

def wait(t):
	print("wait {} sec...".format(t))
	time.sleep(t)

client_1 = new_client("127.0.0.1", 5057)
client_2 = new_client("127.0.0.1", 5059)

print(client_1.call("get_info"))
print(client_2.call("get_info"))

client_1.call("create")
client_2.call("join", client_1.call("get_info"))

# test the functionality after all nodes have joined the Chord ring
# print(client_1.call("find_successor", 123))
# print(client_2.call("find_successor", 123))
