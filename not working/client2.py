import socket
from base64 import b16encode

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(1)

user_ID = input("Enter User ID: > ")
user_ID = user_ID + "\n"
log_on_barrier = ""

# User types HELLO to server
while log_on_barrier != "Log on":
    log_on_barrier = input("Enter \"Log on\" > ")

# User gets CHALLENGE from server, or not if invalid ID
sock.sendto((user_ID.encode('utf-8')), ('127.0.0.1', 32002))
data, address = sock.recvfrom(1024)
data = data.decode('utf-8')
if data != "CHALLENGE":
    exit(1)

serv_resp = False
enc_key = ""
response = "RESPONSE"

# RESPONSE to server
sock.sendto(response.encode('utf-8'), ('127.0.0.1', 32002))
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

in_chat = False

while not in_chat:
    data = input("> ")
    if data == "Log off":   # user logs off by typing "Log off"
        sock.close()
        exit(0)
    if data == "Chat Client-ID-A":
        data = "CHAT_REQUEST"
        in_chat = True
        sock.sendto(data.encode('utf-8'), ('127.0.0.1', 32002))
        data, address = sock.recvfrom(1024)
        text = data.decode('utf-8')
        print(text)

while in_chat:
    data = input("> ")
    sock.sendto(data.encode('utf-8'), ('127.0.0.1', 32002))
    data, address = sock.recvfrom(1024)
    text = data.decode('utf-8')
    print(text)
