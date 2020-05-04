import socket
import select
from random import randrange

HEADER_LENGTH = 10

IP = "127.0.0.1"
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

        # Return an object of message header and message data
        print('received message header ', message_header)
        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:

        # If we are here, client closed connection violently, for example by pressing ctrl+c on his script
        # or just lost his connection
        # socket.close() also invokes socket.shutdown(socket.SHUT_RDWR) what sends information about closing the socket (shutdown read/write)
        # and that's also a cause when we receive an empty message
        return False

while True:

    # Calls Unix select() system call or Windows select() WinSock call with three parameters:
    #   - rlist - sockets to be monitored for incoming data
    #   - wlist - sockets for data to be send to (checks if for example buffers are not full and socket is ready to send some data)
    #   - xlist - sockets to be monitored for exceptions (we want to monitor all sockets for errors, so we can use rlist)
    # Returns lists:
    #   - reading - sockets we received some data on (that way we don't have to check sockets manually)
    #   - writing - sockets ready for data to be send thru them
    #   - errors  - sockets with some exceptions
    # This is a blocking call, code execution will "wait" here and "get" notified in case any action should be taken
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)


    # Iterate over notified sockets
    for notified_socket in read_sockets:

        # If notified socket is a server socket - new connection, accept it
        if notified_socket == server_socket:

            # Accept new connection
            # That gives us new socket - client socket, connected to this given client only, it's unique for that client
            # The other returned object is ip/port set
            client_socket, client_address = server_socket.accept()

            # Client should send his name right away, receive it
            clientID = receive_message(client_socket)
            print('received header', clientID)

            # NEW ENCRYPTION/ AUTHENTICATION CODE STARTS, DELETE IF PROBLEMS ARE CAUSED
            client_key = clientID[0:2]

            # Authentication (must receive a HELLO from valid USER)
            # verify client in list
            user_accepted = False

            while not user_accepted:
                userIDfile = open("userlist.txt", "r").readlines()
                for line in userIDfile:
                    user_accepted = (line == clientID) or user_accepted
                if user_accepted:
                    client_socket.send("CHALLENGE, sending rand int")
                    random_int = randrange(999)
                else:
                    client_socket.send("AUTH_FAIL, closing connection")
                    client_socket.close();

            # Encryption Algo
            CK_A = hash(random_int + client_key)
            client_socket.send("AUTH_SUCCESS")
            # END OF NEW ENCRYPTION. AUTHENTICATION CODE

            # If False - client disconnected before he sent his name
            if clientID is False:
                continue

            # Add accepted socket to select.select() list
            sockets_list.append(client_socket)

            # Also save clientID and clientID header
            clients[client_socket] = {'clientID':clientID, 
                                      'status':'waiting',
                                      'chattingWith':''}

            print('Accepted new connection from {}:{}, clientID: {}'.format(*client_address, clientID['data'].decode('utf-8')))

        # Else existing socket is sending a message
        else:

            # Receive message
            message = receive_message(notified_socket)

            # If False, client disconnected, cleanup
            if message is False:
                print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))

                # Remove from list for socket.socket()
                sockets_list.remove(notified_socket)

                # Remove from our list of clientIDs
                del clients[notified_socket]

                continue

            # Get clientID by notified socket, so we will know who sent the message
            clientID = clients[notified_socket]['clientID']

            print(f'Received message from {clientID["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')

            # Okay, so at this point we have the server getting the message
            # that the user sends. Now we need to change what it does based on
            # that message and the user state
            # the message string is just message, the user state is 
            # clients[notified_socket]['status']

            userStatus = clients[notified_socket]['status']

            # assume that if chat is in the message then it's a request to start
            # a chat
            messageBody = message["data"].decode("utf-8")
            if "Chat" in messageBody and userStatus == 'waiting':
                # need to pull the user id
                targetID = messageBody.split()[1]
                print('targetid type: ', type(targetID))
                # print("received chat start with targetid ", targetID)
                for client in clients:
                    print(client.__getattribute__("clientID"))
                    # if clients[client]['clientID'] == targetID:
                    #     print('chained')
                    # print(client.__dict__.keys())
                    # if client.'userID' == targetID:
                    #     print('okay it kinda worked')
                    
                # else = the user is offline or otherwise unavailable
                else:
                    print('do this later 139')
                    # we need to send a message to the client that requested
                    # the chat saying that the invitation failed

            # Iterate over connected clients and broadcast message
            # for client_socket in clients:

            #     # But don't sent it to sender
            #     if client_socket != notified_socket:

            #         # Send clientID and message (both with their headers)
            #         # We are reusing here message header sent by sender, and saved clientID header send by clientID when he connected
            #         client_socket.send(clientID['header'] + clientID['data'] + message['header'] + message['data'])

    # It's not really necessary to have this, but will handle some socket exceptions just in case
    for notified_socket in exception_sockets:

        # Remove from list for socket.socket()
        sockets_list.remove(notified_socket)

        # Remove from our list of clientIDs
        del clients[notified_socket]