import uuid
from ecdsa import SigningKey
from hashlib import sha256
import json

def gen_message_id():
	return uuid.uuid1().hex

def gen_sk():
	return SigningKey.generate()

def gen_hash(data):
	return sha256(json.dumps(data).encode('UTF-8')).hexdigest()

def sign_data(sk, data):
	return SigningKey.from_string(bytearray.fromhex(sk)).sign(data.encode('UTF-8'))

def verify_sign(vk, signature, data):
	return vk.verify(signature, data)

def jsonify_blockchain(blockchain):
	out_dict = {}
	for index, block in enumerate(blockchain.chain):
		out_dict['Block '+str(index)] = block.__dict__

	return out_dict
