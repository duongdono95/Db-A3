"""
This module provides a multithreaded TCP server for handling client connections and classifying Iris flower data using a neural network model.
The server accepts a set of commands from clients to input, clear, classify, and return Iris flower measurements and classifications.

Classes:
    ClientHandler: Handles a single client connection, allowing clients to input flower measurements, request classifications, and retrieve data.
    Server: Manages server initialization, starts listening for incoming connections, and shuts down the server.

Modules:
    socket: Provides access to the BSD socket interface for communication between the server and clients.
    threading: Supports multithreading to allow handling of multiple clients concurrently.

Constants:
    commands (List[str]): List of valid command strings that the server can recognize.
    VARIABLE_RANGES (dict): Defines acceptable ranges for each measurement in the Iris flower dataset.

Classes:
    ClientHandler: Thread-based handler for client connections.
    Server: Main server class to start, run, and shut down the server.

"""

import socket
import threading

from IrisANN.TIris import TIris

# List of valid command strings the server recognizes and processes
commands = ["close", "input", "clear", "classify", "return", "quit", "shutdown"]

# Acceptable measurement ranges for Iris flower variables
VARIABLE_RANGES = {
    "sepallength": (4.3, 7.9),
    "sepalwidth": (2.0, 4.4),
    "petallength": (1.0, 6.9),
    "petalwidth": (0.1, 2.5),
}


class ClientHandler(threading.Thread):
    """
    Handles a single client connection and processes commands such as input, classify, clear, and return.

    Attributes:
        connection (socket.socket): The client connection socket.
        address (tuple): The client's address (IP, port).
        server (Server): A reference to the server for managing server-wide operations.
        shutdown_func (function): A function to trigger server shutdown.
        inputs (dict): Stores original and normalized values of Iris measurements for the client.
        outputs (list): Holds the model's classification result.
        model (TIris): An instance of the Iris classification model.

    Methods:
        run(): Listens for commands from the client and delegates processing to specific handlers.
        handleInput(command): Processes 'input' commands to store and normalize client-provided values.
        handleReturn(command): Processes 'return' commands to retrieve input/output data.
        handleClassify(): Processes 'classify' commands to perform classification on provided input data.
        handleClear(): Resets the client's inputs and outputs.
        handleClose(): Closes the connection with the client.
        handleQuit(): Ends the client's session with a quit message.
        handleShutdown(): Shuts down the server upon client request.
    """

    def __init__(self, connection, address, server, shutdown_func):
        super().__init__()
        self.connection = connection
        self.address = address
        self.server = server
        self.shutdown_func = shutdown_func
        self.inputs = {
            "sepallength": {"original": None, "normalized": None},
            "sepalwidth": {"original": None, "normalized": None},
            "petallength": {"original": None, "normalized": None},
            "petalwidth": {"original": None, "normalized": None},
        }
        self.outputs = None
        self.model = TIris()

    def run(self):
        """
        Main method to handle client communication. Listens for commands, processes each command, and handles exceptions.
        """
        print(f"server: got connection from client {self.address[0]}")
        self.connection.send("Server is ready...\nWelcome to the Iris Server".encode())

        while True:
            try:
                command = self.connection.recv(1024).decode().strip().lower()
                print("================================")
                print(f"Client: Requested to {command}")
                print("================================")
                if not command:
                    break
                # Command dispatch based on received command string
                if command.startswith("input"):
                    self.handleInput(command)
                elif command.startswith("return"):
                    self.handleReturn(command)
                elif command == "classify":
                    self.handleClassify()
                elif command == "clear":
                    self.handleClear()
                elif command == "close":
                    self.handleClose()
                    break
                elif command == "shutdown":
                    self.handleShutdown()
                    break
                elif command == "quit":
                    self.handleQuit()
                    break
                else:
                    self.connection.send("400 Command not valid.\n".encode())
            except ConnectionResetError:
                print(
                    f"Client {self.address[0]} disconnected unexpectedly (ConnectionResetError)."
                )
                break
        self.connection.close()
        print(f"Connection with client {self.address[0]} closed.")

    def handleInput(self, command):
        """
        Processes 'input' commands to receive a value for a specific variable, normalize it, and store it.

        Parameters:
            command (str): The command string received from the client.
        """
        try:
            _, var_name, value_str = command.split(maxsplit=2)
            if var_name not in VARIABLE_RANGES:
                self.connection.send("400 Error: Invalid variable name.\n".encode())
                return

            try:
                value = float(value_str)
                min_val, max_val = VARIABLE_RANGES[var_name]
                if min_val <= value <= max_val:
                    normalized_value = (value - min_val) / (max_val - min_val)
                    self.inputs[var_name] = {
                        "original": value,
                        "normalized": normalized_value,
                    }
                    self.connection.send("OK".encode())
                    print(f"Server: {var_name} - {value} - {normalized_value:.4f}")
                else:
                    self.connection.send("400 Error: Value out of range.\n".encode())
            except ValueError:
                self.connection.send("400 Error: Invalid value format.\n".encode())

        except ValueError:
            self.connection.send("400 Error: Invalid input format.\n".encode())

    def handleReturn(self, command):
        """
        Processes 'return' commands to provide input/output data to the client.

        Parameters:
            command (str): The command string received from the client.
        """
        try:
            _, option = command.split(maxsplit=1)
            if option == "inputs":
                response = self.formatInputs()
            elif option == "outputs":
                response = self.formatOutputs()
            elif option == "class":
                response = self.classifyIris()
            else:
                response = "400 Error: Invalid return option.\n"
            self.connection.send(response.encode())
        except ValueError:
            self.connection.send("400 Error: Invalid return command format.\n".encode())

    def handleClassify(self):
        """
        Classifies the Iris flower based on the normalized input data provided by the client.
        """
        input_vector = [self.inputs[var]["normalized"] for var in self.inputs]
        if any(v is None for v in input_vector):
            self.connection.send(
                "400 Error: Insufficient input values for classification.\n".encode()
            )
            return

        self.outputs = self.model.Recall(input_vector)
        print("classified output:", self.outputs)
        self.connection.send("Classification complete".encode())

    def handleClear(self):
        """
        Clears all inputs and outputs for the current client session.
        """
        self.inputs = {
            key: {"original": None, "normalized": None} for key in self.inputs
        }
        self.outputs = None
        self.connection.send("All input and output values have been cleared.".encode())
        print("Server: Cleared all inputs and outputs for the client.")

    def formatInputs(self):
        """
        Formats and returns the original input values for each variable.

        Returns:
            str: A formatted string with each variable's original value.
        """
        inputs_set = {k: v for k, v in self.inputs.items() if v["original"] is not None}
        if not inputs_set:
            return "400 Error: No input values set.\n"
        return " ".join([f"{k} {v['original']}" for k, v in inputs_set.items()])

    def formatOutputs(self):
        """
        Formats and returns the classification outputs.

        Returns:
            str: A formatted string with the classification probability for each species.
        """
        if not self.outputs:
            return "400 Error: No output values set.\n"
        species = ["IrisSetosa", "IrisVersicolor", "IrisVirginica"]
        return " ".join(
            [f"{species[i]} {self.outputs[i]:.5f}" for i in range(len(species))]
        )

    def classifyIris(self):
        """
        Identifies and returns the species with the highest probability from the classification outputs.

        Returns:
            str: The identified species of the Iris flower.
        """
        if not self.outputs:
            return "400 Error: No output values set.\n"
        species = ["Iris setosa", "Iris versicolor", "Iris virginica"]
        classification = species[self.outputs.index(max(self.outputs))]
        print(f"Classification: {classification}")
        return f"Classification: {classification}"

    def handleClose(self):
        """
        Ends the client connection by resetting inputs/outputs and notifying the client.
        """
        print(f"{self.address[0]} requested to close connection.")
        self.inputs = {
            key: {"original": None, "normalized": None} for key in self.inputs
        }
        self.outputs = None
        self.connection.send("200 OK".encode())

    def handleQuit(self):
        """
        Disconnects the client from the server with a confirmation message.
        """
        print(f"{self.address[0]} requested to quit. Closing connection.")
        self.connection.send("200 OK\nConnection closed.".encode())

    def handleShutdown(self):
        """
        Shuts down the server, closing all connections and notifying clients.
        """
        self.connection.send("200 OK\nServer is shutting down...\n".encode())
        print("Shutdown command received. Server is shutting down.")
        self.shutdown_func()
        self.connection.close()


class Server:
    """
    Main server class to handle incoming client connections, instantiate client handlers, and manage server shutdown.

    Attributes:
        host (str): The server's hostname or IP address.
        port (int): The server's port number.
        server_socket (socket.socket): The main server socket for listening to incoming connections.

    Methods:
        start(): Binds the socket, starts listening for incoming connections, and creates a new ClientHandler for each connection.
        shutdownServer(): Closes the server socket and stops accepting new connections.
        stop(): Stops the server.
    """

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = None

    def start(self):
        """
        Starts the server, binds the host and port, and listens for incoming connections.
        Each client connection is handled in a separate thread.
        """
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
                client_handler = ClientHandler(
                    connection, address, self, self.shutdownServer
                )
                client_handler.start()
            except OSError:
                break
        print("Server has been shut down.")

    def shutdownServer(self):
        """
        Initiates server shutdown by closing the main socket and stopping connections.
        """
        print("Shutting down the server...")
        if self.server_socket:
            self.server_socket.close()

    def stop(self):
        """
        Stops the server by closing the server socket.
        """
        if self.server_socket:
            self.server_socket.close()


# Entry point to run the server
if __name__ == "__main__":
    host = socket.gethostname()
    port = 5991
    server = Server(host, port)
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt detected. Shutting down the server...")
        server.shutdownServer()
    finally:
        server.stop()
        print("Server stopped.")
