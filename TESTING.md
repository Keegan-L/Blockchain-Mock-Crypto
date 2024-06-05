


# Blockchain-based Project: Testing Document

## Overview
This document describes the testing strategy and checkpoints used to ensure the reliability and integrity of the blockchain system. The project was tested primarily through the terminal UI and the Flask-based front end.

## Testing Strategy
The testing strategy involves verifying that the blockchain remains synchronized across all nodes and that transactions are correctly broadcasted.

### Testing Levels
1. **Terminal UI Testing:**
   - Ensures that the blockchain remains synchronized and transactions are broadcasted correctly using terminal UI commands.
   - Tests the node's ability to connect to the tracker and correctly manage transactions.

2. **Flask and HTML Front-End Testing:**
   - Validates the accuracy of balances and node synchronization via the HTML front end.
   - Verifies transaction broadcasting and viewing the blockchain.

## Test Cases

### Terminal UI Testing
1. **Run the Tracker Server:**
   - Ensure the tracker server is running:
   
            python tracker.py 5000
   

2. **Run Two or More Nodes:**
   - Start multiple blockchain nodes to test network behavior:
   
            python node.py 127.0.0.1 5000 5001
            python node.py 127.0.0.1 5000 5002
            

3. **Test Node-to-Tracker Communication:**
   - Verify that each node is connected to the tracker using the `notify_existence` method:

   # In Node class
        node.notify_existence(receiver_port)
   

4. **Test Node Transaction Broadcasting:**
   - Check the transaction broadcasting functionality:
   
   # In the node terminal UI:
        1. Choose to make a transaction
        2. Provide recipient IP and amount
        3. Verify that the transaction is correctly added to the transaction queue
        4. Ensure the transaction is correctly broadcasted and added to the blockchain
        5. Verify that the transaction is mined and added to the blockchain

   

   **Code Checkpoints:**
   - `Node.transaction_queue`: Ensure transactions are added to the queue.
   - `Node.mine_block`: Check if the transaction is added to the blockchain after mining.
   - `Node.broadcast`: Verify if the transaction is broadcasted to other nodes.

5. **Test Blockchain Synchronization:**
   - Verify that each node has an identical blockchain by calling `request_attendance` and comparing the `community_blockchain` attribute.
   python
   # In Node class
   def request_attendance(self):
       ...
   

   **Code Checkpoints:**
   - `Node.community_blockchain`: Ensure it matches across all nodes.
   - `Node.handle_request`: Confirm that the `msg_type` "updated blockchain" synchronizes all nodes.

### Flask and HTML Front-End Testing
1. **Run the Tracker Server:**
   - Ensure the tracker server is running:
   
            python tracker.py 5000
   

2. **Run the HTTP Application (Front-End):**
   - Start the HTTP application:
   
            python app.py
   

3. **Test Blockchain Synchronization via Front-End:**
   - Check that each node's blockchain is synchronized by calling the `/active_nodes` and `/balance` endpoints:
   
   # Visit the homepage
   # Use the "View Active Nodes" feature
   # Verify blockchain synchronization via the "Check Balance" feature
   

   **Code Checkpoints:**
   - `Node.request_attendance`: Confirm the nodes' attendance is accurate.
   - `Node.get_balance`: Ensure the balance is correctly displayed.

4. **Test Transaction Submission via Front-End:**
   - Submit transactions via the "Submit Transaction" feature on the front-end.
   
   # Use the "Submit Transaction" feature to transfer funds between nodes
   # Check the transaction status via "View Blockchain"
   

   **Code Checkpoints:**
   - `Node.broadcast`: Ensure transactions are broadcasted to all nodes.
   - `Node.mine_block`: Confirm transactions are mined correctly.

### Testing Checkpoints (Detailed List)

1. **Tracker Communication:**
   - [ ] Tracker server accepts and manages nodes (`tracker.py`).

2. **Node-to-Tracker Notification:**
   - [ ] Each node correctly notifies the tracker (`Node.notify_existence`).

3. **Transaction Broadcasting:**
   - [ ] Transactions are added to the `Node.transaction_queue`.
   - [ ] Transactions are correctly broadcasted to all peers (`Node.broadcast`).
   - [ ] Transactions are mined and added to the blockchain (`Node.mine_block`).

4. **Blockchain Synchronization:**
   - [ ] All nodes maintain a synchronized blockchain (`Node.community_blockchain`).
   - [ ] Updated blockchain is correctly handled via the `msg_type` "updated blockchain".

5. **Front-End Integration:**
   - [ ] HTML front-end accurately displays balance and active nodes (`app.py`).
   - [ ] Front-end transaction submission synchronizes blockchain across nodes.

### How to Run Tests
1. Ensure all dependencies are installed:
   
        pip install -r requirements.txt
   

2. Run terminal UI tests:
   
        python tracker.py 5000
        python node.py 127.0.0.1 5000 5001
        python node.py 127.0.0.1 5000 5002
   

3. Run Flask and HTML front-end tests:

        # on a tracker VM
        python tracker.py 5000

        # on a node VM
        python app.py 
   

### Testing with Google VMs

The project was tested using multiple Google Cloud VMs to simulate a distributed network environment.

1. **VM Setup:**
   - **Tracker Server VM:** One VM was configured to run the tracker server.
   - **Node VMs:** Multiple VMs were used to run blockchain nodes.
   - **Flask Front-End on Node VMs:** The same VMs running the blockchain nodes were also used to run the Flask front-end application.

2. **Testing Steps:**
   - **Tracker Server:**
     - The tracker server was started on a dedicated VM:
       
            python tracker.py 5000
      

   - **Blockchain Nodes:**
     - Blockchain nodes were started on separate VMs, each connected to the tracker server:
       
            python node.py <tracker_server_ip> 5000 5001
            python node.py <tracker_server_ip> 5000 5002
      

   - **Flask Front-End:**
     - The Flask front-end application was started on the same VMs running the blockchain nodes:
       
             python app.py
      

3. **Verification:**
   - **Node Synchronization:**
     - Confirm that all nodes remain synchronized by calling the `/active_nodes` endpoint.
   - **Transaction Broadcasting:**
     - Verify that transactions submitted via the front-end or terminal UI are correctly broadcasted and mined by all nodes.

### Testing Information for `Node.transaction`

The `transaction` method in the `Node` class is an interactive function that allows users to initiate transactions, view active nodes, and interact with the blockchain through a simple terminal UI. Here's how we tested the functionality:

#### Functionalities Tested
1. **Transaction Submission (Option `t`):**
   - **Description:**
     - Allows users to select a recipient node and submit a transaction to transfer cryptocurrency.
   - **Test Approach:**
     1. Select the transaction option (`t`).
     2. Provide the recipient IP from the list of active nodes.
     3. Enter a valid amount for the transaction.
     4. Confirm that:
        - The transaction is added to `transaction_queue`.
        - The transaction is correctly broadcasted via `broadcast` method.
        - The transaction is mined and added to the blockchain via `mine_block`.

   **Code Checkpoints:**
   - `Node.transaction_queue`: Ensure transactions are added to the queue.
   - `Node.broadcast`: Verify that the transaction is broadcasted to all nodes.
   - `Node.mine_block`: Confirm that the transaction is mined and added to the blockchain.

2. **Disconnect from the Network (Option `d`):**
   - **Description:**
     - Allows users to disconnect from the network.
   - **Test Approach:**
     1. Select the disconnect option (`d`).
     2. Confirm that:
        - The node is removed from the list of active nodes in the tracker.
        - The connection to the tracker server is closed via `close_tracker_connection`.
        - The terminal displays "Disconnecting from the tracker, bye bye!"

   **Code Checkpoints:**
   - `Node.close_tracker_connection`: Verify the node is removed from the tracker.

3. **View Active Nodes (Option `a`):**
   - **Description:**
     - Allows users to view the currently active nodes in the network.
   - **Test Approach:**
     1. Select the view active nodes option (`a`).
     2. Confirm that:
        - The list of active nodes is fetched using `request_attendance`.
        - The active nodes are displayed accurately in the terminal.

   **Code Checkpoints:**
   - `Node.request_attendance`: Ensure that the list of active nodes is accurate.

4. **View Blockchain (Option `b`):**
   - **Description:**
     - Allows users to view the entire blockchain maintained by the node.
   - **Test Approach:**
     1. Select the view blockchain option (`b`).
     2. Confirm that:
        - The blockchain is displayed correctly using `pprint`.

   **Code Checkpoints:**
   - `Node.blockchain.chain`: Ensure that the blockchain is accurately displayed.

3. **Test the Terminal UI Commands:**
   - Test each option in the `transaction` method and ensure accurate behavior:
   - **Option `t`:** Make a transaction
   - **Option `d`:** Disconnect from the network
   - **Option `a`:** View active nodes
   - **Option `b`:** View the blockchain

### Notes
- Ensure all VMs have necessary permissions and firewall rules to communicate with each other.
- Update the tracker IP address and ports in the `node.py` and `app.py` files accordingly.


