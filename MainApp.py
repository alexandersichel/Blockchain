from models import *
from flask import Flask, request
import sys

print (sys.argv)
app = Flask(__name__)
#sys.argv makes list from command line arguments
port = int(sys.argv[-1])

peer_ports = [3000, 5000, 8000, 8080]
if port in peer_ports:
    peer_ports.remove(port)
prefix = 'http://localhost:'
peers = {prefix + str(port_num) for port_num in peer_ports}

network = Network(peers)

blockchain = Blockchain(network = network)

@app.route('/' , methods = ['GET'])
def get_blocks():
    return json.dumps(blockchain.blocks[0].__dict__)

@app.route('/ping' , methods = ['GET'])
def send_ping():
    return 'pong'

#node receive blocks
@app.route('/add_block' , methods = ['POST'])
def add_block():
    block_data_dict = request.json
    new_block = Block(
        txns = block_data_dict['txns'],
        timestamp = block_data_dict['timestamp'],
        index = block_data_dict['index'],
        previous_hash = block_data_dict['previous_hash'],
        nonce = block_data_dict['nonce'],
    )
    blockchain.add_block(new_block)

#node receive txn in mempool
@app.route('/add_txn_to_mempool' , methods = ['POST'])
def add_txn_to_mempool():
    txn_dict = request.json
    new_txn = {
        name: txn_dict['name'],
        weight: txn_dict['weight'],
        timestamp: txn_dict['timestamp']
    }
    blockchain.add_txn_to_mempool(new_txn)

#API for setting the endpoints
network.ping_all_peers()
if __name__ == '__main__':
    app.run(use_reloader=True, port=port, threaded=True, host='')

if port == 3000:
    blockchain.add_txn_to_mempool('steve', 150.0, time.time())
    blockchain.create_block()


#communicate = block, transactions in mempool, consensus of chain

