from socket import *
from routes.api import users, chat_sessions, online_user
import socket
import base64
import hashlib
import threading

server_ip = "127.0.0.1"
server_port = 8000
max_conn = 10
clients = {}


def get_headers(data):
    header_dict = {}
    data = str(data, encoding='utf-8')
    header, body = data.split('\r\n\r\n', 1)
    header_list = header.split('\r\n')
    for i in range(0, len(header_list)):
        if i == 0:
            if len(header_list[i].split(' ')) == 3:
                header_dict['method'], header_dict['url'], header_dict['protocol'] = header_list[i].split(' ')
        else:
            k, v = header_list[i].split(':', 1)
            header_dict[k] = v.strip()
    return header_dict


def broadcast(session_id, message):
    for key in clients.keys():
        return


class ClientThread(threading.Thread):
    def __init__(self, client, address):
        super(ClientThread, self).__init__()
        self.client = client
        self.address = address

    def run(self):
        data = self.client.recv(1024)
        headers = get_headers(data)
        print(headers)
        username = headers['username']
        token = 'a'
        res_header = "HTTP/1.1 101 Switching Protocols\r\n" \
                     "Upgrade:websocket\r\n" \
                     "Connection: Upgrade\r\n" \
                     "Sec-WebSocket-Accept: %s\r\n" % token
        #
        self.client.send(bytes(res_header, encoding='utf-8'))
        while 1:
            try:
                data = self.client.recv(1024)
            except socket.error:
                clients.pop(self.address)
                online_user.remove(username)
                break
            headers = get_headers(data)
            print(headers)
            session_id = headers['sessionId']


class ChatServer(threading.Thread):
    def __init__(self, ip='127.0.0.1', port=8088):
        super(ChatServer, self).__init__()
        self.addr = (ip, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        self.sock.bind(self.addr)
        self.sock.listen()
        print("Socket server is listening on ", self.addr)
        while True:
            client, address = self.sock.accept()
            clients[address] = client
            client_thread = ClientThread(client, address)
            client_thread.start()

    def stop(self):
        for s in clients.values():
            s.close()
        self.sock.close()
