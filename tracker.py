import socket
import select
import time
import json
import sys


class Tracker:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.inputs = [self.server_socket]
        self.client_addresses = {}
        self.data_from_clients = {}
        self.last_broadcast_time = time.time()
        self.broadcast_interval = 10  # seconds

    def broadcast_transaction(self, data, sender_socket):
        transaction = data.decode()
        sender_id = transaction.split()[-1]
        print(f"Broadcasting transaction, excluding sender ID: {sender_id}")
        for client in self.inputs:
            if client is not self.server_socket and client != sender_socket:
                client.sendall(data)

    '''''
    def check_for_disconnections(self):
        for client in list(self.client_addresses.keys()):
            if client.fileno() == -1:  # Socket has been closed
                del self.client_addresses[client]
                print(f"Removed disconnected client: {client}")
    '''''
    
    def remove_client(self, client_socket):
        if client_socket in self.inputs:
            self.inputs.remove(client_socket)
            del self.client_addresses[client_socket]
            print(f"Removed client {client_socket.getpeername()} from the list of active clients.")
        else:
            print(f"Client {client_socket.getpeername()} not in list of active clients.")

    def attendance(self): # This is the new attendance method
        active_clients = [{"IP": info[0], "Port": info[1]} for info in self.client_addresses.values()]
    
        return active_clients
    


    '''' # This is the original attendance method
    def attendance(self):
        # Check which client sockets are ready to read without actually reading
        ready_to_read, _, _ = select.select(self.inputs, [], [], 0)
        active_clients = []
        for client in ready_to_read:
            if client is not self.server_socket:
                client_info = {
                    "IP": self.client_addresses[client][0],
                    "Port": self.client_addresses[client][1]
                }
                active_clients.append(client_info)
        return active_clients
        '''

    def handle_client_requests(self, client_socket):
        """
        Handle client requests and send appropriate responses.

        Args:
            client_socket (socket): The client socket to handle requests from.

        Raises:
            json.JSONDecodeError: If there is an error decoding JSON from the client.
            ConnectionError: If there is a connection error with the client socket.
        """
        try:
            data = client_socket.recv(5000).decode()
            if data:
                message = json.loads(data)
                print(f"Received message from client {client_socket.getpeername()}: {message}")  # Debug incoming message

                if message['msg_type'] == 'attendance request':
                    active_clients = self.attendance()
                    print(f"Active clients before sending: {active_clients}")  # Debug the list of active clients
                    response = json.dumps({'payload': active_clients}).encode()
                    print(f"Sending response to client {client_socket.getpeername()}: {response}")  # Debug the response being sent
                    client_socket.send(response)

                if message['msg_type'] == 'disconnect':
                    self.remove_client(client_socket)
                    print(f"Client {client_socket.getpeername()} disconnected.")
                    client_socket.close()
                   
                elif message['msg_type'] == 'existence notification':
                    client_IP = message['payload']['IP']
                    client_port = message['payload']['port']
                    self.client_addresses[client_socket] = (client_IP, client_port)  # set the client address
                    # print(f"Updated active nodes list: {self.client_addresses}")  # Debug the updated list of nodes

        except json.JSONDecodeError:
            print("Failed to decode JSON from client")
        except ConnectionResetError:
            print(f"Connection reset by {client_socket.getsockname()}")
            self.inputs.remove(client_socket)
            client_socket.close()
        except ConnectionError:
            print(f"Connection error with {client_socket.getsockname()}")

    def run(self):
        print("Tracker running and listening...")
        while True:
            readable, _, _ = select.select(self.inputs, [], [], 0.5)
            for s in readable:
                if s is self.server_socket:
                    client, address = s.accept()
                    print(f"Connected by {address}")
                    self.inputs.append(client)
                    # self.client_addresses[client] = address
                else:
                    self.handle_client_requests(s)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python tracker.py <port>")
        sys.exit(1)

    try:
        port = int(sys.argv[1])
    except ValueError:
        print("Please provide a valid integer for the port.")
        sys.exit(1)

    host = '0.0.0.0'
    tracker = Tracker(host, port)
    tracker.run()
