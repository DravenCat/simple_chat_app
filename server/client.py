# TCPclient.py

import socket

host_ip = "127.0.0.1"
host_port = 8000
charset = "utf-8"


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host_ip, host_port))

    while True:
        data = input("type test message\r\n")
        if not data:
            break

        client.send(data.encode(charset))
        response = client.recv(1024)
        print(response)

    client.close()


if __name__ == '__main__':
    main()
