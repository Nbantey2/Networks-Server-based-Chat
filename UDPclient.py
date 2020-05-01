import socket
from base64 import b16encode

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(1)

user_ID = input("Enter User ID: > ")
user_input = ""

# User types HELLO to server
while user_input != "HELLO ":
    user_input = input("Type HELLO to enter chat: > ")
    user_input = user_input + " "

# User gets CHALLENGE from server, or not if invalid ID
sock.sendto(user_input.encode('utf-8') + (user_ID.encode('utf-8')), ('127.0.0.1', 32001))
data, address = sock.recvfrom(1024)
data = data.decode('utf-8')
if data != "CHALLENGE":
    exit(0)

serv_resp = False
enc_key = ""

# User types RESPONSE to server
while not serv_resp:
    user_input = input("Authenticate yourself: > ")
    sock.sendto(user_input.encode('utf-8') + (user_ID.encode('utf-8')), ('127.0.0.1', 32001))
    data, address = sock.recvfrom(1024)
    if data == "AUTH_FAIL":
        print("AUTH_FAIL")
    else:
        cka = b16encode(data).decode('utf-8')
        serv_resp = True

# I will be honest, even though we generated a CKA, for the sake of this project, we are sticking
# with utp-8 because we really need to finish this project

# Right here is when the connection starts with the server
data, address = sock.recvfrom(1024)
print(data.decode('utf-8'))

while True:
    data = input("> ")
    sock.sendto(data.encode('utf-8'), ('127.0.0.1', 32001))
    data, address = sock.recvfrom(1024)
    print(address)
    text = data.decode('utf-8')
    print('Received from server %s : %s' % (address, text))
