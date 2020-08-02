from socket import AF_INET, socket, SOCK_STREAM, SHUT_WR
from threading import Thread
from os import path
from time import sleep
import sys

# connect to server
def connect_server(client_socket, address):
    try:
        client_socket.connect(address)
    except ConnectionRefusedError:
        print("Unable to connect to server, please try again")
        sys.exit(0)

# send a message
def send_message(client_socket, message):
    if message[0:5] == "file ":
        file_path = message.split(" ")[1]
        send_file(client_socket, file_path)
        return
    else:
        client_socket.send(bytes(message, 'UTF-8'))


def type_and_send_message(client_socket):
    while True:
        print("Enter a message: ", sep="")
        message = input()
        send_message(client_socket, message)
        if message == "exit":
            close_connection(client_socket)

# recieve a message
def recieve(client_socket):
    message = ""
    while True:
        try:
            message = client_socket.recv(BUFFER_SIZE).decode('UTF-8')
            # print('Message: {message}'.format(message = message))
        except ConnectionResetError:
            print("Connection reset by server")
            close_connection(client_socket)
            
        # print("Waiting for message...")
        if message == "" :
            print("Revieved empty string, closing connecting")
            close_connection(client_socket)

        elif message[0:5] == "file ":
            print("Started revieving file")
            metadata = message[5:]
            recieve_file(client_socket, metadata)

        else:
            print("{msg}".format(msg = message))

def close_connection(client_socket):
    print("Client socket closed")
    client_socket.close()
    sys.exit(0)
    pass

# This function executes after the server is in file mode
def send_file(client_socket, file_path):
    if path.exists(file_path):
        file_name = file_path.split('/')[-1]
        file_binary = open(file_path, "rb")
        file_size = path.getsize(file_path)

        client_socket.send(bytes("file 1#{name}#{size}".format(name = file_name, size = file_size), "UTF-8"))
        sleep(0.1)
        client_socket.send(bytes(file_binary.read()))
    else:
        client_socket.send(bytes("0", "UTF-8"))

def recieve_file(client_socket, metadata):
    global BUFFER_SIZE
    file_name, file_size = metadata.split('#')
    file_size = int(file_size)
    
    try:
        f = open("./files/"+file_name, 'wb')
    except Exception as error:
        print(error)
        f.close()
        return

    while file_size > 0:
        print(file_size)
        file_size -= 1024
        data = ""
        data = client_socket.recv(BUFFER_SIZE)
        if not data:
            break
        f.write(data)
    f.close()
    print("Finished recieving file")

if __name__ == "__main__":
    BUFFER_SIZE = 1024
    ADDRESS = ("localhost", 5000)
    CLIENT_SOCKET = socket(AF_INET, SOCK_STREAM)
    connect_server(CLIENT_SOCKET, ADDRESS)
    Thread(target = recieve, args = (CLIENT_SOCKET,)).start()
    messege_type_thread = Thread(target = type_and_send_message, args = (CLIENT_SOCKET,))
    messege_type_thread.start()
    messege_type_thread.join()
