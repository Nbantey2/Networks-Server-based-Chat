import socket
import select
import errno
import threading

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 1234
my_clientID = input("clientID: ")

# Create a socket
# socket.AF_INET - address family, IPv4, some otehr possible are AF_INET6, AF_BLUETOOTH, AF_UNIX
# socket.SOCK_STREAM - TCP, conection-based, socket.SOCK_DGRAM - UDP, connectionless, datagrams, socket.SOCK_RAW - raw IP packets
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to a given ip and port
client_socket.connect((IP, PORT))

# Set connection to non-blocking state, so .recv() call won;t block, just return some exception we'll handle
client_socket.setblocking(False)

# Prepare clientID and header and send them
# We need to encode clientID to bytes, then count number of bytes and prepare header of fixed size, that we encode to bytes as well
clientID = my_clientID.encode('utf-8')
clientID_header = f"{len(clientID):<{HEADER_LENGTH}}".encode('utf-8')
client_socket.send(clientID_header + clientID)

# Define a general function that loops, waiting to receive a message from the
# Server then process it
def receive_messages():
    while True:
        try:
            # Now we want to loop over received messages (there might be more than one) and print them
            while True:

                # Receive our "header" containing clientID length, it's size is defined and constant
                clientID_header = client_socket.recv(HEADER_LENGTH)

                # If we received no data, server gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
                if not len(clientID_header):
                    print('Connection closed by the server')
                    sys.exit()

                # Convert header to int value
                clientID_length = int(clientID_header.decode('utf-8').strip())

                # Receive and decode clientID
                clientID = client_socket.recv(clientID_length).decode('utf-8')

                # Now do the same for message (as we received clientID, we received whole message, there's no need to check if it has any length)
                message_header = client_socket.recv(HEADER_LENGTH)
                message_length = int(message_header.decode('utf-8').strip())
                message = client_socket.recv(message_length).decode('utf-8')

                # Print message
                print(f'{clientID} > {message}')

        except IOError as e:
            # This is normal on non blocking connections - when there are no incoming data error is going to be raised
            # Some operating systems will indicate that using AGAIN, and some using WOULDBLOCK error code
            # We are going to check for both - if one of them - that's expected, means no incoming data, continue as normal
            # If we got different error code - something happened
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error: {}'.format(str(e)))
                sys.exit()

            # We just did not receive anything
            continue

        except Exception as e:
            # Any other exception - something happened, exit
            print('Reading error: '.format(str(e)))
            sys.exit()

# Start the thread to receive messages
threading.Thread(target=receive_messages).start()

# Now that the receiving thread is running run a loop in the main thread to
# get input from the user and send it to the server
while True:
    # Wait for clientID to input a message
    message = input(f'{my_clientID} > ')

    # If message is not empty - send it
    if message:

        # Encode message to bytes, prepare header and convert to bytes, like for clientID above, then send
        message = message.encode('utf-8')
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(message_header + message)
        del message