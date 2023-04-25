#ifndef RPCS_H
#define RPCS_H

#include "chord.h"
#include "rpc/client.h"

Node self, successor, predecessor;
uint64_t mod_p = static_cast<uint64_t>(pow((double)2, (double)32));
int r = 3; // lenth of successor list
bool is_join = false;
Node* successor_list = new Node[r]; 

Node get_info() { return self; } // Do not modify this line.

void create() {
  for (int i = 0; i < r; i++) {
     successor_list[i].ip = "";
  }
  predecessor.ip = "";
  successor = self;
  successor_list[0] = self;
  is_join = true;
}

void join(Node n) {
  for (int i = 0; i < r; i++) {
     successor_list[i].ip = "";
  }
  predecessor.ip = "";
  rpc::client client(n.ip, n.port);
  successor = client.call("find_successor", self.id).as<Node>();
  is_join = true;
  // check if now only 2 nodes
  Node n_successor = client.call("get_successor").as<Node>();
  successor_list[0] = successor;
  if (n.port == n_successor.port) {
    client.call("change_successor", self);
    client.call("change_predecessor", self);
  }
}

Node find_successor(uint64_t id) {
  id = id % mod_p;
  try {
    if ((self.id <= successor.id && ((id > self.id && id <= successor.id) || (self.id == successor.id)))
        ||
        (self.id > successor.id && ((id > self.id && id > successor.id) || (id < self.id && id <= successor.id))))
      {
      return successor;
    } else {
      rpc::client client(successor.ip, successor.port);
      return client.call("find_successor", id).as<Node>();
    }
  } catch (std::exception &e) {
    for (int i = 0; i < r; i++) {
      try {
        rpc::client client(successor_list[i].ip, successor_list[i].port);
        return client.call("find_successor", id).as<Node>();
      } catch (std::exception &e) {}
    }
  }
}

void stabilize() {
  if (!is_join) { return; }
  try {
    rpc::client client(successor.ip, successor.port);
    Node x = client.call("get_predecessor").as<Node>(); // x = successor.predecssor
    if(x.ip != ""){
      if((self.id < successor.id && x.id > self.id && x.id < successor.id) ||
         (self.id > successor.id && ((x.id < self.id && x.id < successor.id) || (x.id > self.id && x.id > successor.id)))
        ) {
        successor = x;
      }
    }
    // reconcile successofr list
    Node* list = client.call("get_successor_list").as<Node*>();
    successor_list[0] = successor;
    for (int i = 1; i < r; i++) {
      if (list[i -1].ip != "") {
        successor_list[i] = list[i - 1];
      } else {
        successor_list[i].ip = "";
      }
    }
    client.call("notify", self);
  } catch (std::exception &e) {
    // std::cout << std::to_string(self.port) + " stabilize error\n";
  }
}

void notify(Node n) {
  if((predecessor.ip == "") || 
     (predecessor.id < self.id && n.id > predecessor.id && n.id < self.id) ||
     (predecessor.id > self.id && ((n.id > predecessor.id && n.id > self.id) || (n.id < predecessor.id && n.id < self.id)))
    ) {
      predecessor = n;
      // std::cout << std::to_string(self.port) + "change predecessor to " + std::to_string(predecessor.port) + '\n';
  }
}

Node get_successor() {
  return successor;
}

Node get_predecessor() {
  return predecessor;
}

Node* get_successor_list() {
  return successor_list;
}

void change_successor(Node n) {
  successor = n;
}
void change_predecessor(Node n) {
  predecessor = n;
}

void check_predecessor() {
  try {
    rpc::client client(predecessor.ip, predecessor.port);
    Node n = client.call("get_info").as<Node>();
  } catch (std::exception &e) {
    predecessor.ip = "";
  }
}

void check_successor() {
  if (!is_join) { return; }
  try {
    rpc::client client(successor.ip, successor.port);
    Node n = client.call("get_info").as<Node>();
  } catch (std::exception &e) {
    for (int i = 0; i < r; i++) {
      try {
        rpc::client client(successor_list[i].ip, successor_list[i].port);
        Node n = client.call("get_info").as<Node>();
        successor = n;
        return;
      } catch (std::exception &e) {}
    }
  }
}

void register_rpcs() {
  add_rpc("get_info", &get_info); // Do not modify this line.
  add_rpc("create", &create);
  add_rpc("join", &join);
  add_rpc("find_successor", &find_successor);
  // newly added
  add_rpc("notify", &notify);
  add_rpc("get_predecessor", &get_predecessor);
  add_rpc("get_successor", &get_successor);
  add_rpc("get_successor_list", &get_successor_list);
  add_rpc("change_predecessor", &change_predecessor);
  add_rpc("change_successor", &change_successor);
}

void register_periodics() {
  add_periodic(check_predecessor);
  add_periodic(check_successor);
  add_periodic(stabilize);
}

#endif /* RPCS_H */


// ./chord 127.0.0.1 5057 & ./chord 127.0.0.1 5058 & ./chord 127.0.0.1 5059 & ./chord 127.0.0.1 5060 & ./chord 127.0.0.1 5061 & ./chord 127.0.0.1 5062 & ./chord 127.0.0.1 5063 & ./chord 127.0.0.1 5064 &
// python3 ./test_scripts/test_part_1.py
// sudo lsof -i :5057,5058,5059,5060,5061,5062,5063,5064
// sudo kill `sudo lsof -t -i :5057,5058,5059,5060,5061,5062,5063,5064`
