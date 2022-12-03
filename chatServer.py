from socket import *
from routes.api import users, chat_sessions, online_user
import socket
import base64
import hashlib
import threading
import json
import pymongo

server_ip = "127.0.0.1"
server_port = 8000
max_conn = 10
global_clients = {"clients": [], "addresses": []}

client = pymongo.MongoClient("localhost", 27017) # use this to connect to mongodb
mongo = client["chatApp"]
# test database connectivity
try:
    print(client.server_info())
except Exception:
    print("Unable to connect to mongodb")
users = mongo['user']
chat_sessions = mongo['chatSession']


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

def send_msg(conn, msg_bytes):
    import struct
    token = b"\x81"
    length = len(msg_bytes)
    if length < 126:
        token += struct.pack("B", length)
    elif length <= 0xFFFF:
        token += struct.pack("!BH", 126, length)
    else:
        token += struct.pack("!BQ", 127, length)
    msg = token + msg_bytes
    conn.send(msg)
    return True

def broadcast(session_id, user, message):
    print('clients:', global_clients)
    if session_id == 'global':
        for client in global_clients['clients']:
            send_msg(client, bytes(user+': '+message, encoding='utf-8'))
    else:
        broadcast_in_session(session_id, message) # this part not done
        
def broadcast_in_session(session_id, user, message): # this function not done
    for value in global_clients.values():
        print(value)
        username = value['username']
        user = users.find_one({'username': username})

"""class SessionInfo():
    def __init__(self, sessionId):
        self.sessionId = sessionId
        self.clients = {"clients": [], "addresses": []}

    def add_client(self, client, address):
        self.clients['clients'].append(client)
        self.clients['addresses'].append(address)
    
    def remove_client(self, client, address):
        self.clients['clients'].remove(client)
        self.clients['addresses'].remove(address)"""

class ClientThread(threading.Thread):
    def __init__(self, client, address):
        super(ClientThread, self).__init__()
        self.client = client
        self.address = address

    def run(self):
        print("new client joined")
        data = self.client.recv(1024)
        headers = get_headers(data)
        print(headers)
        response_tpl = "HTTP/1.1 101 Switching Protocols\r\n" \
                     "Upgrade:websocket\r\n" \
                     "Connection: Upgrade\r\n" \
                     "Sec-WebSocket-Accept: %s\r\n" \
                     "WebSocket-Location: ws://%s%s\r\n\r\n"
        magic_string = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        value = headers['Sec-WebSocket-Key'] + magic_string
        ac = base64.b64encode(hashlib.sha1(value.encode('utf-8')).digest())
        response_str = response_tpl % (ac.decode('utf-8'), headers['Host'], headers['url'])
        self.client.send(bytes(response_str, encoding='utf-8')) # build connection
        print('glob clients:', global_clients)
        # start listening
        while 1:
            try:
                info = self.client.recv(8096)
            except Exception as e:
                info = None
            if not info:
                break
            payload_len = info[1] & 127
            if payload_len == 126:
                extend_payload_len = info[2:4]
                mask = info[4:8]
                decoded = info[8:]
            elif payload_len == 127:
                extend_payload_len = info[2:10]
                mask = info[10:14]
                decoded = info[14:]
            else:
                extend_payload_len = None
                mask = info[2:6]
                decoded = info[6:]
            bytes_list = bytearray()
            for i in range(len(decoded)):
                chunk = decoded[i] ^ mask[i % 4]
                bytes_list.append(chunk)
            body = str(bytes_list, encoding='utf-8')
            body = json.loads(body)
            print(body)
            broadcast(body['sessionId'], body['user'], body['message'])
    
    def process_login(self, body):
        if (body['username'] == 'alice' and body['password'] == 'abc'):
            send_msg(self.client, bytes('200', encoding='utf-8'))
        else: 
            send_msg(self.client, bytes('Wrong credentials', encoding='utf-8'))

    def process_post(self, body):
        return None

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
            print('addr:', address)
            global_clients['clients'].append(client)
            global_clients['addresses'].append(address)
            client_thread = ClientThread(client, address)
            client_thread.start()

    def stop(self):
        for s in global_clients.values():
            s.close()
        self.sock.close()
