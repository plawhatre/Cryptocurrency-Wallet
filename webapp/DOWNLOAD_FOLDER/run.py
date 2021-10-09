from block import Block
from blockchain import Blockchain
import json
from utils import jsonify_blockchain

# Recreate blockchain
with open('bc.json') as f:
	BC = json.load(f)

bc = Blockchain()

for key, value in BC.items():
	block = Block(
		value['timestamp'], 
		value['prev_hash'], 
		value['data'], 
		value['present_hash'], 
		value['nonce'], 
		value['difficulty'])
	
	if key == 'Block 0':
		bc.chain[0] = block
	else:
		bc.chain.append(block)

# Data
with open('data_hash.txt', 'r') as f:
	data = f.read()

new_block = bc.add_block(data)

json_bc = jsonify_blockchain(bc)

with open('output.json', "w") as file:
	json.dump(json_bc, file)

