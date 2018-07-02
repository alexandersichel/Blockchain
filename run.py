from models import *

blockchain = Blockchain()\

print (blockchain.blocks)
blockchain.add_txn_to_mempool('steve', 150.0,time.time())

print (blockchain.mempool)
blockchain.create_block()
print (blockchain.blocks)