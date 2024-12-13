import sys
import socket
import time
import random
import threading
class BackendServer:
    def __init__(self, host="localhost", port=9001):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"[*] Backend Server started on {self.host}:{self.port}")

    def handle_client(self, client_socket):
        request = client_socket.recv(4096).decode()
        print(f"[*] Received request: {request}")

        time.sleep(random.randint(5, 12))
        response = f"HTTP/1.1 200 OK\n\nHello from server {self.port}"
        client_socket.send(response.encode())
        client_socket.close()

    def start(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"[*] Accepted connection from {addr}")
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()

if __name__ == "__main__":
    server = BackendServer(port=int(sys.argv[1]))
    server.start()
