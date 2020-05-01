import socket
import os
from base64 import b16encode

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('127.0.0.1', 32001))

# Authentication (must receive a HELLO from valid USER)
user_accepted = False
while not user_accepted:
    mag_bytes, address = sock.recvfrom(1024)
    mag_str = mag_bytes.decode('utf-8')
    userIDfile = open("userlist.txt", "r").readlines()
    message = " "
    for line in userIDfile:
        user_accepted = line == mag_str[6:]
    if user_accepted:
        mag_str = "CHALLENGE"
    sock.sendto(mag_str.encode('utf-8'), address)

# Response (must receive a RESPONSE from valid USER)
user_accepted = False
cka = ""
while not user_accepted:
    mag_bytes, address = sock.recvfrom(1024)
    mag_str = mag_bytes.decode('utf-8')
    if "RESPONSE" in mag_str:
        cka = os.urandom(16)
        sock.sendto(cka, address)
        cka = b16encode(cka).decode('utf-8')
        user_accepted = True
    else:
        sock.sendto("AUTH_FAIL".encode('utf-8'), address)

string = "CONNECTED"
sock.sendto(string.encode('utf-8'), address)

while True:
    mag_bytes, address = sock.recvfrom(1024)
    mag_str = mag_bytes.decode('utf-8')
    print('Received from client {} : {}'.format(address, mag_str))
    sock.sendto(mag_str.encode(), address)
