import logging
from flask import Flask, jsonify, request, render_template, abort
from node import Node
from collections import deque
from bank import Transaction
import socket
import random
import string

# Initialize in-memory log storage
logs = deque(maxlen=100)  # Store up to 100 logs

# Initialize Node with tracker details
app = Flask(__name__)

# Set up logging with level INFO
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create a custom log handler
class InMemoryLogHandler(logging.Handler):
    def emit(self, record):
        logs.append(self.format(record))
        pass

# Add the custom handler to the logger
handler = InMemoryLogHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Function to find a free port
def find_free_port(start_port=50000, end_port=60000):
    for port in range(start_port, end_port + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("", port))
                return port
            except OSError:
                continue
    raise RuntimeError(f"No available ports in the range {start_port}-{end_port}")

@app.before_request
def log_request_info():
    logger.info('Request method: %s', request.method)
    logger.info('Request URL: %s', request.url)
    #logger.info('Request headers: %s', request.headers)
    logger.info(f'Request data: %s', request.get_data())

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    logger.info(f'Response status code: %s\n', response.status_code)
    return response

@app.errorhandler(Exception)
def handle_exception(e):
    logger.exception('An error occurred:')
    return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/')
def index():
    node_ip = node.address  # Get the node's IP address
    node_port = receiver_port  # Assuming `tracker_port` is the port you want to display
    print("Node IP:", node_ip)  # Debug print statement
    print("Node Port:", node_port)  # Debug print statement
    return render_template('index.html', node_ip=node_ip, node_port=node_port)

@app.route('/logs', methods=['GET'])
def get_logs():
    return jsonify(list(logs)), 200


@app.route('/balance', methods=['GET', 'OPTIONS'])
def get_balance():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        logger.info("Fetching balance")
        return jsonify({'balance': node.balance}), 200
    except AttributeError as e:
        logger.error(f"Error fetching balance: {str(e)}")
        return jsonify({'error': f'Failed to retrieve balance: {str(e)}'}), 500
    
@app.route('/status', methods=['GET', 'OPTIONS'])
def get_node_status():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        logger.info("Fetching node status")
        return jsonify({'active': node.active}), 200
    except Exception as e:
        logger.exception("Error fetching node status:")
        abort(500, description=str(e))

@app.route('/transaction', methods=['POST', 'OPTIONS'])
def send_transaction():
    if request.method == 'OPTIONS':
        return '', 200
    if not node or not node.active:
        abort(503, description="Service unavailable. Node is not initialized.")

    data = request.get_json()
    try:
        recipient_ip = data['recipient_ip']  # Correct key name
        amount = int(data['amount'])
        if amount <= 0:
            abort(400, description="Invalid amount. Must be greater than zero.")
        if amount*1.1 > node.balance:
            abort(400, description="Insufficient balance.")

        # Find the recipient node info from the attendance list
        all_nodes = node.request_attendance()
        recipient = next((n for n in all_nodes if n['IP'] == recipient_ip), None)
        if not recipient:
            abort(400, description="Recipient not found or not available.")

        # Create a transaction
        recipient_port = recipient['Port']
        transaction = Transaction(amount, node.address, recipient_port ) # Corrected to use `Transaction` object
        node.transaction_queue.put(transaction)

        # Broadcast transaction
        node.broadcast(all_nodes, {'msg_type': "transaction broadcast", "payload": transaction.__dict__})

        logger.info(f"Transaction sent to {recipient_ip} for amount {amount}")
        return jsonify(transaction.__dict__), 201
    except (KeyError, TypeError, ValueError) as e:
        logger.error(f"Bad request: {str(e)}")
        abort(400, description=f"Bad request: {str(e)}")


@app.route('/active_nodes', methods=['GET', 'OPTIONS'])
def get_active_nodes():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        logger.info("Fetching active nodes")
        active_nodes = node.request_attendance()
        return jsonify({'active_nodes': active_nodes}), 200
    except Exception as e:
        logger.exception("Error fetching active nodes:")
        abort(500, description=str(e))

def shutdown_server():
    # Shut down Flask application
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/disconnect', methods=['POST', 'OPTIONS'])
def handle_disconnect():
    if request.method == 'OPTIONS':
        return '', 200
    if not node or not node.active:
        abort(400, description='Node is not active or not initialized')

    node.active = False
    node.close_tracker_connection()
    # Shut down Flask application
    #shutdown_server()
    logger.info('Node disconnected successfully')
    return jsonify({'message': 'Node disconnected successfully'})

@app.route('/connect_node', methods=['POST', 'OPTIONS'])
def connect_node():
    if request.method == 'OPTIONS':
        return '', 200
    data = request.get_json()
    address = data.get('address')
    port = int(data.get('port'))
    try:
        node2 = Node(receiver_port, tracker_address, tracker_port)
        node2.notify_existence(receiver_port)  # Notify tracker when Flask app starts, if required
        if node2:
            logger.info(f'Node connected on :{random_name}:{port} successfully')
            return jsonify({'message': f'Node connected to {random_name}: {tracker_address}:{tracker_port} successfully'}), 200
    except Exception as e:
        logger.error(f"Failed to connect to node: {str(e)}")
        return jsonify({'error': f'Failed to connect to node: {str(e)}'}), 500

@app.route('/reconnect_node', methods=['POST', 'OPTIONS'])
def reconnect_node():
    if request.method == 'OPTIONS':
        return '', 200
    if node.active:
        return jsonify({'message': 'Node is already connected'}), 200
    
    try:
        # Re-initialize server socket or other necessary services
        if not node.server.is_alive():
            node.server_socket(node.port)  # Restart the server socket if not running
        node.active = True
        node.notify_existence(node.port)  # Crucial to let the network know this node is active again
        logger.info('Node reconnected successfully')
        return jsonify({'message': 'Node reconnected successfully'}), 200
    except Exception as e:
        node.active = False
        logger.error(f"Failed to reconnect node: {str(e)}")
        return jsonify({'error': f'Failed to reconnect node: {str(e)}'}), 500


def notify_tracker():
    try:
        node.notify_existence(node.port)
        print("Node has successfully notified tracker of its existence.")
    except Exception as e:
        print(f"Failed to notify tracker: {e}")

if __name__ == '__main__': 
    # Initialize the Node object
    tracker_address = input(f"Enter tracker address: Y (Enter tracker address) or N (default is 35.222.131.246) or local (default is 127.0.0.1)):\n")

    if tracker_address == "Y":
        tracker_address = input("Enter tracker address: ")
    elif tracker_address == "local":
        tracker_address = '127.0.0.1'
    else:
        tracker_address = tracker_address = '35.222.131.246'  
    
    #random_name = generate_random_string(10)
    #tracker_address = '35.222.131.246'  

    tracker_port = input(f"Enter tracker port: Y (Enter tracker port) or N (default is 50007) or local (default is 50007):\n")
    if tracker_port == "Y":
        tracker_port = input("Enter tracker port: ")
    elif tracker_port == "local" or tracker_port =="N":
        tracker_port = 50007
    else:
        tracker_port = int(tracker_port)

    tracker_port = 50007
    receiver_port = find_free_port()  # Find a free port
    node = Node(receiver_port, tracker_address, tracker_port)
    node.notify_existence(receiver_port)  # Notify tracker when Flask app starts, if required

    # Start the Flask application
    app.run(debug=True, port=5005, host='0.0.0.0', use_reloader=False)
