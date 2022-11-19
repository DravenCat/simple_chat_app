import socket
import threading

server_ip = "127.0.0.1"
server_port = 8000
max_connection = 10

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def main():
    server.bind((server_ip, server_port))
    server.listen(max_connection)
    print("Server is listening on %s:%d, accepting %d connections..." % (server_ip, server_port, 10))

    client, addr = server.accept()
    print("Client address:" , addr)

    data = b''
    while True:
        chunk = client.recv(1024)
        data += chunk
        if len(chunk) < 1024:
            break

    print("收到的信息：", data)

    # 向客户端返回数据
    client.sendall(b'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<h1>Hello World</h1>')
    # 关闭客户端
    client.close()
    server.close()


if __name__ == '__main__':
    main()
