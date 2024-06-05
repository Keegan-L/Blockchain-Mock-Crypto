
# Blockchain-based Project: Design Document

## Overview
This project is a blockchain-based system involving multiple nodes that communicate with a central tracker server. Each node maintains its own blockchain and can handle peer-to-peer transactions. The tracker server keeps a list of active nodes and helps facilitate communication between them.

## Architecture

### Components
1. **Tracker Server (`tracker.py`)**
   - A central server that manages a list of active blockchain nodes.
   - Provides HTTP endpoints for node registration, unregistration, and peer management.

2. **Blockchain Node (`node.py`)**
   - Represents an individual blockchain node with its own ledger and peer connections.
   - Handles the creation, validation, and broadcasting of transactions and blocks.

3. **Blockchain (`block.py`)**
   - Contains the `Block` class for managing blocks in the blockchain.
   - Each block stores transactions, and the blockchain is maintained by the nodes.

4. **HTTP Application (`app.py`)**
   - Exposes a REST API for interacting with the blockchain node.
   - Supports transaction submission, block mining, and peer management.

5. **Launcher (`launch.py`)**
   - CLI tool for starting tracker servers and blockchain nodes.
   - Allows configuration via command-line arguments. 

6. **Bank Simulator (`bank.py`)**
   - Utility for simulating banking transactions for testing purposes.
   - Can generate a series of transactions for benchmarking.

7. **Utilities (`utils.py`)**
   - Provides cryptographic functions for hashing and signing data.

### Dependencies
- `pycryptodome`
- `flask~=3.0.3`

P2P Protocol
The peer-to-peer protocol allows the tracker server and nodes to maintain a distributed ledger and manage transactions securely.

### Tracker Server (`tracker.py`)

The tracker server maintains a list of all active blockchain nodes and facilitates communication between them. 

**Class: `Tracker`**
- **Attributes:**
  - `host`: IP address of the tracker server.
  - `port`: Port number of the tracker server.
  - `server_socket`: The main socket listening for incoming connections.
  - `inputs`: List of connected clients, including the server socket.
  - `client_addresses`: Dictionary mapping client sockets to IP addresses and ports.
  - `broadcast_interval`: Interval between consecutive transaction broadcasts.
  - `last_broadcast_time`: Timestamp of the last broadcast.
- **Methods:**
  - `broadcast_transaction(data, sender_socket)`: Broadcasts a transaction to all connected nodes except the sender.
  - `attendance()`: Returns a list of all active clients' IP addresses and ports.
  - `handle_client_requests(client_socket)`: Handles client requests like attendance, disconnect, and existence notifications.
  - `remove_client(client_socket)`: Removes a client from the list of active clients.
  - `run()`: Runs the main event loop of the tracker server.

**Endpoints:**
- `POST /register`: Register a new node.
- `POST /unregister`: Unregister a node.
- `GET /peers`: Retrieve a list of active peers.

**Usage Example**

# Run tracker server
python tracker.py 5000

### Blockchain Node (`node.py`)

The blockchain node is responsible for managing a local blockchain ledger, handling transactions, and interacting with the tracker server to maintain a network of peers.


**Class: `Node`**
- **Attributes:**
  - `peers`: Dictionary of connected peers and their sockets.
  - `port`: Port number for receiving connections.
  - `tracker_address`: IP address of the tracker server.
  - `tracker_port`: Port number of the tracker server.
  - `transaction_queue`: Queue for storing transactions to be mined.
  - `blockchain`: Local instance of the `Blockchain` class.
  - `community_blockchain`: A shared copy of the blockchain maintained by the community.
  - `server`: Thread for running the server socket.
  - `mine_thread`: Thread for mining blocks.
  - `syncing`: Flag indicating whether the node is syncing with the community blockchain.
  - `active`: Flag indicating whether the node is active.
  - `address`: IP address of the node.
- **Methods:**
  - `server_socket(port)`: Opens a socket to receive connections from other nodes.
  - `create_connect(address, port_number)`: Establishes a socket connection with a peer.
  - `notify_existence(my_port)`: Notifies the tracker server of the node's existence.
  - `mine_block()`: Mines a new block using transactions from the `transaction_queue`.
  - `handle_request(client_socket)`: Handles requests from connected peers.
  - `get_balance()`: Calculates the node's balance based on the blockchain ledger using the `address` attribute.
  - `broadcast(nodes_info, info)`: Broadcasts a message to a list of nodes.
  - `close_tracker_connection()`: Closes the connection to the tracker server.
  - `request_attendance()`: Requests a list of active nodes from the tracker server.
  - `transaction(disconnect)`: Handles user interaction for submitting transactions and viewing the blockchain.

**Usage Example**

# Run blockchain node

    python node.py 127.0.0.1 5000 5001


### Transaction (`bank.py`)

The `Transaction` class represents an individual transaction within the blockchain. It contains information about the payer, payee, and the amount being transferred.

**Class: `Transaction`**
- **Attributes:**
  - `amount`: Amount of currency being transferred.
  - `payer`: IP address of the sender.
  - `payee`: IP address of the recipient.
- **Methods:**
  - `to_bytes()`: Converts the transaction data to a JSON-encoded byte string.
  - `__str__()`: Returns a human-readable representation of the transaction.
  - `__repr__()`: Returns a detailed string representation of the transaction.

**Usage Example**
python
# Creating a new transaction
transaction = Transaction(amount=10, payer='192.168.1.1', payee='192.168.1.2')
print(transaction)

### Blockchain (`block.py`)

The blockchain component is responsible for maintaining a chain of blocks that contain transactions. It uses the proof-of-work mechanism to secure the blockchain.

Blockchain Design
The blockchain design is based on a distributed ledger where each node maintains a copy of the blockchain. The system ensures integrity and security through cryptographic hashing and proof-of-work consensus.

**Class: `Blockchain`**
- **Attributes:**
  - `chain`: List of `Block` objects.
  - `difficulty`: Number of leading zeros required for a valid proof.
- **Methods:**
  - `create_genesis_block()`: Initializes the blockchain with the genesis block.
  - `last_block`: Returns the last block in the chain.
  - `proof_of_work(block)`: Finds a valid proof-of-work for the given block.
  - `add_block(block, proof)`: Adds a block to the chain if the proof is valid.
  - `is_valid_proof(block, block_hash)`: Checks if a given proof-of-work is valid for the block.
  - `add_new_transaction(transaction, address)`: Adds a new transaction to the blockchain and mines a new block.
  - `toJSON()`: Serializes the blockchain to a JSON string.
  - `fromJSON(cls, json_str)`: Deserializes a blockchain object from a JSON string.

**Class: `Block`**
- **Attributes:**
  - `timestamp`: Timestamp of the block creation.
  - `transaction`: Main transaction in the block.
  - `transaction_reward`: Reward transaction for the miner.
  - `previous_block_hash`: Hash of the previous block.
  - `nonce`: Nonce used for the proof-of-work.
- **Methods:**
  - `_hash()`: Computes the hash of the block.
  - `__str__()`: Returns a human-readable representation of the block.
  - `__repr__()`: Returns a detailed string representation of the block.
  - `toJSON()`: Serializes the block to a JSON string.

  

**Usage Example**
python
# Create a blockchain and add transactions

    blockchain = Blockchain()
    transaction = Transaction(amount=10, payer='192.168.1.1', payee='192.168.1.2')
    blockchain.add_new_transaction(transaction, address='192.168.1.1')

# View the blockchain
    for block in blockchain.chain:
        print(block)

### Utilities (`utils.py`)

This module contains utility functions for cryptographic operations like hashing.

**Functions:**
- `calculate_hash(data, hash_function="sha256")`: Computes the hash of the given data using the specified hash function.
  - **Arguments:**
    - `data`: The data to be hashed (string or byte array).
    - `hash_function`: The hash function to use (default is "sha256").
  - **Returns:** Hexadecimal string of the hash.

**Usage Example**

python
# Calculate SHA256 hash of a string
    data = "Hello, blockchain!"
    hash_value = calculate_hash(data)
    print(f"Hash Value: {hash_value}")

### HTTP Application (`app.py`)

The HTTP application is a Flask-based REST API for interacting with the blockchain node. It provides endpoints for transaction submission, balance retrieval, node status, and more.

**Endpoints:**
- `GET /`: Returns the homepage with the node's IP address and port.
- `GET /logs`: Retrieves recent application logs.
- `GET /balance`: Retrieves the current balance of the node.
- `GET /status`: Retrieves the current status of the node (active/inactive).
- `POST /transaction`: Submits a new transaction.
- `GET /active_nodes`: Retrieves a list of active nodes.
- `POST /disconnect`: Disconnects the node from the network.
- `POST /connect_node`: Connects the node to a new address and port.
- `POST /reconnect_node`: Reconnects a previously disconnected node.

**Class: `Node` (within `node.py` is utilized)**
- **Attributes:**
  - `node`: Instance of the `Node` class representing the blockchain node.
  - `logs`: Deque storing recent application logs.
- **Methods:**
  - `find_free_port(start_port=50000, end_port=60000)`: Finds a free port within a given range.
  - `notify_tracker()`: Notifies the tracker server of the node's existence.

**Usage Example**

# Run the HTTP application
    python app.py

### Demo Application
The demo application for this project is a cryptocurrency wallet that allows users to:

1. **Check Balance:** View the balance of their account.
2. **Make Transactions:** Transfer cryptocurrency to other users in the network.
3. **View Active Nodes:** Check the list of currently active nodes.
4. **Mine Blocks:** Mine new blocks to earn rewards.

### Testing Overview
The project is tested to ensure resilience against invalid transactions and block modifications. The testing strategy includes:

- **Unit Testing:** Testing individual components like the transaction, block, and blockchain classes.
- **Integration Testing:** Verifying the interaction between tracker server, nodes, and blockchain.
- **Functional Testing:** Checking the functionality of the demo application (wallet).

### Graphical Interface

1. **Launching the webpage:**
   Start the HTTP application using `app.py`:

        python app.py


**For `TESTING`:**

> ### Testing Protocol
> The project follows a detailed testing protocol to ensure the blockchain remains synchronized and transactions are correctly broadcasted. The protocol includes:
> - **Terminal UI Testing:** Ensures blockchain synchronization and transaction management using terminal commands.
> - **Flask and HTML Front-End Testing:** Validates the accuracy of balances and node synchronization via the HTML front end.
>
> For specific test cases, checkpoints, and Google VM testing details, refer to the [TESTING.md](./TESTING.md) document.