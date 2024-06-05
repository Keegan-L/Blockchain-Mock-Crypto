import json
import time
from utils import calculate_hash
from bank import Transaction

class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()
        self.difficulty = 3

    def create_genesis_block(self):
        genesis_block = Block(timestamp=time.time(), transaction=Transaction(0, "Genesis", "Creator"), transaction_reward=Transaction(0, "0", "0"), previous_block=None)
        self.chain.append(genesis_block)
    @property
    def last_block(self):
        return self.chain[-1]
    
    def proof_of_work(self, block):
        computed_hash = block._hash()
        while not computed_hash.startswith('0' * self.difficulty):
            block.nonce += 1
            computed_hash = block._hash()
        return computed_hash
    
    def add_block(self, block, proof):
        previous_hash = self.last_block._hash()
        if previous_hash != block.previous_block_hash or not self.is_valid_proof(block, proof):
            return False
        self.chain.append(block)
        return True
 
    def is_valid_proof(self, block, block_hash):
        return (block_hash.startswith('0' * self.difficulty) and block_hash == block._hash())

    def add_new_transaction(self, transaction, address): # Should probably have dedicated thread for this.
        last_block = self.last_block
        new_block = Block(timestamp=time.time(),
                        transaction=transaction,
                        transaction_reward= Transaction(transaction.amount * 0.1, transaction.payer, address),
                        previous_block=last_block)
        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)
        return self.chain

    def toJSON(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__, 
            sort_keys=True,
            indent=4)
    
    @classmethod
    def fromJSON(cls, json_str):
        if not json_str:
            return None
        blockchain_data = json.loads(json_str)

        # Extract necessary data from the JSON
        chain_data = blockchain_data.get('chain', [])
        difficulty = blockchain_data.get('difficulty', 3)

        # Create a new Blockchain object
        restored_blockchain = cls()

        # Restore chain and difficulty
        restored_blockchain.chain = []
        for block_data in chain_data:
            block = Block(0, None, None)  # Create a dummy block for now
            block.nonce = block_data.get('nonce', 0)
            block.previous_block_hash = block_data.get('previous_block_hash', '')
            block.timestamp = block_data.get('timestamp', 0)
            
            # Restore regular transaction
            block_transaction_data = block_data.get('transaction')
            if block_transaction_data:
                block.transaction = Transaction(
                    amount=block_transaction_data.get('amount', 0),
                    payee=block_transaction_data.get('payee', ''),
                    payer=block_transaction_data.get('payer', '')
                )
            
            # Restore transaction reward
            block_reward_data = block_data.get('transaction_reward')
            if block_reward_data:
                block.transaction_reward = Transaction(
                    amount=block_reward_data.get('amount', 0),
                    payee=block_reward_data.get('payee', ''),
                    payer=block_reward_data.get('payer', '')
                )
            
            restored_blockchain.chain.append(block)

        restored_blockchain.difficulty = difficulty

        return restored_blockchain

class Block:
    def __init__(self, timestamp, transaction, transaction_reward, previous_block=None):
        self.timestamp = timestamp
        self.transaction = transaction
        self.transaction_reward = transaction_reward
        self.previous_block_hash = previous_block._hash() if previous_block else 0
        self.nonce = 0
    
    def _hash(self):
        # data = {
        #     "transaction_data": self.transaction.to_bytes(),
        #     "transaction_reward": self.transaction_reward.to_bytes(),
        #     "time": self.timestamp,
        #     "previous_block_hash": self.previous_block_hash,
        #     "nonce": self.nonce
        #     }
        data_bytes = json.dumps(self.toJSON())
        return calculate_hash(data_bytes)

    def __str__(self):
        return f"(\nTimestamp: {self.timestamp},\n" \
               f"Transaction: {self.transaction},\n" \
               f"Transaction Reward: {self.transaction_reward},\n"\
               f"Previous Block Hash: {self.previous_block_hash},\n" \
               f"Nonce: {self.nonce}\n)"
    
    def __repr__(self):
        return f"(\nTimestamp: {self.timestamp},\n" \
               f"Transaction: {self.transaction},\n" \
               f"Transaction Reward: {self.transaction_reward},\n"\
               f"Previous Block Hash: {self.previous_block_hash},\n" \
               f"Nonce: {self.nonce}\n)"
    
    def toJSON(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__, 
            sort_keys=True,
            indent=4)
