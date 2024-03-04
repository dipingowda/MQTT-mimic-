import socket
import threading
import ssl

# Create a TCP/IP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE
client_socket = context.wrap_socket(client_socket, server_hostname='localhost')

# Connect the socket to the server
server_address = ('localhost', 9999)
client_socket.connect(server_address)

def listen_for_messages():
    while True:
        # Receive the response from the server
        data = client_socket.recv(1024)
        print('Received:', data.decode('ascii'))
        
# Start a new thread to listen for messages
threading.Thread(target=listen_for_messages).start()

while True:
    # Send a command to the server
    command = input('turtle> ')
    if command.startswith('PUBLISH'):
        client_socket.sendall(command.encode('ascii'))
        break  # Close the connection after publishing a message
    else:
        client_socket.sendall(command.encode('ascii'))