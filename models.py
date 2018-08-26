import time, json, requests
from hashlib import sha256

difficulty = 2


class Blockchain():
    txns_in_block_limit = 10

    def __init__(self, blocks = [], mempool = {}, network = []):
        self.blocks =[]
        self.mempool = {}
        self.create_genesis_block()
        self.network = network

    def create_genesis_block(self):
        genesis_block = Block(
            index = 0,
            timestamp = 1531062547.271945,
            txns = [],
            previous_hash = ''
        )
        genesis_block.mine()
        self.blocks.append(genesis_block)

    def all_blocks_as_dicts(self):
        block_list = self.blocks
        list_of_block_dicts = []
        for block in block_list:
            list_of_block_dicts.append(block.__dict__)
        return list_of_block_dicts

    def add_txn_to_mempool(self, name, weight, timestamp):
        txn_dict = {
            'name': name,
            'weight': weight,
            'timestamp': timestamp
        }
        #transaction as single hash
        if self.txn_is_valid(txn_dict):
            txn_string = json.dumps(txn_dict, sort_keys = True)
            txn_id = sha256(txn_string.encode()).hexdigest()
         #checking if transaction in our mempool, only add and broadcast if not already in
         #prevents continuous propigation of txn
            if txn_id not in self.mempool:
                self.mempool[txn_id] = txn_dict
                self.network.broadcast_txn(txn_dict)
        else:
            (print ('invalid txn'))

    def create_block(self):
        #gather valid transactions from mempool
        txns_for_block = []
        mempool_list_by_timestamp = [self.mempool[txn_id] for txn_id in self.mempool]
        mempool_list_by_timestamp.sort(key = lambda txn_dict: txn_dict['timestamp'], reverse = True)
        while len(txns_for_block) < self.txns_in_block_limit and len(mempool_list_by_timestamp) > 0:
            current_txn = mempool_list_by_timestamp.pop()
            if self.txn_is_valid(current_txn):
                txns_for_block.append(current_txn)

        new_block = Block(
            index = self.last_block().index + 1,
            timestamp = time.time(),
            txns = txns_for_block,
            previous_hash = self.last_block().to_hash()
        )

        new_block.mine()
        self.add_block(new_block)

            #create a Block
            #mind block('solve' nonce)
            #add to chain

    def add_block(self, block):
        #check previous hash to verify
        previous_block =\
            self.last_block()
        if block.previous_hash != previous_block.to_hash():
            return False
        #index must be +1 of previous index
        if block.index != previous_block.index + 1:
            return False
        #transactions are valid
        for txn in block.txns:
            if not self.txn_is_valid(txn):
                return False
        #verify proof of work (hash)
        if block.to_hash()[0:difficulty] != '0'*difficulty:
            return False

        self.blocks.append(block)
        self.network.broadcast_block(block)
        print ('block added:', block.__dict__)

    def block_is_valide(self,block):
        pass
    def txn_is_valid(self, txn_dict):
        return (type(txn_dict.get('name')) == str) and (type(txn_dict.get('weight')) == float) and (type(txn_dict.get('timestamp')) == float)
    def last_block(self):
        return self.blocks[-1]
    def chain_length(self):
        return len(self.blocks)

class Block():

    def __init__(self, txns = [], timestamp = 0.0, index = 0, previous_hash = '', nonce = 0):
        self.txns = txns
        self.timestamp = timestamp
        self.index = index
        self.previous_hash = previous_hash
        self.nonce = nonce

    def to_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys = True)
        return sha256(block_string.encode()).hexdigest()

    def mine(self):
        current_block_hash = self.to_hash()
        while current_block_hash[0:difficulty] != '0'*difficulty:
            self.nonce += 1
            current_block_hash = self.to_hash()
            #print (self.nonce, current_block_hash)

    def dict_to_block(self, dict):
        return Block(
            txns = d['txns'],
            timestamp = d['timestamp'],
            index = d['index'],
            previous_hash = d['previous_hash'],
            nonce = d['nonce'],
        )

class Network():
    def __init__(self, peers):
        self.peers = peers

    def ping_all_peers(self):
        for peer_url in self.peers:
            try:
                res = requests.get(peer_url + '/ping')
                if res.text == 'pong':
                    print (peer_url, 'is live')
                else:
                    print (peer_url, 'is unavailable')
            except:
                print (peer_url, 'is unavailable')

    def broadcast_block(self, new_block):
        for peer_url in self.peers:
            try:
                res = requests.post(peer_url + '/add_block', json = new_block.__dict__)
            except:
                print (peer_url, 'failed to send block')

    def broadcast_txn(self, new_mempool_txn):
        for peer_url in self.peers:
            try:
                res = requests.post(peer_url + '/add_txn_to_mempool', json = new_mempool_txn)
            except:
                print (peer_url, 'failed to send txn')

    def get_peers_chain_length(self, peer_url):
        try:
            res = requests.get(peer_url+'/block_count')
            return res.data
        except:
            print ('error')

    def get_all_blocks(self, peer_url):
        try:
            res = requests.get(peer_url+'/get_all_blocks')
            return res.data
        except:
            print ('error')