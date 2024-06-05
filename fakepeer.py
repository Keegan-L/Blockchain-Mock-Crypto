import json
import socket
import sys
import threading
import time
import uuid

client_id = str(uuid.uuid4())  # Should be the same ID used in send_commands, 
print(f"Client ID: {client_id}")

def verify_transaction(transaction): 
    """
    Verify if a transaction is valid.

    Args:
        transaction (str): The transaction string to be verified.

    Returns:
        bool: True if the transaction is valid, False otherwise.
    """
    parts = transaction.split()
    print(len(parts))
    if len(parts) != 4 or not parts[0] in ['send', 'request']:
        print("False 1")
        return False
    try:
        amount = float(parts[2])  # Check if the amount is a valid number and positive
        return amount > 0
    except ValueError:
        print("False 2")
        return False

def listen_for_messages(sock, blockchain_file):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("Server connection closed.")
                break
            try:
                message = json.loads(data.decode())
                if 'payload' in message:
                    active_clients = message['payload']
                    print("Active Clients:")
                    for client_info in active_clients:
                        print(f" - IP: {client_info['IP']}, Port: {client_info['Port']}")
                    continue
            except json.JSONDecodeError:
                # Handle non-JSON messages or system commands
                if data == b'PING':
                    sock.sendall(b'PONG')
                else:
                    transaction = data.decode()
                    if transaction.endswith(client_id):
                        print(f"Ignoring transaction from self. Client ID: {client_id}, Transaction: {transaction}")
                        continue  # Ignore this transaction since it originated from this client
                    if verify_transaction(transaction):
                        print(f"Valid transaction received and writing to blockchain_file: {transaction}")
                        with open(blockchain_file, 'a') as file:
                            file.write(transaction + '\n')
                        print("Updated blockchain with new transaction:", transaction)
            except Exception as e:
                print(f"An error occurred when processing data: {e}")
                break
        except Exception as e:
            print(f"An error occurred: {e}")
            break



def send_commands(sock, blockchain_file):
    """
    Sends commands to a server and records transactions in a local ledger.

    Args:
        sock (socket.socket): The socket object used for communication with the server.
        blockchain_file (str): The file path to the local ledger.

    Returns:
        None
    """
    client_id = str(uuid.uuid4())  # Unique identifier for this client session
    while True:
        command = input("Enter command (send/request/attendance/exit): ").strip().lower()
        if command == 'exit':
            print("Exiting...")
            sock.close()
            break
        elif command.startswith('send') or command.startswith('request'):
            try:
                recipient_id, amount = input("Enter recipient ID and amount: ").split()
                transaction = f"{command} {recipient_id} {amount} {client_id}"
                message = transaction.encode()
                sock.sendall(message)
                
                # Immediately write the transaction to the local ledger
                with open(blockchain_file, 'a') as file:
                    file.write(transaction + '\n')
                
                print(f"Command '{command}' sent to server and recorded in ledger.")
            except ValueError:
                print("Invalid input. Please enter both recipient ID and amount.")
        elif command == 'attendance':
            msg = json.dumps({'msg_type': 'attendance request', 'payload': None}).encode()
            sock.sendall(msg)
            print("Attendance request sent to server.")
        else:
            print("Unknown command.")



def client_process(server_host, server_port, blockchain_file):
    """
    Connects to a server at the specified host and port, and performs client operations.

    Args:
        server_host (str): The IP address or hostname of the server.
        server_port (int): The port number of the server.
        blockchain_file (str): The path to the blockchain file.

    Returns:
        None

    Raises:
        Exception: If an error occurs during the connection or execution of client operations.
    """
    print("In the client_process function")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            print(f"Connecting to server at {server_host}:{server_port}...")
            s.connect((server_host, server_port))
            print(f"Connected to server at {server_host}:{server_port}")

            # Pass blockchain_file to the listening thread
            threading.Thread(target=listen_for_messages, args=(s, blockchain_file), daemon=True).start()
            send_commands(s, blockchain_file)

        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == '__main__':
    print("Starting client process...")
    if len(sys.argv) != 4:
        print("Usage: python client_script.py <server_host> <server_port> <blockchain_file>")
        sys.exit(1)
    server_host = sys.argv[1]
    server_port = int(sys.argv[2])
    blockchain_file = sys.argv[3]
    client_process(server_host, server_port, blockchain_file)
