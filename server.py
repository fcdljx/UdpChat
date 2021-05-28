import socket
import threading
import sys

IP = socket.gethostbyname(socket.gethostname())


def RunServer(PORT):
    global IP
    all_clients = {}

    # Create a UDP socket for the server
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the address to the server port
    server.bind((IP, PORT))

    print(f'server started successfully @ {IP} listening on port {PORT}')

    while True:

        data, addr = server.recvfrom(2048)


        print(data)
        print(addr)

        if not data:
            break


def RunClient(nickName, serverIP, serverPort, clientPort):
    all_client = {}

    # create client socket and bind
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clientSocket.bind((IP, clientPort))

    while True:
        command = input('>>> ')

        if command=='reg':
            #send the nickName to server for registration
            clientSocket.sendto(nickName.encode(), (serverIP, serverPort))

if __name__ == '__main__':
    if sys.argv[1] == 's':
        RunServer(int(sys.argv[2]))
    if sys.argv[1] == 'c':
        RunClient(sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]))
