from webapp.block import Block

class Blockchain:

	def __init__(self):
		self.chain = [Block.genesis()]

	def __repr__(self):
		out_string = "---Blockchain---\n"

		for block in self.chain:
			out_string = out_string + str(block) + '\n\n'

		return out_string


	def __eq__(self, new_blockchain):
		new_chain = new_blockchain.chain

		if len(new_chain) != len(self.chain):
			print("Chains have unequal lengths")
			return False

		else:
			for old_block, new_block in zip(self.chain, new_chain):
				if not old_block == new_block:
					print('The Blockchain has been tampered')
					return False
			
			print('The Blockchains matches with each other')
			return True

	def add_block(self, data):
		prev_block = self.chain[-1]
		new_block = Block.mine_block(prev_block, data)
		self.chain.append(new_block)
		return new_block

	@staticmethod
	def is_valid_chain(blockchain):

		chain = blockchain.chain

		if not chain[0] == Block.genesis():
			print('BC invalid since genesis blocks doesn\'t matches')
			return False
		
		for index, block in enumerate(chain[1:]):
			prev_block = chain[index]

			if prev_block.present_hash != block.prev_hash:
				print(prev_block.present_hash)
				print(block.prev_hash)
				print('BC invalid since block\'s prev_hash doesn\'t matches')
				return False

			if block.present_hash != Block.gen_block_hash(block):
				print('BC invalid since block\'s present_hash doesn\'t matches')
				return False

		return True

	def replace_chain(self, new_blockchain):

		new_chain = new_blockchain.chain

		if not Blockchain.is_valid_chain(new_blockchain):
			print('New chain is not valid')
			return False

		if not len(self.chain) < len(new_chain):
			print('New chain is not longer than the present chain')
			return False

		if not self.chain == new_chain[:len(self.chain)]:
			print("New chain maniputes old blocks")
			return False

		self.chain = new_chain
		print("Replaced old chain with new chain")
		return True