import socket
import threading
import matplotlib.pyplot as plt
import sys
class LoadBalancer:
    def __init__(self, backend_servers):
        self.backend_servers = backend_servers
        print(f"[*] Backend servers: {self.backend_servers}")
        self.current_server = 0
        self.lock = threading.Lock()
        self.request_counts = {server: 0 for server in backend_servers}
        self.connections = {server: 0 for server in backend_servers}
        self.fig, self.ax = plt.subplots()
        self.ax.set_xlabel('Backend Server Port')
        self.ax.set_ylabel('Number of Requests')
        self.ax.set_title('Real-Time Request Distribution')
        plt.ion()  # Turn on interactive mode

    def get_server_round_robin(self):
        with self.lock:

            server = self.backend_servers[self.current_server]
            self.current_server = (
                self.current_server + 1) % len(self.backend_servers)
            self.request_counts[server] += 1  # Track requests per server

        return server
    def update_plot(self):
        servers = [f"{server[1]}" for server in self.backend_servers]
        counts = [self.request_counts[server]
                  for server in self.backend_servers]

        self.ax.clear()
        self.ax.bar(servers, counts, color='blue')
        self.ax.set_xlabel('Backend Server Port')
        self.ax.set_ylabel('Number of Requests')
        self.ax.set_title('Real-Time Request Distribution')
        plt.draw()
        plt.pause(0.1)  # Adjust the pause for smoother animation

    def get_server_least_connections(self, connections):
        with self.lock:
            # Find the server with the fewest active connections
            server = min(self.backend_servers, key=lambda s: self.connections[s])
            # Increment the connection count for that server
            self.connections[server] += 1
            # Increment the request count for that server for visualization purposes
            self.request_counts[server] += 1
        return server

    def forward_request(self, client_socket, server_address):
        try:
            # Establish connection to the backend server
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.connect(server_address)

            # Forward client's request to the server
            request = client_socket.recv(4096)
            server_socket.send(request)

            # Receive server's response and send it back to the client
            response = server_socket.recv(4096)
            client_socket.send(response)

        finally:
            server_socket.close()
            client_socket.close()
            with self.lock:
                self.connections[server_address] -= 1

    def handle_client(self, client_socket, algorithm, connections):
        if algorithm == "round_robin":
            server_address = self.get_server_round_robin()
        elif algorithm == "least_connections":
            server_address = self.get_server_least_connections(connections)
            connections[server_address] = connections.get(
                server_address, 0) + 1
        else:
            server_address = self.get_server_round_robin()  # default to round-robin

        self.forward_request(client_socket, server_address)

    def start(self, host="localhost", port=8001, algorithm="round_robin"):
        print(f"[*] Load Balancer started on {host}:{port}")
        connections = {}
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host, port))
        server_socket.listen(5)

        while True:
            client_socket, addr = server_socket.accept()
            print(f"[*] Accepted connection from {addr}")
            client_handler = threading.Thread(
                target=self.handle_client,
                args=(client_socket, algorithm, connections)
            )
            client_handler.start()
            self.update_plot()



if __name__ == "__main__":
    i=0
    backend_servers = []
    for args in sys.argv:
        if i>0:
            backend_servers.append(("localhost", int(args)))
        i+=1
    lb = LoadBalancer(backend_servers)
    lb.start(algorithm="least_connections")
