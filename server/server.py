from socket import *
import socket
import base64
import hashlib
import threading


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


class Chat:
    def __init__(self, ip='0.0.0.0', port=9999):
        self.addr = (ip, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.client = {}

    def start(self, ):
        self.sock.bind((self.addr))
        self.sock.listen()
        threading.Thread(target=self.accept, name='accept').start()

    def accept(self):
        while True:
            conn, address = self.sock.accept()
            self.client[address] = conn

            data = conn.recv(1024)
            headers = get_headers(data)
            response_tpl = "HTTP/1.1 101 Switching Protocols\r\n" \
                           "Upgrade:websocket\r\n" \
                           "Connection: Upgrade\r\n" \
                           "Sec-WebSocket-Accept: %s\r\n" \
                           "WebSocket-Location: ws://%s%s\r\n\r\n"
            magic_string = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
            value = headers['Sec-WebSocket-Key'] + magic_string
            ac = base64.b64encode(hashlib.sha1(value.encode('utf-8')).digest())
            response_str = response_tpl % (ac.decode('utf-8'), headers['Host'], headers['url'])
            conn.send(bytes(response_str, encoding='utf-8'))

            threading.Thread(target=self.recv, name='sock', args=(conn,)).start()

    def recv(self, sock):
        while 1:
            try:
                info = sock.recv(8096)
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
            for s in self.client.values():
                send_msg(s, bytes(body, encoding='utf-8'))

    def stop(self):
        for s in self.client.values():
            s.close()
        self.sock.close()


sc = Chat()
sc.start()
