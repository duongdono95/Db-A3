import socket
import threading

commands = ["close", "input", "clear", "classify", "return", "quit", "shutdown"]

class ClientHandler(threading.Thread):
    def __init__(self, connection, address, server, shutdown_func):
        super().__init__()
        self.connection = connection
        self.address = address
        self.server = server
        self.shutdown_func = shutdown_func  # Store the shutdown function

    def run(self):
        print(f"server: got connection from client {self.address[0]}")
        self.connection.send("Server is ready...\n".encode())

        while True:
            try:
                command = self.connection.recv(1024).decode().strip().lower()
                if not command:
                    break
                if command == "input":
                    self.handleInput()
                elif command == "shutdown":
                    self.handleShutdown()
                    break
                elif command == "quit":
                    self.handleQuit()
                    break
                else:
                    self.connection.send("400 Command not valid.\n".encode())
            except ConnectionResetError:
                print(f"Client {self.address[0]} disconnected unexpectedly (ConnectionResetError).")
                break
        self.connection.close()
        print(f"Connection with client {self.address[0]} closed.")

    def handleInput(self):
        pass

    def handleQuit(self):
        print(f"{self.address[0]} requested to quit. Closing connection.")
        self.connection.send("200 OK\nConnection closed.".encode())

    def handleShutdown(self):
        print("Shutdown command received. Server is shutting down.")
        self.connection.send("200 OK\nServer is shutting down...\n".encode())
        self.shutdown_func()
        self.connection.close()

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = None

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print("\n===============================================")
        print(f"Server started on {self.host}:{self.port}")
        print("Waiting for connections...")
        print("===============================================\n")
        
        while True:
            try:
                connection, address = self.server_socket.accept()
                client_handler = ClientHandler(connection, address, self, self.shutdown_server)
                client_handler.start()
            except OSError:
                break 
        print("Server has been shut down.")

    def shutdown_server(self):
        print("Shutting down the server...")
        if self.server_socket:
            self.server_socket.close()

    def stop(self):
        if self.server_socket:
            self.server_socket.close()

if __name__ == "__main__":
    host = socket.gethostname()
    port = 5991
    server = Server(host, port)
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt detected. Shutting down the server...")
        server.shutdown_server()
    finally:
        server.stop()
        print("Server stopped.")
