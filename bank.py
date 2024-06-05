from Crypto.PublicKey import RSA
import base64
import json
from utils import calculate_hash#, sign_message

class Transaction:
    def __init__(self, amount, payer, payee):
        self.amount = amount
        self.payer = payer # ip address
        self.payee = payee # ip address

    def to_bytes(self):
        data = {
            "from": self.payer,
            "to": self.payee,
            "amount": self.amount,
        }
        return json.dumps(data).encode()
    
    def __str__(self):
        return f"Amount={self.amount}, Payer={self.payer}, Payee={self.payee}"
    
    def __repr__(self):
        return f"Amount={self.amount}, Payer={self.payer}, Payee={self.payee}"