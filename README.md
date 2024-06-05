[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-24ddc0f5d75046c5622901739e7c5dd533143b0c8e959d652212380cedb1ea36.svg)](https://classroom.github.com/a/-Lgd7v9y)
# CSEE 4119 Spring 2024, Class Project
## Team name: Project Node Navigators
## Team members (name, GitHub username): Chimaobi Onwuka, chimaobionwuka; Akinfolarin Ogunmodede, aogunmodede; Keegan Li, Keegan-L

## 
# Blockchain-based Project: README

## Overview
This project is a blockchain-based system involving multiple nodes that communicate with a central tracker server. Each node maintains its own blockchain and can handle peer-to-peer transactions. The tracker server keeps a list of active nodes and helps facilitate communication between them.

Here's a `README.md` file that explains the structure, compilation, and usage of  project:

md
# Blockchain-based Project: README

## Overview
This project is a blockchain-based system involving multiple Flask nodes that communicate with a central tracker server. Each node maintains its own blockchain and can handle peer-to-peer transactions. The tracker server keeps a list of active nodes and helps facilitate communication between them.

## Project Structure


        ├── app.py               # Flask HTTP Application
        ├── bank.py              # Bank Simulator (Transaction class)
        ├── block.py             # Blockchain and Block classes
        ├── node.py              # Blockchain Node class
        ├── tracker.py           # Tracker Server class
        ├── utils.py             # Utility functions (hashing)
        ├── requirements.txt     # Project dependencies
        └── templates
            └── index.html       # HTML template for the homepage


### Main Components

1. **Tracker Server (`tracker.py`):** A central server that manages a list of active blockchain nodes and facilitates communication between them.

2. **Blockchain Node (`node.py`):** Represents an individual blockchain node with its own ledger and peer connections.

3. **Blockchain (`block.py`):** Contains the `Block` and `Blockchain` classes for managing the blockchain ledger.

4. **HTTP Application (`app.py`):** Exposes a REST API for interacting with the blockchain node and serves the HTML frontend.
    - `index.html`: Displays node information via the browser.

5. **Utilities (`utils.py`):** Provides cryptographic functions for hashing and signing data.

6. **Bank Simulator (`bank.py`):** Utility for banking transactions.

## Setup

### Dependencies

Install the necessary Python packages:


    pip install -r requirements.txt


### Configuration

Ensure the tracker server IP and port are correctly set in `node.py` and `app.py`. For development purposes, you can use `127.0.0.1` (localhost).

## Usage

### Running the Tracker Server

Start the tracker server using `tracker.py`:


    python tracker.py <tracker_port>


**Example:**
    Note: Choose a custom port if `5000` is unavailable.

    python tracker.py 5000




### Running a Blockchain Node

Start a blockchain node using `node.py`:


    python node.py <tracker_address> <tracker_port> <node_port>


**Example:**

    python node.py 127.0.0.1 5000 5001


### Running the HTTP Application

Start the HTTP application using `app.py`:


    python app.py


**Endpoints:**
- `GET /`: Homepage displaying the node's IP and port.
- `GET /logs`: Retrieves recent application logs.
- `GET /balance`: Retrieves the current balance of the node.
- `GET /status`: Retrieves the current status of the node (active/inactive).
- `POST /transaction`: Submits a new transaction.
- `GET /active_nodes`: Retrieves a list of active nodes.
- `POST /disconnect`: Disconnects the node from the network.
- `POST /connect_node`: Connects the node to a new address and port.
- `POST /reconnect_node`: Reconnects a previously disconnected node.

### Running the Bank Simulator

The `bank.py` file provides a basic transaction class and can be used for testing and benchmarking.

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
If your project has a graphical user interface (GUI):

1. **Launching the webpage:**
   Start the HTTP application using `app.py`:

        python app.py


**For `TESTING`:**

> ### Testing Overview
> The project has been tested to ensure resilience against invalid transactions and block modifications. The testing strategy includes:
> - **Unit Testing:** Testing individual components like the transaction, block, and blockchain classes.
> - **Integration Testing:** Verifying the interaction between tracker server, nodes, and blockchain.
> - **Functional Testing:** Checking the functionality of the demo application (wallet).
>
> For a detailed description of test cases and execution steps, refer to the [TESTING.md](./TESTING.md) document.
