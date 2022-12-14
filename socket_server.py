import socket
import select

HEADER_LENGTH = 128

IP = socket.gethostbyname(socket.gethostname())
PORT = 1234

# Create a socket
# socket.AF_INET - address family, IPv4, some otehr possible are AF_INET6, AF_BLUETOOTH, AF_UNIX
# socket.SOCK_STREAM - TCP, conection-based, socket.SOCK_DGRAM - UDP, connectionless, datagrams, socket.SOCK_RAW - raw IP packets
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# SO_ - socket option
# SOL_ - socket option level
# Sets REUSEADDR (as a socket option) to 1 on socket
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind, so server informs operating system that it's going to use given IP and port
# For a server using 0.0.0.0 means to listen on all available interfaces, useful to connect locally to 127.0.0.1 and remotely to LAN interface IP
server_socket.bind((IP, PORT))

# This makes server listen to new connections
server_socket.listen()

# List of sockets for select.select()
sockets_list = [server_socket]

# List of connected clients - socket as a key, user header and name as data
clients = {}

# List of public keys - socket as a key, user header and name as data
keys = {}

print(f'Listening for connections on {IP}:{PORT}...')

# Handles message receiving
def receive_message(client_socket):

    try:

        # Receive our "header" containing message length, it's size is defined and constant
        message_header = client_socket.recv(HEADER_LENGTH)

        # If we received no data, client gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
        if not len(message_header):
            return False

        # Convert header to int value
        message_length = int(message_header.decode('utf-8').strip())

        # Getting message
        message = client_socket.recv(message_length).decode('utf-8')
        if ':>>>:' in message:
            message = message.split(':>>>:')
            message = {
                'header': message_header,
                'data': message[0].encode('utf-8'),
                'addressee': message[1]
            }
        else:
            message = {
                'header': message_header,
                'data': message.encode('utf-8')
            }
        return message

    except:
        return False

def update_users_status():
    
    for client_socket in clients:
        others_keys = {}
        for key in keys.keys():
            if clients[client_socket]['data'] != key:
                others_keys[key.decode("utf-8")] = keys[key]
        message = repr(others_keys).encode('utf-8')
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
        flag = '__flag__'.encode('utf-8')
        flag_header = f"{len(flag):<{HEADER_LENGTH}}".encode('utf-8')
        #print(message_header + message)
        client_socket.send(flag_header + flag + message_header + message)

while True:

    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
    
    for notified_socket in read_sockets:

        # If notified socket is a server socket - new connection, accept it
        if notified_socket == server_socket:

            # Accept new connection
            # That gives us new socket - client socket, connected to this given client only, it's unique for that client
            # The other returned object is ip/port set
            client_socket, client_address = server_socket.accept()

            # Client should send their name right away, receive it
            user = receive_message(client_socket)

            # If False - client disconnected before he sent his name
            if user is False:
                continue

            # Client should send their public key right away, receive it
            public_key = receive_message(client_socket)

            # If False - client disconnected before he sent his name
            if public_key is False:
                continue

            public_key = eval(public_key['data'])
            #print(f'PUBLIC KEY: {public_key}')

            # Add accepted socket to select.select() list
            sockets_list.append(client_socket)

            # Also save username and username header
            clients[client_socket] = user

            # Also save public key and username
            keys[user['data']] = public_key
            
            update_users_status()

            print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode('utf-8')))
            #print('\n', list(clients.values()))

        # Else existing socket is sending a message
        else:

            # Receive message
            message = receive_message(notified_socket)

            # If False, client disconnected, cleanup
            if message is False:
                print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))

                # Remove from list for public key
                keys.pop(clients[notified_socket]['data'])

                # Remove from list for socket.socket()
                sockets_list.remove(notified_socket)

                # Remove from our list of users
                del clients[notified_socket]

                update_users_status()

                continue

            # Get user by notified socket, so we will know who sent the message
            user = clients[notified_socket]


            print(f'Received message from {user["data"].decode("utf-8")}')

            # Iterate over connected clients and broadcast message
            for client_socket in clients:
                # But don't sent it to sender
                if clients[client_socket]['data'] == message['addressee'].encode('utf-8'):

                    # Send user and message (both with their headers)
                    # We are reusing here message header sent by sender, and saved username header send by user when he connected
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

    # It's not really necessary to have this, but will handle some socket exceptions just in case
    for notified_socket in exception_sockets:

        # Remove from list for socket.socket()
        sockets_list.remove(notified_socket)

        # Remove from our list of users
        del clients[notified_socket]