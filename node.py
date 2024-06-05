import json
from pprint import pprint
from block import Blockchain
from bank import Transaction
import socket
import time
import threading
import queue
import sys




class Node:
    def __init__(self, receiver_port, tracker_address, tracker_port):
        self.peers = {}
        self.port = receiver_port
        self.tracker_address = tracker_address
        self.tracker_port = tracker_port
        self.transaction_queue = queue.Queue()
        self.blockchain = Blockchain()
        self.community_blockchain = Blockchain() #temporarity creaion of community blockchain 
        self.server = threading.Thread(target=self.server_socket, args=(receiver_port,))
        self.server.daemon = True
        self.server.start()
        self.mine_thread = threading.Thread(target=self.mine_block)
        self.mine_thread.daemon = True
        self.mine_thread.start()
        self.syncing = False  # Added an active flag to control the server loop
        self.active = True
        self.address = None

    @property
    def balance(self):
        balance = 1000
        for block in self.blockchain.chain:
            if hasattr(block, 'transaction') and block.transaction:
                # Now correctly access payer and payee from the transaction attribute of last_block
                if block.transaction.payer == self.address:
                    balance -= block.transaction.amount
                elif block.transaction.payee == self.address:
                    balance += block.transaction.amount

            if hasattr(block, 'transaction_reward') and block.transaction_reward:
                # Now correctly access payer and payee from the transaction attribute of last_block
                if block.transaction_reward.payer == self.address:
                    balance -= block.transaction_reward.amount
                elif block.transaction_reward.payee == self.address:
                    balance += block.transaction_reward.amount
        return balance

    def server_socket(self, port):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        my_IP = socket.gethostbyname(socket.gethostname())
        self.address = my_IP
        server_address = (my_IP, port)

        server_socket.bind(server_address)

        server_socket.listen(10)
        print(f"\nNode receiving on {my_IP}:{port}")

        while True:
            client_socket, client_address = server_socket.accept()
            #print(f"Connection established from {client_address}")

            # Add client socket to dictionary of peers
            self.peers[client_address] = client_socket

            # Start new thread to handle client request
            client_thread = threading.Thread(target=self.handle_request, args=(client_socket,))

            client_thread.start()

    def create_connect(self, address, port_number):
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        my_socket.connect((address, port_number))
        print(f"Connected to server at {address}:{port_number}")

        return my_socket

    def notify_existence(self, my_port):
        # telling the tracker that this node is in the network
        # returns tuple [ip, port]

        msg = {"msg_type": "existence notification",
               "payload": {'IP': socket.gethostbyname(socket.gethostname()), 'port': my_port}}
        try:
            tracker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tracker_socket.connect((self.tracker_address, self.tracker_port))
            tracker_socket.sendall(json.dumps(msg).encode())
            self.peers["tracker_socket"] = tracker_socket
            print("Existence notification sent to tracker")
            self.active = True
        except Exception as e:
            print(f"Error2: {e}")

    def mine_block(self):
        #
        while True:
            if self.transaction_queue.qsize() > 0:
                transaction_to_mine = self.transaction_queue.get()

                new_blockchain = self.blockchain.add_new_transaction(transaction_to_mine, self.address) 

                # if len(self.community_blockchain.chain) > len(self.blockchain.chain): # fixed this line to compare the length of the chains
                #     self.blockchain.chain = self.community_blockchain.chain
                if self.community_blockchain and len(self.community_blockchain.chain) >= len(self.blockchain.chain): # fixed this line to compare the length of the chains
                    print("Replacing local blockchain with community blockchain")
                    self.blockchain.chain = self.community_blockchain.chain

                if not self.syncing:
                    # attendance = self.request_attendance()
                    # self.blockchain.chain = new_blockchain
                    self.community_blockchain.chain = self.blockchain.chain  # Sync community blockchain  # Changed line #NEWWWWWW
                    msg = {"msg_type": "updated blockchain", "payload": self.blockchain.toJSON()} # Changed line #NEWWWWWW
                    self.broadcast(self.request_attendance(), msg)
                    print("Broadcasted updated blockchain to peers")  # Added line NEWWWW
                    # self.get_balance()
                    print(f"Your new balance is ${self.balance} CHIMCHIMCOINS\n")

    def handle_request(self, client_socket):
        # deals with incoming messages
        while True:
            try:
                data = client_socket.recv(10000)
                if not data:
                    continue                    
                try:
                    d = data.decode()
                    request = json.loads(d)
                    msg_type = request.get('msg_type')  # Access msg_type safely
                    if msg_type == "attendance request":
                        self.notify_existence()

                    elif msg_type == "transaction broadcast":
                        payload = request.get('payload')  # Access payload safely
                        if payload:
                            transaction = Transaction(payload.get('amount', 0), payload.get('payer', 0), payload.get('payee', 0))
                            self.transaction_queue.put(transaction)

                    elif msg_type == "updated blockchain":
                        payload = request.get('payload')  # Access payload safely
                        if payload:
                            # if payload:
                            #     self.community_blockchain = payload
                            received_blockchain = Blockchain.fromJSON(payload)
                            if received_blockchain and (not self.community_blockchain or len(received_blockchain.chain) >= len(self.community_blockchain.chain)):
                                print(f"Replaced community blockchain in {self.address}")
                                self.syncing = True
                                self.community_blockchain.chain = received_blockchain.chain
                                self.blockchain.chain = self.community_blockchain.chain
                                self.syncing = False
                except json.JSONDecodeError as e:
                    print("JSON decode error: ", e)
                    break
                except Exception as e:
                    print(f"An error occured when processing data: {e}")
                    break
            except Exception as e:
                print(f"An error occured: {e}")
                break

    def get_balance(self):
        balance = self.balance

        last_block = self.blockchain.chain[-1]
        if hasattr(last_block, 'transaction') and last_block.transaction:
            # Now correctly access payer and payee from the transaction attribute of last_block
            if last_block.transaction.payer == self.address:
                balance -= last_block.transaction.amount
            elif last_block.transaction.payee == self.address:
                balance += last_block.transaction.amount

        if hasattr(last_block, 'transaction_reward') and last_block.transaction_reward:
            # Now correctly access payer and payee from the transaction attribute of last_block
            if last_block.transaction_reward.payer == self.address:
                balance -= last_block.transaction_reward.amount
            elif last_block.transaction_reward.payee == self.address:
                balance += last_block.transaction_reward.amount
    
        self.balance = balance

        '''
        my_ip = socket.gethostbyname(socket.gethostname())
        for block in self.blockchain.chain:
            if block.transaction.payer == my_ip:
                balance -= block.transaction.amount
            elif block.transaction.payee == my_ip:
                balance += block.transaction.amount

        self.balance = balance
        return balance
        '''


    def broadcast(self, nodes_info, info):
    # Iterate over the list of dictionaries containing node details
        for node_info in nodes_info:
            if node_info['IP'] != self.address:
                try:
                    new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    new_socket.connect((node_info['IP'], node_info['Port']))  # Use IP and Port from the dictionary
                    new_socket.send(json.dumps(info).encode())
                    new_socket.close()  # Close the socket after sending data
                    #print(f"Data sent to {node_info['IP']}:{node_info['Port']}")
                except socket.error as e:
                    print(f"Failed to connect or send data to {node_info['IP']}:{node_info['Port']}, Error: {e}")
                except json.JSONEncodeError as e:
                    print(f"Failed to encode data as JSON, Error: {e}")
                except Exception as e:
                    print(f"An unexpected error occurred, Error: {e}")

        return

    def close_tracker_connection(self):
        tracker_socket = self.peers.get("tracker_socket")
        if tracker_socket:
            try:
                disconnect_message = json.dumps({"msg_type": "disconnect"})
                tracker_socket.sendall(disconnect_message.encode())
                print("Sent disconnect message to tracker")
            except Exception as e:
                print(f"Error sending disconnect message: {e}")
            finally:
                tracker_socket.close()  # Ensure the socket is closed regardless of errors
                del self.peers["tracker_socket"]  # Clean up the peer entry
                self.active = False  # Set the node's active status to False
                print("Tracker connection closed")
        else:
            print("No tracker connection found")


    def request_attendance(self):
        # Initialize an empty list to hold the response data
        response = []

        # Define the message to request the attendance list from the tracker
        message = {'msg_type': 'attendance request', 'payload': None}
        tracker_socket = self.peers.get("tracker_socket")

        if tracker_socket:
            tracker_socket.sendall(json.dumps(message).encode())

            # Try to receive and decode the response from the tracker
            try:
                msg = tracker_socket.recv(1024).decode()
                response_dict = json.loads(msg)
                #print("Received response:", response_dict)  # Debug print to show the received JSON
                #print("Type of response:", type(response_dict))  # Debug print to show the type of the received data

                # Extract the actual list of nodes from the 'payload' key
                if 'payload' in response_dict and isinstance(response_dict['payload'], list):
                    response = response_dict['payload']
                else:
                    print("Payload is not in the expected format or not a list")

            except json.JSONDecodeError:
                print("Can't decode JSON")
            except Exception as e:
                print(f"Error occurred in request_attendance(): {e}")

        if response:
            for node_info in response:
                if isinstance(node_info, dict):
                    try:
                        #print(f"Client IP is {node_info['IP']} and client port is {node_info['Port']}")
                        pass
                    except KeyError as e:
                        print(f"Key error: {e} in node_info {node_info}")
                else:
                    print("Error: node_info is not a dictionary, received:", node_info)
        else:
            print("No nodes are currently active or received data is incorrect")

        return response
    
    def get_balancev2(self):
        balance = self.balance
        return balance


    def transaction(self, disconnect):
        while not disconnect:

            # Display options to the user
            # self.get_balance()
            print(f"What action would you like to make?\n")
            print(f"Your balance is ${self.balance} CHIMCHIMCOINS\n")
            print("1. Press 'd' to disconnect from the network")
            print("2. Press 't' to make a transaction")
            print("3. Press 'a' to view active nodes")
            print("4. Press 'b' to view the blockchain")
            resp = input("Choose an option (d, t, a, b):")

            # Validate user input
            while resp.lower() not in ["d", "t", "a", "b"]:
                resp = input("Invalid response, please enter 't' for transaction, 'd' to disconnect, or 'a' to view active nodes: ")

            if resp.lower() == "t":
                # Handle transaction request
                all_nodes = self.request_attendance()
                print("\nYou have requested to make a transaction.")
                
                if all_nodes:
                    print("Here are the available IP addresses to transact to:\n")

                    ip_list = []
                    for node_info in all_nodes:
                        if node_info['IP'] != socket.gethostbyname(socket.gethostname()):
                            ip_list.append(node_info['IP'])
                            print(f"{len(ip_list)}: IP: {node_info['IP']} Port: {node_info['Port']}")

                    recipient_number = input(f"\nEnter the number of the recipient you would like to transact with:\n ")
                    #recipient_ip = input("Enter the IP address number of the recipient: ")
                    recipient_ip = ip_list[int(recipient_number) - 1]
                    print(f"Selected Recipient IP: {recipient_ip}")

                    for node in all_nodes:
                        if recipient_ip == node['IP']:
                            recipient_port = node['Port']

                    amount = input("Enter the amount to transact: ")

                    try:
                        amount = round(float(amount), 2)
                        if amount * 1.1 > self.balance:
                            print("You do not have enough funds to complete this transaction.")
                            continue
                    except ValueError:
                        print("Invalid amount entered. Please enter a numeric value.")
                        continue

                    # Create a transaction object and broadcast it to all nodes
                    transaction = Transaction(amount, self.address, recipient_ip)

                    # if len(self.community_blockchain.chain)== len(self.blockchain.chain):
                    self.broadcast(all_nodes, {'msg_type': "transaction broadcast", "payload": transaction.__dict__})
                    self.transaction_queue.put(transaction)
                        #self.community_blockchain.chain = self.blockchain.chain

                    #self.get_balance()
                    print(f"Transaction broadcasted successfully.\n")
                    #print(f"Your new balance is ${self.balance} CHIMCHIMCOINS\n")
                else:
                    print("No available nodes to transact with.")

            elif resp.lower() == "d":
                # Handle disconnection request
                self.close_tracker_connection()
                print("Disconnecting from the tracker, bye bye!")
                disconnect = True

            elif resp.lower() == "a":
                # Handle request to view active nodes
                print(f"Fetching list of active nodes...\n")
                all_nodes = self.request_attendance()
                if all_nodes:
                    print("Currently active nodes:")
                    for node_info in all_nodes:
                        print(f"Node at IP {node_info['IP']} on Port {node_info['Port']}")
                else:
                    print("No active nodes found or unable to fetch the list.")

            elif resp.lower() == "b":
                pprint(self.blockchain.chain)
            else:
                # Fallback for any other incorrect input (just in case)
                print("Invalid option, please choose again.")
            time.sleep(1)



def terminate_node():
    global node
    if node:
        node.active = False
        node.server.join()  # Ensure all threads are properly joined
        node = None


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 node.py <tracker_address> <tracker_port> <node_port>")
        sys.exit(1)

    tracker_address = sys.argv[1]
    tracker_port = int(sys.argv[2])
    receiver_port = int(sys.argv[3])

    node = Node(receiver_port, tracker_address, tracker_port)

    # Notify tracker of existence
    node.notify_existence(receiver_port)

    disconnect = False

    # Start the transaction loop
    node.transaction(disconnect)


