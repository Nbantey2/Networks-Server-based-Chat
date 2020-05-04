# Networks-Server-based-Chat

## Goals
* Create a server that can communicate with multiple clients and faciliate a chat between them. You can start a chat with someone and all your messages will go to that user.

## Server.py
* Creates a socket and bind it so that the operating system knows that it is going to use the given IP and port. Makes the socket listen for new connections and create a list of clients which will be filled later. The receive message function first reads the header, accepts the socket, saves the clientID and clientID header. There is code to verify if the client is in the subscriber list and perform the authentication and encryption with the specified algorithm.

## Client.py
* The client also performs the socket creation and is able to record and send mesages from the user to the server.
