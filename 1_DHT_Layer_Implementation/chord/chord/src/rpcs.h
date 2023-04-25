#ifndef RPCS_H
#define RPCS_H

#include "chord.h"
#include "rpc/client.h"
#include "math.h"

bool is_join = false;                         // check if node has joined or create
int m_bit = 32, next = 0, FT_size = 4, r = 4; // next : index of the next finger to fix, r : length of successor_list (unused)
Node self, successor, predecessor;
uint64_t mod_p = static_cast<uint64_t>(pow((double)2, (double)32));
Node* FT = new Node[FT_size];
Node* successor_list = new Node[r];

Node get_info() { return self; } // Do not modify this line.

void create() {
  for (int i = 0; i < FT_size; i++){
    FT[i].ip = "";
  }
  for (int i = 0; i < r; i++){
    successor_list[i].ip = "";
  }
  predecessor.ip = "";
  successor = self;
  is_join = true;

  FT[0] = successor;
  successor_list[0] = self;
}

void join(Node n) {
  for (int i = 0; i < FT_size; i++){
    FT[i].ip = "";
  }
  for (int i = 0; i < r; i++){
    successor_list[i].ip = "";
  }

  predecessor.ip = "";
  rpc::client client(n.ip, n.port);
  successor = client.call("find_successor", self.id).as<Node>();
  
  is_join = true;
  FT[0] = successor;
  successor_list[0] = self;
  // check if now only 2 nodes
  Node n_successor = client.call("get_successor").as<Node>();
  if (n.port == n_successor.port) {
    client.call("change_successor", self);
    client.call("change_predecessor", self);
    // client.call("change_first_successor", self);
  }
}

Node closet_preceding_node(uint64_t id) {
  // case1 : n.id > id, return the largest node in FT or successor
  if (self.id > id) {
    Node n;
    n.id = 0;
    n.ip = "";
    for (int i = FT_size - 1; i >= 0; i--) {
      if (FT[i].ip != "") {
        if (n.id < FT[i].id && FT[i].id > self.id) {
          n = FT[i];
        }
      }
    }
    if (n.ip != "") {
      return n;
    }
  } else {
    // try to find closet_preceding_node between n & id, if dosen't exist then return successor 
    for(int i = FT_size - 1; i >= 0; i--) {
      if (FT[i].ip != "" && (FT[i].id > self.id && FT[i].id < id)) {
        return FT[i];
      }
    }
  }
  return successor;
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
    Node n = closet_preceding_node(id);
    rpc::client client(n.ip, n.port);
    return client.call("find_successor", id).as<Node>();
  }
}

void stabilize() {
  if (!is_join) { return; }
  try {
    rpc::client client(successor.ip, successor.port);
    Node x = client.call("get_predecessor").as<Node>(); // x = successor.predecssor
    // try update successor
    if (x.ip != "") {
      if((self.id < successor.id && x.id > self.id && x.id < successor.id) ||
         (self.id > successor.id && ((x.id < self.id && x.id < successor.id) || (x.id > self.id && x.id > successor.id))))
        {
        successor = x;
      }
    }
    client.call("notify", self);
  } catch (std::exception &e) {
    successor = self;
  }
}

void notify(Node n) {
  if((predecessor.ip == "") || 
     (predecessor.id < self.id && n.id > predecessor.id && n.id < self.id) ||
     (predecessor.id > self.id && ((n.id > predecessor.id && n.id > self.id) || (n.id < predecessor.id && n.id < self.id))))
    {
    predecessor = n;
  }
}

void fix_fingers() {
  if (!is_join) { return; }
  try {
    if(next > FT_size - 1){
      next = 0;
    }
    uint64_t id_off = static_cast<uint64_t>(pow((double)2, (double)(m_bit - 4 + next)));
    FT[next] = find_successor(((self.id + id_off) % mod_p));
  } catch (std::exception &e){}
  next++;
}

void check_predecessor() {
  try {
    rpc::client client(predecessor.ip, predecessor.port);
    Node n = client.call("get_info").as<Node>();
  } catch (std::exception &e) {
    predecessor.ip = "";
  }
}

Node get_successor() {
  return successor;
}

Node get_predecessor() {
  return predecessor;
}

// get successor_list[i]
Node get_target_successor(int i) {
  return successor_list[i];
}

void change_successor(Node n) {
  successor = n;
}

void change_predecessor(Node n) {
  predecessor = n;
}

void change_first_successor(Node n) {
  successor_list[0] = n;
}

void register_rpcs() {
  add_rpc("get_info", &get_info); // Do not modify this line.
  add_rpc("create", &create);
  add_rpc("join", &join);
  add_rpc("find_successor", &find_successor);
  // newly added :
  add_rpc("closet_preceding_node", &closet_preceding_node);
  add_rpc("notify", &notify);
  add_rpc("get_successor", &get_successor);
  add_rpc("get_predecessor", &get_predecessor);
  add_rpc("change_successor", &change_successor);
  add_rpc("change_predecessor", &change_predecessor);
  // newly added for successor_list
  add_rpc("change_first_successor", &change_first_successor);
  add_rpc("get_target_successor", get_target_successor);
}

void register_periodics() {
  add_periodic(check_predecessor);
  add_periodic(stabilize);
  add_periodic(fix_fingers);
}

#endif /* RPCS_H */


// ./chord 127.0.0.1 5057 & ./chord 127.0.0.1 5058 & ./chord 127.0.0.1 5059 & ./chord 127.0.0.1 5060 & ./chord 127.0.0.1 5061 & ./chord 127.0.0.1 5062 & ./chord 127.0.0.1 5063 & ./chord 127.0.0.1 5064 &
// python3 ./test_scripts/test_part_1.py
// python3 ./test_scripts/test_part_3-1.py
// sudo lsof -i :5057,5058,5059,5060,5061,5062,5063,5064
// sudo kill `sudo lsof -t -i :5057,5058,5059,5060,5061,5062,5063,5064`