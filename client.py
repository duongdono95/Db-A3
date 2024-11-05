import socket
import sys

# Define acceptable ranges for input variables
VARIABLE_RANGES = {
    "sepalLength": (4.3, 7.9),
    "sepalWidth": (2.0, 4.4),
    "petalLength": (1.0, 6.9),
    "petalWidth": (0.1, 2.5),
}


class TCPClient:
    def __init__(self):
        self.clientSocket = None  # Initialize the client socket
        self.portNum = 5991  # Default port number for connection

    # Function to handle and display input errors
    def handleInputError(self, text="Text cannot be empty. Please enter a valid Text."):
        print("\n*****************************************************************")
        print(f"* Error: {text} *")
        print("*****************************************************************")

    # Function to handle and display server errors
    def handleServerError(self, sStatus):
        print("\n***************************************")
        print(f"* ERROR: {sStatus} *")
        print("***************************************")

    # Function to establish a connection to the server with a given address
    def handleOpen(self, command):
        try:
            _, address = command.split(maxsplit=1)  # Parse address from the command
        except ValueError:
            self.handleInputError(
                "Please specify an address to open a connection (e.g., 'open 127.0.0.1')."
            )
            return

        try:
            # Create socket and attempt to connect to server
            self.clientSocket = socket.socket()
            print(f"Trying to connect to host {address} on port {self.portNum}")
            self.clientSocket.connect((address, self.portNum))
            print("Connection successful")
            sWelcome = self.clientSocket.recv(1024).decode()  # Receive welcome message
            print("Server:", sWelcome)
        except socket.error as err:
            print(f"Failed to connect to {address} with error: {err}")
            self.clientSocket = None

    # Function to close the current connection
    def handleClose(self):
        if self.clientSocket:
            self.clientSocket.send("close".encode())  # Send close command to server
            sStatus = self.clientSocket.recv(1024).decode()  # Receive server response
            print("Server:", sStatus)
            if sStatus == "200 OK":
                print("Connection closed.")
            self.clientSocket.close()
            self.clientSocket = None
        else:
            print("No active connection to close.")

    # Function to send an input command to the server
    def handleInput(self, command):
        if self.clientSocket:
            self.clientSocket.send(command.encode())  # Send input command to server
            sStatus = self.clientSocket.recv(1024).decode()  # Receive server response
            print("Server:", sStatus)
        else:
            self.handleInputError(
                "No active connection. Please use 'open <address>' to connect."
            )

    # Function to clear stored inputs and outputs on the server
    def handleClear(self):
        if self.clientSocket:
            self.clientSocket.send("clear".encode())  # Send clear command to server
            sStatus = self.clientSocket.recv(1024).decode()  # Receive server response
            print("Server:", sStatus)
        else:
            self.handleInputError(
                "No active connection. Please use 'open <address>' to connect."
            )

    # Function to classify the current inputs stored on the server
    def handleClassify(self):
        if self.clientSocket:
            self.clientSocket.send(
                "classify".encode()
            )  # Send classify command to server
            sStatus = self.clientSocket.recv(1024).decode()  # Receive server response
            print("Server:", sStatus)
        else:
            self.handleInputError(
                "No active connection. Please use 'open <address>' to connect."
            )

    # Function to shut down the server
    def handleShutdown(self):
        if self.clientSocket:
            self.clientSocket.send(
                "shutdown".encode()
            )  # Send shutdown command to server
            sStatus = self.clientSocket.recv(1024).decode()  # Receive server response
            print("Server:", sStatus)
            if "Server is shutting down" in sStatus:
                self.clientSocket.close()
                self.clientSocket = None
                print("Server shutdown initiated.")
        else:
            self.handleInputError(
                "No active connection. Please use 'open <address>' to connect."
            )

    # Function to quit the client and close any open connection
    def handleQuit(self):
        if self.clientSocket:
            self.clientSocket.send("quit".encode())  # Send quit command to server
            print("Closing connection.")
            self.clientSocket.close()
            self.clientSocket = None
        print("Goodbye!")  # Message displayed when client quits

    # Main loop to manage user commands
    def mainFunction(self):
        while True:
            print("\n================================================")
            print(
                "Available commands:\n"
                " - OPEN <address>\n"
                " - CLOSE \n"
                " - INPUT <variable> <value>\n"
                " - RETURN <inputs|outputs|class>\n"
                " - CLASSIFY\n"
                " - CLEAR \n"
                " - QUIT \n"
                " - SHUTDOWN"
            )

            command = input("Enter command: ").strip().lower()  # User command input
            if not command:
                self.handleInputError()
                continue
            if not self.clientSocket:
                # If no connection, allow only OPEN and QUIT commands
                if command.startswith("open"):
                    self.handleOpen(command)
                elif command == "quit":
                    self.handleQuit()
                    break
                else:
                    self.handleInputError(
                        "No connection detected, please start with an OPEN command."
                    )
                    continue
            else:
                # If connected, process various commands
                if command == "close":
                    self.handleClose()
                elif command == "quit":
                    self.handleQuit()
                    break
                elif command.startswith("input"):
                    self.handleInput(command)
                elif command.startswith("return"):
                    self.handleInput(command)  # Send return command to server
                elif command == "classify":
                    self.handleClassify()
                elif command == "clear":
                    self.handleClear()
                elif command == "shutdown":
                    self.handleShutdown()
                else:
                    self.handleInputError(
                        "Invalid command. Please use one of the following: OPEN <address>/ CLOSE/ INPUT <variable> <value>/ RETURN <inputs|outputs|class>/ CLASSIFY/ CLEAR/ QUIT/ SHUTDOWN."
                    )
                    continue


# Main execution block
if __name__ == "__main__":
    client = TCPClient()  # Initialize TCPClient instance
    try:
        client.mainFunction()  # Start main function loop
    except KeyboardInterrupt:
        # Handle keyboard interrupt gracefully
        print("\nKeyboardInterrupt detected. Closing the client connection...")
        if client.clientSocket:
            client.clientSocket.close()
