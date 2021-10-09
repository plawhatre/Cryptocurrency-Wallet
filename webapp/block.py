import hashlib
import yaml
from time import time

with open('webapp/config.yaml') as stream:
	yaml_dict = yaml.safe_load(stream) 


DIFFICULTY = yaml_dict['DIFFICULTY']
MINE_RATE = yaml_dict['MINE_RATE']

class Block:
	def __init__(self, timestamp, prev_hash, data, present_hash, nonce, difficulty):
		self.timestamp = timestamp
		self.prev_hash = prev_hash
		self.data = data
		self.present_hash = present_hash
		self.nonce = nonce
		self.difficulty = difficulty

	def __repr__(self):
		return f'\
			timestamp = {self.timestamp}\n \
			prev_hash = {self.prev_hash}\n \
			data = {self.data}\n \
			present_hash = {self.present_hash}\n \
			nonce = {self.nonce}\n \
			difficulty = {self.difficulty}'

	def __eq__(self, block):
		
		if self.prev_hash != block.prev_hash:
			print('prev_hash does not matches')
			return False
		if self.data != block.data:
			print('data does not matches')
			return False
		if self.present_hash != block.present_hash:
			print('present_hash does not matches')
			return False

		return True


	@staticmethod
	def genesis():
		return Block(str(time()), 'prev-4ddr355', [], 'present-4ddr355', 0, DIFFICULTY)		
		

	@staticmethod
	def gen_hash(timestamp, prev_hash, data, nonce, difficulty):
		return hashlib.sha256(
			str(str(timestamp) + prev_hash + str(data) + str(nonce) + str(difficulty)).encode()).hexdigest()

	@staticmethod
	def gen_block_hash(block):
		return hashlib.sha256(
			str(str(block.timestamp) + block.prev_hash + str(block.data) + str(block.nonce) + str(block.difficulty)).encode()).hexdigest()

	@staticmethod
	def adjust_difficulty(block, timestamp):
		if timestamp - float(block.timestamp) < MINE_RATE:
			return block.difficulty + 1 
		else:
			return block.difficulty - 1 

	@staticmethod
	def mine_block(prev_block, data):
		nonce = 0
		difficulty = prev_block.difficulty

		print('Mining in progress......')

		while True:
			nonce += 1
			timestamp = time()
			difficulty = Block.adjust_difficulty(prev_block, timestamp)

			new_hash = Block.gen_hash(timestamp, prev_block.present_hash, data, nonce, difficulty)

			if new_hash[:difficulty] == '0'*difficulty:
				break

		print('Mining is complete.')
		return Block(timestamp, prev_block.present_hash, data, new_hash, nonce, difficulty)
