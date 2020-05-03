import signal
import socket
import os
import time
from base64 import b16encode

# Lines 6 to 38 handle connecting Client A
sockA = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockA.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sockA.bind(('127.0.0.1', 32001))

# Authentication (must receive a HELLO from valid USER)
user_accepted = False

while not user_accepted:
    mag_bytes, address = sockA.recvfrom(1024)
    mag_str = mag_bytes.decode('utf-8')
    userIDfile = open("userlist.txt", "r").readlines()
    for line in userIDfile:
        user_accepted = (line == mag_str) or user_accepted
    if user_accepted:
        mag_str = "CHALLENGE"
    sockA.sendto(mag_str.encode('utf-8'), address)

# Response (must receive a RESPONSE from valid USER)
user_accepted = False
cka = ""
while not user_accepted:
    mag_bytes, address = sockA.recvfrom(1024)
    mag_str = mag_bytes.decode('utf-8')
    if mag_str == "RESPONSE":
        cka = os.urandom(16)
        sockA.sendto(cka, address)
        cka = b16encode(cka).decode('utf-8')
        user_accepted = True
    else:
        sockA.sendto("AUTH_FAIL".encode('utf-8'), address)

string = "CONNECTED"
sockA.sendto(string.encode('utf-8'), address)
address1 = address

# Lines 42 to 74 handle connecting Client B

sockB = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockB.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sockB.bind(('127.0.0.1', 32002))

# Authentication (must receive a HELLO from valid USER)
user_accepted = False

while not user_accepted:
    mag_bytes, address = sockB.recvfrom(1024)
    mag_str = mag_bytes.decode('utf-8')
    userIDfile = open("userlist.txt", "r").readlines()
    for line in userIDfile:
        user_accepted = (line == mag_str) or user_accepted
    if user_accepted:
        mag_str = "CHALLENGE"
    sockB.sendto(mag_str.encode('utf-8'), address)

# Response (must receive a RESPONSE from valid USER)
user_accepted = False
cka = ""
while not user_accepted:
    mag_bytes, address = sockB.recvfrom(1024)
    mag_str = mag_bytes.decode('utf-8')
    if mag_str == "RESPONSE":
        cka = os.urandom(16)
        sockB.sendto(cka, address)
        cka = b16encode(cka).decode('utf-8')
        user_accepted = True
    else:
        sockB.sendto("AUTH_FAIL".encode('utf-8'), address)

# Tell client B that they are connected
string = "CONNECTED"
sockB.sendto(string.encode('utf-8'), address)
address2 = address

# Send something to Client A to show that Client B is online
string = "Client B online"
sockA.sendto(string.encode('utf-8'), address1)

# Both clients are in server not talking to each other
chat_initiated = False
while not chat_initiated:
    try:
        mag_bytes, address = sockA.recvfrom(1024)
        mag_str = mag_bytes.decode('utf-8')
        print('Received from client A {} : {}'.format(address, mag_str))
        if mag_str == "CHAT_REQUEST":
            chat_initiated = True
            mag_str = "Chat started"
            sockA.sendto(mag_str.encode(), address)
    except socket.timeout:
        None

    try:
        mag_bytes, address = sockB.recvfrom(1024)
        mag_str = mag_bytes.decode('utf-8')
        print('Received from client B {} : {}'.format(address, mag_str))
        if mag_str == "CHAT_REQUEST":
            chat_initiated = True
            mag_str = "Chat started"
            sockB.sendto(mag_str.encode(), address)
    except socket.timeout:
        None

logged_out = False
while not logged_out:
    try:
        mag_bytes, address = sockB.recvfrom(1024)
        mag_str = mag_bytes.decode('utf-8')
        print('Client B: {}'.format(mag_str))
        if mag_str == "End chat":
            logged_out = True
            mag_str = "Chat ended"
        sockA.sendto(mag_str.encode(), address1)
    except socket.timeout:
        None

    if logged_out:
        break

    try:
        mag_bytes, address = sockA.recvfrom(1024)
        mag_str = mag_bytes.decode('utf-8')
        print('Client A: {}'.format(mag_str))
        if mag_str == "End chat":
            logged_out = True
            mag_str = "Chat ended"
        sockB.sendto(mag_str.encode(), address2)
    except socket.timeout:
        None
