from socket import AF_INET, socket, SOCK_STREAM, SHUT_WR
from threading import Thread
import subprocess

# Start the server
def init_server(server_socket, PORT):
    address = ('', PORT)
    server_socket.bind(address)
    server_socket.listen()
    print("Server started on port {port}".format(port = PORT))

# Listen for connection on a thread
def listen(server_socket):
    while True:
        client_socket, client_address = server_socket.accept()
        create_client(client_socket, client_address)

# When client connects create a thread for each client
# TODO: Make it scalable
def create_client(client_socket, client_address):
    clients[client_socket] = client_address
    print("Connected to {address}".format(address = client_address))

    # wait for clients messege in a new thread
    Thread(target = recieve_message, args = (client_socket,)).start()

def recieve_message(client_socket):
    message = ""
    while True:
        print("Waiting for message...")
        try:
            message = client_socket.recv(BUFFER_SIZE).decode('UTF-8')
        except Exception as error:
            print(error)
            close_connection(client_socket)
            return
        print("Recieved: {message}".format(message = message))

        # check message
        # TODO: Don't disconnect if accidently sent empty message
        if message == "":
            print("Revieved empty string, closing connecting")
            close_connection(client_socket)

        elif message == "help":
            client_socket.send(bytes("""-> Send file syntax to enter file mode:
            \tfile /path/to/file
            -> To exit from the chat:
            \t exit""", "UTF-8"))

        elif message == "exit":
            print("Recieved exit string, closing connecting")
            close_connection(client_socket)
            return

        elif message[0:5] == "file ":
            print("Entering file mode")
            metadata = message[5:]
            handle_file(client_socket, metadata)

        else:
            print("Recieved text message: {msg}".format(msg = message))
            for socket in clients.keys():
                if socket != client_socket:
                    socket.send(bytes(message, 'UTF-8'))

def handle_file(client_socket, metadata):
    status, file_name, file_size = metadata.split('#')
    file_size = int(file_size)
    if status == "0":
        return
    else:
        print("Starting file transfer")
        broadcast(client_socket ,bytes("file {name}#{size}".format(name = file_name, size = file_size), "UTF-8"))
        while file_size > 0:
            print(file_size)
            file_size -= 1024
            data = ""
            data = client_socket.recv(BUFFER_SIZE)
            # print(data)
            broadcast(client_socket, data)
            if not data:
                break

        print("File transfer complete, switching to text mode")

def close_connection(client_socket):
    global clients
    client_socket.close()
    del clients[client_socket]

def broadcast(client_socket, data):
    for socket in clients.keys():
        if socket != client_socket:
            socket.send(data)

# TODO: close port when exiting in any way
if __name__ == "__main__":
    # constants
    SERVER_SOCKET = socket(AF_INET, SOCK_STREAM)
    PORT = 5000
    BUFFER_SIZE = 1024

    # clients dictionary stores sockets as key and address as value
    clients = {}

    # start server
    init_server(SERVER_SOCKET, PORT)
    listen(SERVER_SOCKET)
