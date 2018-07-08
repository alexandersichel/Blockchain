from models import *
from flask import Flask, request
import sys

print (sys.argv)
app = Flask(__name__)
#sys.argv makes list from command line arguments
port = int(sys.argv[-1])

blockchain = Blockchain()

@app.route('/' , methods = ['GET'])
def get_blocks():
    return json.dumps(blockchain.blocks[0].__dict__)

@app.route('/ping' , methods = ['GET'])
def send_ping():
    return 'pong'

if __name__ == '__main__':
    app.run(use_reloader=True, port=port, threaded=True, host='')

#communicate = block, transactions in mempool, consensus of chain

