import socket
import sys

class TCPClient:
    def __init__(self):
        self.clientSocket = None
        self.portNum = 5991
        self.hostName = socket.gethostname()
    
    def handleInputError(self, text="Text cannot be empty. Please enter a valid Text."): 
        print(
            "\n*****************************************************************"
        )
        print(
            f"* Error: {text} *"
        )
        print(
            "*****************************************************************"
        )

    
    def handleOpenConnection(self):
        try:
            clientSocket = socket.socket()
        except socket.error as err:
            print(f"Socket creation failed with error {err}")
            sys.exit()

        print(f"Trying to connect to host {self.hostName} on port {self.portNum}")
        clientSocket.connect((self.hostName, self.portNum))
        print("Connection successful")
        sWelcome = clientSocket.recv(1024).decode()
        print(sWelcome)
        self.clientSocket = clientSocket
        return clientSocket
    
    def handleQuit(self):
        self.clientSocket.send("quit".encode())
        print("Closing connection.")
        self.clientSocket.close()
    
    def handleShutdown(self):
        self.clientSocket.send("shutdown".encode())
        sStatus = self.clientSocket.recv(1024).decode()
        print("sStatus", sStatus)
        if sStatus == "200 OK":
            print("server: 200 OK \n Server is shutting down...\n")
    
    def mainFunction(self):
        while True:
            print("\n================================================")
            print("Available commands: OPEN/ CLOSE/ INPUT/ CLEAR/ CLASSIFY/ RETURN/ QUIT/ SHUTDOWN")
            command = input("Enter command: ").strip().lower()
            if not command:
                self.handleInputError()
                continue
            if not self.clientSocket:
                if command == "open":
                    self.handleOpenConnection()
                else:
                    self.handleInputError("No Connection detected, please start with OPEN command.")
                    continue
            else:
                if command == "open":
                    print(f"Connected to host {self.hostName} on port {self.portNum}")
                    continue
                if command == "quit":
                    self.handleQuit()
                    break
                if command == "shutdown":
                    self.handleShutdown()
                    break
                else:
                    self.handleInputError("Invalid command. Please use one of the following: OPEN/ CLOSE/ INPUT/ CLEAR/ CLASSIFY/ RETURN/ QUIT/ SHUTDOWN.")
                    continue

if __name__ == "__main__":
    client = TCPClient()
    try:
        client.mainFunction()
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt detected. Closing the client connection...")
        if client.clientSocket:
            client.clientSocket.close()
