# TCPclient.py

import socket

host_ip = "127.0.0.1"
host_port = 8000

while True:

    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    client.connect((host_ip, host_port))

    data = input(">")

    if not data:
        break

    client.send(data.encode())

    response = client.recv(1024)

    print(response)

client.close()