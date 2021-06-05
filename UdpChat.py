import socket
from datetime import datetime as dt
import threading
import sys, os
import json
import time

IP = socket.gethostbyname(socket.gethostname())

class Server:
    global IP

    def __init__(self, port):
        self.host = IP
        self.port = int(port)
        self.socket = None
        self.client_table = {}
        self.isACKed = True

    def print_line(self, msg):
        time = dt.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f'[{time}]  {msg}')

    def create_and_bind(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))
        self.print_line(f'server started successfully @ {self.host} '
                        f'listening on port {self.port}')

    def broadcast_table(self):
        table = 'UPDATE ' + json.dumps(self.client_table)
        for name in self.client_table:
            if self.client_table[name][1]:
                self.socket.sendto(table.encode(), self.client_table[name][0])

    def send_error(self, address, error):
        self.socket.sendto(error.encode(), address)

    def send_ping(self, address):
        self.isACKed = False
        self.socket.sendto('PING'.encode(), address)
        time.sleep(0.5)

    def send_and_clear(self, name, to_address):
        self.print_line(f'Transmitting offline chat history for client {name}')
        self.socket.sendto('CHAT You Have Messages'.encode(), to_address)
        chat = open(f'{name}.txt', 'r')
        records = chat.readlines()
        i = 0
        for lines in records:
            self.socket.sendto(f'CHAT {lines}'.encode(), to_address)
            i += 1
        chat.close()
        self.print_line(f'Transmitting finished with {i} lines sent to {name}, deleting chat history')
        os.remove(f'{name}.txt')

    def process_request(self, request_data, request_source):
        command = request_data.split()[0]
        content = ' '.join(request_data.split()[1:])

        if command == 'TEST':
            self.print_line(f'message received: {content} from {request_source}')
            self.socket.sendto('test success!'.encode(), request_source)

        elif command == 'REG':
            if os.path.exists(f'{content}.txt'):
                self.send_and_clear(content, request_source)
            self.print_line(f'REG new client {content} at {request_source}')
            self.client_table[content] = [request_source, True]
            self.broadcast_table()

        elif command == 'CHECK':
            all_names = ''
            for name in self.client_table.keys():
                all_names += name + ' '
            all_names = 'CHECK ' + all_names
            self.socket.sendto(all_names.encode(), request_source)
            self.socket.sendto('ACK'.encode(), request_source)

        elif command == 'DEREG':
            self.print_line(f'DEREG client {content} at {request_source}')
            self.client_table[content][1] = False
            self.socket.sendto('ACK'.encode(), request_source)
            self.broadcast_table()

        elif command == 'SAVE-MESSAGE':
            recipient = content.split()[0]
            recipient_address = self.client_table[recipient][0]
            msg = ' '.join(content.split()[1:])
            self.send_ping(recipient_address)
            if self.isACKed:
                self.send_error(request_source, f'ERROR [Client {recipient} exists!!]')
                self.broadcast_table()
            else:
                self.client_table[recipient][1] = False
                self.broadcast_table()
                if os.path.exists(f'{recipient}.txt'):
                    f = open(f'{recipient}.txt', "a")
                    time = dt.now().strftime('%Y-%m-%d %H:%M:%S')
                    f.write(f"At {time} {msg}\n")
                    f.close()
                else:
                    f = open(f'{recipient}.txt', "w")
                    time = dt.now().strftime('%Y-%m-%d %H:%M:%S')
                    f.write(f"At {time} {msg}\n")
                    f.close()
                self.socket.sendto('SAVE-ACK'.encode(), request_source)

        elif command == 'ACK':
            self.isACKed = True

    def listen_to_request(self):
        try:
            while 1:
                data, client_address = self.socket.recvfrom(2048)
                data = data.decode('utf-8')
                threading.Thread(target=self.process_request, args=[data, client_address]).start()
        except KeyboardInterrupt:
            self.socket.close()


class Client:
    global IP

    def __init__(self, name, serverIP, serverPort, clientPort):
        self.name = name
        self.takenNames = []
        self.serverIP = serverIP
        self.serverPort = int(serverPort)
        self.clientPort = int(clientPort)
        self.socket = None
        self.client_table = {}
        self.isRegistered = False
        self.isOnline = True
        self.isACKed = True
        self.isError = False
        self.error = ''

    def print_line(self, msg):
        time = dt.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f'[{time}]  {msg}')

    def create_and_bind(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.serverIP, self.clientPort))

    def register(self):
        self.socket.sendto('CHECK'.encode(), (self.serverIP, self.serverPort))
        self.isACKed = False
        time.sleep(0.5)
        if self.isACKed:

            if self.name in self.takenNames:
                self.print_line('Cannot register with a duplicate name')
                os._exit(1)
            else:
                self.socket.sendto(f'REG {self.name}'.encode(), (self.serverIP, self.serverPort))
                self.print_line(f'[Welcome, {self.name}! You are now successfully registered.]')
                self.isRegistered = True
        else:
            self.print_line('Cannot register: Server not responding')
            os._exit(1)

    def send_offline(self, recipient, msg):
        self.socket.sendto(f'SAVE-MESSAGE {recipient} {msg}'.encode(), (self.serverIP, self.serverPort))
        self.isACKed = False
        time.sleep(0.8)
        if self.isACKed:
            self.print_line(f'[Client {recipient} is offline. Messages received by the server and saved]')
        else:
            if self.isError:
                self.print_line(self.error)
                self.isACKed = True
                self.isError = False
            else:
                self.print_line('[Messages not saved: server not responding]')

    def get_command(self):
        while 1:

            command = input('>>> ')
            if not command:
                continue
            command_header = command.split()[0]

            if command_header == 'test':
                self.print_line(f'success! {self.name} {self.serverIP} {self.serverPort} {self.clientPort}')

            elif command_header.lower() == 'testserver':
                self.socket.sendto('TEST hello world'.encode(), (self.serverIP, self.serverPort))

            elif command_header.lower() == 'reg':
                if self.isRegistered:
                    self.print_line('You are already registered!')
                    continue
                else:
                    self.socket.sendto(f'REG {self.name}'.encode(), (self.serverIP, self.serverPort))
                    self.print_line(f'[Welcome, {self.name}! You are now successfully registered.]')
                    self.isRegistered = True
                    self.isOnline = True

            elif command_header.lower() == 'send':
                try:
                    recipient_name = command.split()[1]
                    recipient_address = tuple(self.client_table[recipient_name][0])
                    msg = ' '.join(command.split()[2:])
                    if not self.client_table[recipient_name][1]:
                        self.send_offline(recipient_name, f'{self.name} says: {msg}')
                    else:
                        self.socket.sendto(f'MESSAGE {self.name} says: {msg}'.encode(), recipient_address)
                        self.isACKed = False
                        time.sleep(0.5)
                        if self.isACKed:
                            self.print_line(f'[Message received by {recipient_name}.]')
                        else:
                            self.print_line(f'[No ACK from {recipient_name}, message sent to server.]')
                            self.send_offline(recipient_name, f'{self.name} says: {msg}')
                except KeyError:
                    self.print_line(f'Client {recipient_name} not found')
                    continue

            elif command_header.lower() == 'dereg':
                self.isOnline = False
                self.socket.sendto(f'DEREG {self.name}'.encode(), (self.serverIP, self.serverPort))
                self.isACKed = False
                time.sleep(0.5)
                if not self.isACKed:
                    for i in range(0, 5):
                        self.print_line(f'[Resending DEREG request No. {i + 1}]')
                        self.socket.sendto('DEREG'.encode(), (self.serverIP, self.serverPort))
                        time.sleep(0.5)
                        if self.isACKed:
                            break
                if self.isACKed:
                    self.print_line('[You are Offline. Bye.]')
                    self.isRegistered = False
                else:
                    self.print_line('[Server not responding]')
                    self.print_line('[Exiting]')
                    os._exit(1)

    def process_msg(self, msg, msg_source):
        header = msg.split()[0]
        content = ' '.join(msg.split()[1:])

        if header == 'CHECK':
            self.takenNames = msg.split()[1:]
        if header == 'UPDATE':
            new_table = json.loads(content)
            if self.client_table != new_table:
                self.client_table = new_table
                self.print_line('[Client table updated.]')
        if header == 'MESSAGE':
            self.print_line(content)
            self.socket.sendto('ACK'.encode(), msg_source)
        if header == 'ACK':
            self.isACKed = True
        if header == 'SAVE-ACK':
            self.isACKed = True
        if header == 'ERROR':
            self.error = content
            self.isError = True
        if header == 'PING':
            if self.isOnline:
                self.socket.sendto('ACK'.encode(), msg_source)
        if header == 'CHAT':
            msg = ' '.join(msg.split()[1:])
            print(msg)

    def listen_to_message(self):
        while 1:
            data, address = self.socket.recvfrom(2048)
            data = data.decode('utf-8')
            thread = threading.Thread(target=self.process_msg, args=[data, address])
            thread.start()


if __name__ == '__main__':

    if len(sys.argv) == 1:
        print('Please provide the necessary arguments. If running as a server, provide -s <port>. If running as a client, '
              'provide -c <nick-name> <server-ip> <server-port> <client-port>')

    elif sys.argv[1] == '-s':
        try:
            server = Server(sys.argv[2])
            server.create_and_bind()
            server.listen_to_request()
        except:
            print('Please format your command as -s <port> and make sure the port number is correct')

    elif sys.argv[1] == '-c':
        try:

            client = Client(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
            client.create_and_bind()

            l = threading.Thread(target=client.listen_to_message)
            l.daemon = True
            l.start()

            client.register()

            try:
                client.get_command()
            except KeyboardInterrupt:
                client.print_line('Connection terminated')
                os._exit(1)
        except:
            print('Please format your command as -c <nick-name> <server-ip> <server-port> <client-port>')

    else:
        print('Please specify the correct running mode: -s for server and -c for client')
