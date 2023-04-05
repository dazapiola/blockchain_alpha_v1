# -*- encoding: utf-8 -*-
from uuid import uuid4
from flask import Flask, jsonify, request
from Blockchain import Blockchain

app = Flask(__name__)

app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
blockchain = Blockchain()
node_address = str(uuid4()).replace('-', '')

@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender = node_address, receiver = 'Ale zapiola', amount = 10)
    block = blockchain.create_block(proof, previous_hash)
    response = {
        'message': 'Enhorabuena, has minado un nuevo bloque',
        'index': block['index'],
        'timestamp': block['timestamp'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
        'transactions' : block['transactions']
    }
    return jsonify(response), 200

@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200

@app.route('/is_valid', methods = ['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'La cadena de bloques es válida'}
    else:
        response = {'message': 'La cadena de bloques NO es válida'}
    return jsonify(response), 200

@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all(key in json for key in transaction_keys):
        return 'Faltan algunos elementos de la transaccion', 400
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response = {'message': f'La transacción será añadida al bloque {index}'}
    return jsonify(response), 201

@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return 'No hay nodos para añadir', 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'Todos los nodos han sido conectaos. La blockchain de AleCoins contiene ahora los nodos siguientes: ',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201

@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
  """ Reemplazar la cadena por la más larga (si es necesario) """

  is_chain_replaced = blockchain.replace_chain()
  if is_chain_replaced:
      response = {'message' : 'Los nodos tenían diferentes cadenas, se ha remplazado por la Blockchain más larga.',
                  'new_chain': blockchain.chain}
  else:
      response = {'message'       : 'Todo correcto. La Blockchain en todos los nodos ya es la más larga.',
                  'actual_chain'  : blockchain.chain}
  return jsonify(response), 200  
if __name__ == "__main__":
    app.run()