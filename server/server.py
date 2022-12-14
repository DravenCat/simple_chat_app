import socket
import threading
import re

server_ip = "127.0.0.1"
server_port = 8000
max_connection = 10
charset = "utf-8"


def handle_connection(client):
    data = client.recv(1024).decode(charset)

    print("[*] Received: ")
    request_header_lines = data.splitlines()
    for line in request_header_lines:
        print(line)

    try:
        response_header = "HTTP/1.1 200 OK\r\n"
        response_header += "Content-Type: text/html\r\n"
        response_header += "\r\n"

        ret = re.match(r"[^/]+/(\S*)", request_header_lines[0])
        front_end_file = "../frontend/"
        if ret:
            front_end_file += ret.group(1)
            if front_end_file == "../frontend/":
                front_end_file += "index.html"

        f = open(front_end_file, "rb")
        response_body = f.read()
        f.close()

        client.send(response_header.encode(charset))
        client.send(response_body)
    except:
        response_headers = "HTTP/1.1 404 not found\r\n"
        response_headers += "\r\n"
        response_body = "Not found"
        response = response_headers + response_body
        client.send(response.encode(charset))
    client.close()


def main():
    # Set server type = TCP
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Reuse port
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((server_ip, server_port))
    server.listen(max_connection)
    print("Server is listening on %s:%d, accepting %d connections..." % (server_ip, server_port, 10))

    while True:
        client, addr = server.accept()
        print(">> Accept client connection from %s:%d" % (addr[0], addr[1]))

        client_handler = threading.Thread(target=handle_connection, args=(client,))
        client_handler.start()


if __name__ == '__main__':
    main()
