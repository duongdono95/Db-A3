import socket
import threading

from IrisANN.TIris import TIris  # Import the Iris classification model

# List of valid command strings
commands = ["close", "input", "clear", "classify", "return", "quit", "shutdown"]

# Acceptable ranges for each iris flower variable
VARIABLE_RANGES = {
    "sepallength": (4.3, 7.9),
    "sepalwidth": (2.0, 4.4),
    "petallength": (1.0, 6.9),
    "petalwidth": (0.1, 2.5),
}


# Class to handle each client connection
class ClientHandler(threading.Thread):
    def __init__(self, connection, address, server, shutdown_func):
        super().__init__()
        self.connection = connection  # Connection object for the client
        self.address = address  # Client's address
        self.server = server  # Reference to the server
        self.shutdown_func = shutdown_func  # Function to trigger server shutdown
        # Dictionary to hold input data and normalized values for each variable
        self.inputs = {
            "sepallength": {"original": None, "normalized": None},
            "sepalwidth": {"original": None, "normalized": None},
            "petallength": {"original": None, "normalized": None},
            "petalwidth": {"original": None, "normalized": None},
        }
        self.outputs = None  # Placeholder for model classification results
        self.model = TIris()  # Instance of the Iris classification model

    # Main method to handle client connection
    def run(self):
        print(f"server: got connection from client {self.address[0]}")
        self.connection.send("Server is ready...".encode())

        while True:
            try:
                # Receive and process commands from the client
                command = self.connection.recv(1024).decode().strip().lower()
                if not command:
                    break
                # Handle different commands based on the command string
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

    # Handle the 'input' command, which provides variable values
    def handleInput(self, command):
        try:
            _, var_name, value_str = command.split(maxsplit=2)
            if var_name not in VARIABLE_RANGES:
                self.connection.send("400 Error: Invalid variable name.\n".encode())
                return

            try:
                value = float(value_str)  # Convert the value to float
                min_val, max_val = VARIABLE_RANGES[var_name]
                # Check if the value is within the acceptable range
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

    # Handle the 'return' command, which returns data to the client
    def handleReturn(self, command):
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

    # Handle the 'classify' command to classify the Iris based on input data
    def handleClassify(self):
        # Prepare an input vector for classification
        input_vector = [
            self.inputs["sepallength"]["normalized"],
            self.inputs["sepalwidth"]["normalized"],
            self.inputs["petallength"]["normalized"],
            self.inputs["petalwidth"]["normalized"],
        ]
        # Ensure all inputs are provided
        if any(v is None for v in input_vector):
            self.connection.send(
                "400 Error: Insufficient input values for classification.\n".encode()
            )
            return

        # Get classification results from the model
        self.outputs = self.model.Recall(input_vector)
        print("classified output:", self.outputs)
        self.connection.send("Classification complete".encode())

    # Handle the 'clear' command to reset inputs and outputs
    def handleClear(self):
        # Reset input and output values to None
        self.inputs = {
            key: {"original": None, "normalized": None} for key in self.inputs
        }
        self.outputs = None
        self.connection.send("All input and output values have been cleared.".encode())
        print("Server: Cleared all inputs and outputs for the client.")

    # Format input data to return to the client
    def formatInputs(self):
        inputs_set = {k: v for k, v in self.inputs.items() if v["original"] is not None}
        if not inputs_set:
            return "400 Error: No input values set.\n"
        return " ".join([f"{k} {v['original']}" for k, v in inputs_set.items()])

    # Format output data to return to the client
    def formatOutputs(self):
        if not self.outputs:
            return "400 Error: No output values set.\n"
        species = ["IrisSetosa", "IrisVersicolor", "IrisVirginica"]
        return " ".join(
            [f"{species[i]} {self.outputs[i]:.5f}" for i in range(len(species))]
        )

    # Classify and return the Iris species as a string
    def classifyIris(self):
        if not self.outputs:
            return "400 Error: No output values set.\n"
        species = ["Iris setosa", "Iris versicolor", "Iris virginica"]
        classification = species[self.outputs.index(max(self.outputs))]
        print(f"Classification: {classification}")
        return f"Classification: {classification}"

    # Handle the 'close' command to end the client connection
    def handleClose(self):
        print(f"{self.address[0]} requested to close connection.")
        self.inputs = {
            key: {"original": None, "normalized": None} for key in self.inputs
        }
        self.outputs = None
        self.connection.send("200 OK".encode())

    # Handle the 'quit' command, indicating the client wants to disconnect
    def handleQuit(self):
        print(f"{self.address[0]} requested to quit. Closing connection.")
        self.connection.send("200 OK\nConnection closed.".encode())

    # Handle the 'shutdown' command to stop the server
    def handleShutdown(self):
        self.connection.send("200 OK\nServer is shutting down...\n".encode())
        print("Shutdown command received. Server is shutting down.")
        self.shutdown_func()
        self.connection.close()


# Main server class to handle incoming connections
class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = None  # Server's socket object

    # Start the server and accept incoming connections
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
                # Start a new thread to handle the client
                client_handler = ClientHandler(
                    connection, address, self, self.shutdownServer
                )
                client_handler.start()
            except OSError:
                break
        print("Server has been shut down.")

    # Shutdown the server
    def shutdownServer(self):
        print("Shutting down the server...")
        if self.server_socket:
            self.server_socket.close()

    # Stop the server
    def stop(self):
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
