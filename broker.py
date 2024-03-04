# Server code
import socket
import threading
import sys 
import ssl
# Create a TCP/IP socket
try:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error as e:
    print(f"Failed to create socket. Error: {e}")
    sys.exit(1)

# Define the server address and port
server_address = ('localhost', 9999)
print('Starting up on {} port {}'.format(*server_address))

# Bind the socket to the server address and port
try:
    server_socket.bind(server_address)
except socket.error as e:
    print(f"Failed to bind socket. Error: {e}")
    sys.exit(1)

# Listen for incoming connections
server_socket.listen(1)
#wrapping the socket with ssl
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
try:
    context.load_cert_chain(certfile="C:\\Users\\Dipin\\Data Science\\mini project\\certificate.pem", keyfile="C:\\Users\\Dipin\\Data Science\\mini project\\key.pem")
    server_socket = context.wrap_socket(server_socket, server_side=True)
    print("Socket successfully wrapped with SSL")
except ssl.SSLError as e:
    print(f"Failed to wrap socket with SSL. Error: {e}")
    sys.exit(1)

# Initialize a dictionary to keep track of topics and their subscribers
topics = {}

def handle_client(connection, client_address):
    print('Connection from', client_address)

    while True:
        try:
            # Receive data from the client
            data = connection.recv(1024).decode('ascii').strip()
            command, *args = data.split(' ')
        except socket.error as e:
            print(f"Failed to receive data from {client_address}. Error: {e}")
            connection.close()
            return

        if command == 'SUBSCRIBE':
            for topic in args:
                if topic not in topics:
                    topics[topic] = []
                topics[topic].append(connection)
            connection.sendall(f'Subscribed to {", ".join(args)}'.encode('ascii'))
        elif command == 'UNSUBSCRIBE':
            for topic in args:
                if topic in topics and connection in topics[topic]:
                    topics[topic].remove(connection)
            connection.sendall(f'Unsubscribed from {", ".join(args)}'.encode('ascii'))
        elif command == 'PUBLISH':
            if len(args) < 2:
                raise ValueError('PUBLISH command requires a topic and a message')
            topic, message = args[0], ' '.join(args[1:])
            if topic in topics:
                for subscriber in topics[topic]:
                    try:
                        subscriber.sendall(f'{client_address[1]}: {message}'.encode('ascii'))
                    except socket.error as e:
                        print(f"Failed to send data to {client_address}. Error: {e}")
                        connection.close()
                        return
                    connection.sendall(f'Message published to {topic}'.encode('ascii'))
        else: 
            connection.sendall(b'Unknown Command')

while True:
    try:
        # Wait for a connection
        print('Waiting for a connection...')
        connection, client_address = server_socket.accept()
    except socket.error as e:
        print(f"Failed to accept connection. Error: {e}")
        continue

    # Start a new thread to handle the client
    threading.Thread(target=handle_client, args=(connection, client_address)).start()