from Crypto.Hash import SHA256
import base64
import time
    
def calculate_hash(data, hash_function="sha256"): # this one works
    if type(data) == str:
        data = bytearray(data, "utf-8")
    if hash_function == "sha256":
        hash_object = SHA256.new()
        hash_object.update(data)
        return hash_object.hexdigest()
    
