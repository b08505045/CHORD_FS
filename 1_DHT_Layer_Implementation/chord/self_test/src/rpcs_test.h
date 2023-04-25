#ifndef RPCS_H
#define RPCS_H

#include "chord.h"
#include "rpc/client.h"

Node self, successor, predecessor;
uint64_t mod_p = static_cast<uint64_t>(pow((double)2, (double)32));
bool is_join = false;

Node get_info() { return self; } // Do not modify this line.

void create() {
  predecessor.ip = "";
  successor = self;
  is_join = true;
}

void join(Node n) {
  predecessor.ip = "";
  rpc::client client(n.ip, n.port);
  successor = client.call("find_successor", self.id).as<Node>();
  is_join = true;
  // check if now only 2 nodes
  Node n_successor = client.call("get_successor").as<Node>();
  if (n.port == n_successor.port) {
    client.call("change_successor", self);
    client.call("change_predecessor", self);
  }
}

Node find_successor(uint64_t id) {
  id = id % mod_p;
  if ((self.id <= successor.id && ((id > self.id && id <= successor.id) || (self.id == successor.id)))
      ||
      (self.id > successor.id && ((id > self.id && id > successor.id) || (id < self.id && id <= successor.id)))
     ) {
      return successor;
     }
  else {
    rpc::client client(successor.ip, successor.port);
    return client.call("find_successor", id).as<Node>();
  }
}

void stabilize() {
  if (!is_join) { return; }
  try {
    rpc::client client(successor.ip, successor.port);
    Node x = client.call("get_predecessor").as<Node>(); // x = successor.predecssor
    if(x.ip != ""){
      // std::cout << std::to_string(self.port) + " stabilize, successor : " 
      // + std::to_string(successor.port) + ", x : " + std::to_string(x.port) + '\n';
      if((self.id < successor.id && x.id > self.id && x.id < successor.id) ||
         (self.id > successor.id && ((x.id < self.id && x.id < successor.id) || (x.id > self.id && x.id > successor.id)))
        ) {
        successor = x;
      }
    } else {
      // std::cout << std::to_string(self.port) + " stabilize, successor : " 
      // + std::to_string(successor.port) + ", x none\n";
    }
    client.call("notify", self);
    // std::cout << std::to_string(self.port) + " stabilize done\n";
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

void change_successor(Node n) {
  successor = n;
}
void change_predecessor(Node n) {
  predecessor = n;
}

Node check_predecessor() {
  Node n;
  try {
    rpc::client client(predecessor.ip, predecessor.port);
    n = client.call("get_info").as<Node>();
    return n;
  } catch (std::exception &e) {
    predecessor.ip = "";
  }
  n.ip = "";
  return n;
}

void print_predecessor() {
  try {
    rpc::client client(predecessor.ip, predecessor.port);
    Node n = client.call("get_info").as<Node>();
    if (predecessor.port == 0) {
      std::cout << "predecessor.port == 0, dosen't exist ?\n";
    } else {
      std::cout << "predecessor.port != 0, exist\n";
    }
    // std::cout << std::to_string(n.port) + '\n';
  } catch (std::exception &e) {
    std::cout << "oops\n";
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
  add_rpc("change_predecessor", &change_predecessor);
  add_rpc("change_successor", &change_successor);
  add_rpc("print_predecessor", &print_predecessor);
  add_rpc("check_predecessor", &check_predecessor);
}

void register_periodics() {
  add_periodic(check_predecessor);
  add_periodic(stabilize);
}

#endif /* RPCS_H */


// ./chord 127.0.0.1 5057 & ./chord 127.0.0.1 5058 & ./chord 127.0.0.1 5059 & ./chord 127.0.0.1 5060 & ./chord 127.0.0.1 5061 & ./chord 127.0.0.1 5062 & ./chord 127.0.0.1 5063 & ./chord 127.0.0.1 5064 &
// python3 ./test_scripts/test_part_1.py
// sudo lsof -i :5057,5058,5059,5060,5061,5062,5063,5064
// sudo kill `sudo lsof -t -i :5057,5058,5059,5060,5061,5062,5063,5064`