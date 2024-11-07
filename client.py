"""
TCP Client Module for interacting with a TCP server to classify Iris flower data.

This module provides a command-line client that connects to a server, sends commands, and receives responses. The client supports commands to input data, classify it, retrieve results, and control the server connection.

Classes:
    TCPClient: Main class representing the TCP client, handling user commands and managing the server connection.

Modules:
    socket: Provides access to network sockets for communication between client and server.
    sys: Provides system-specific parameters and functions, used here for handling the main entry point.

Constants:
    VARIABLE_RANGES (dict): Acceptable ranges for each Iris flower variable, imported from the client module.

Classes:
    TCPClient: Represents a TCP client that connects to the server, sends commands, and receives responses.

"""

import socket
import sys

from server import VARIABLE_RANGES


class TCPClient:
    """
    Represents a TCP client for connecting to a server, managing user commands, and handling server responses.

    Attributes:
        clientSocket (socket.socket): The socket instance used for client-server communication.
        portNum (int): The port number for the connection, defaulting to 5991.

    Methods:
        handleInputError(text): Prints an error message for invalid user input.
        handleServerError(sStatus): Prints an error message for errors returned by the server.
        handleOpen(command): Establishes a connection to the server at a specified address.
        handleClose(): Closes the current connection with the server.
        handleInput(command): Sends an input command to the server.
        handleClear(): Clears the stored inputs and outputs on the server.
        handleClassify(): Requests classification of the current inputs from the server.
        handleShutdown(): Sends a shutdown command to the server.
        handleQuit(): Closes the client connection and exits.
        mainFunction(): Main loop to interact with the user and manage commands.
    """

    def __init__(self):
        self.clientSocket = None  # Initialize the client socket
        self.portNum = 5991  # Default port number for connection

    def handleInputError(self, text="Text cannot be empty. Please enter a valid Text."):
        """
        Displays an error message for invalid user input.

        Parameters:
            text (str): The error message to display.
        """
        print("\n*****************************************************************")
        print(f"* Error: {text} *")
        print("*****************************************************************")

    def handleServerError(self, sStatus):
        """
        Displays an error message returned by the server.

        Parameters:
            sStatus (str): The error message received from the server.
        """
        print("\n***************************************")
        print(f"* ERROR: {sStatus} *")
        print("***************************************")

    def handleOpen(self, command):
        """
        Establishes a connection to the server at the specified address.

        Parameters:
            command (str): Command string containing the server address.
        """
        try:
            _, address = command.split(maxsplit=1)  # Parse address from the command
        except ValueError:
            self.handleInputError(
                "Please specify an address to open a connection (e.g., 'open 127.0.0.1')."
            )
            return

        try:
            self.clientSocket = socket.socket()
            print(f"Trying to connect to host {address} on port {self.portNum}")
            self.clientSocket.connect((address, self.portNum))
            print("Connection successful")
            sWelcome = self.clientSocket.recv(1024).decode()  # Receive welcome message
            print("Server:", sWelcome)
        except socket.error as err:
            print(f"Failed to connect to {address} with error: {err}")
            self.clientSocket = None

    def handleClose(self):
        """
        Closes the current connection with the server.
        """
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

    def handleInput(self, command):
        """
        Sends an input command to the server, expecting a response.

        Parameters:
            command (str): The input command, including the variable name and value.
        """
        if self.clientSocket:
            self.clientSocket.send(command.encode())  # Send input command to server
            sStatus = self.clientSocket.recv(1024).decode()  # Receive server response
            print("Server:", sStatus)
        else:
            self.handleInputError(
                "No active connection. Please use 'open <address>' to connect."
            )

    def handleClear(self):
        """
        Sends a command to clear stored inputs and outputs on the server.
        """
        if self.clientSocket:
            self.clientSocket.send("clear".encode())  # Send clear command to server
            sStatus = self.clientSocket.recv(1024).decode()  # Receive server response
            print("Server:", sStatus)
        else:
            self.handleInputError(
                "No active connection. Please use 'open <address>' to connect."
            )

    def handleClassify(self):
        """
        Requests classification of the current inputs stored on the server.
        """
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

    def handleShutdown(self):
        """
        Sends a command to shut down the server and closes the client connection.
        """
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

    def handleQuit(self):
        """
        Sends a quit command to the server and closes the client connection.
        """
        if self.clientSocket:
            self.clientSocket.send("quit".encode())  # Send quit command to server
            print("Closing connection.")
            self.clientSocket.close()
            self.clientSocket = None
        print("Goodbye!")  # Message displayed when client quits

    def mainFunction(self):
        """
        Main loop to interact with the user and manage commands. Provides available commands, handles input, and executes commands.
        """
        while True:
            print("================================================")
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
