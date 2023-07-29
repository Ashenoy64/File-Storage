from socket import *
from _thread import *
import os
import sys
import ssl

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

context.load_cert_chain(certfile="./serverCert/rootCA.pem",
                        keyfile="./serverCert/rootCA.key")


path = 'serverFiles'
BUFFERSIZE = 4096


def registered(client_name, passwd):
    with open("registers.txt", "r") as f:
        for line in f:
            name, password = line.strip().split(',')
            if name == client_name:
                return password == passwd
        with open('registers.txt', 'a') as f:
            f.write(f'{client_name},{passwd}\n')
        return "Registration Successfull"


def multi_threaded_client(client):
    client = context.wrap_socket(client, server_side=True)
    register = True
    client_name, passwd = client.recv(2048).decode().split('&')

    text = registered(client_name, passwd)
    if text == False:
        client.send("Login Failed".encode())
        register = False
    else:
        if text == True:
            client.send("Login Successfull".encode())
        else:
            client.send(text.encode())
        clientPath = path + '/' + client_name
        if (not os.path.isdir(clientPath)):
            os.mkdir(clientPath)

    while register:
        # Get all the file available in the clients folder
        fileList = os.listdir(clientPath)
        if fileList == []:
            fileString = "no"
        else:
            fileString = '&'.join(fileList)

        # Assuming the variable size of the string
        size = sys.getsizeof(fileString)

        client.send(str(size).encode())
        client.send(fileString.encode())

        operation = client.recv(2048).decode()  # Start Serving the client
        while (operation != 'Done'):
            if operation == 'sending':  # client sends the file
                filename, size = client.recv(BUFFERSIZE).decode().split(' ')
                filePath = clientPath+'/'+filename
                size = int(size)
                read = 0
                with open(filePath, 'wb') as f:
                    while True:
                        bytes_read = client.recv(BUFFERSIZE)
                        read += len(bytes_read)
                        if not bytes_read:
                            break
                        f.write(bytes_read)
                        print(f"Recieved {read} out of {size} of the {filename}")
                        if read == size:
                            break
                print("File Has Been Recived successfully!")

            elif operation == "listdir":
                files = os.listdir(clientPath)
                fileString = ','.join(files)
                size = sys.getsizeof(fileString)
                client.send(str(size).encode())
                client.send(fileString.encode())

            else:  # client recives the file, operation will be the filename
                filePath = clientPath+'/'+operation
                size = os.path.getsize(filePath)
                client.send(f"{operation} {size}".encode())
                send = 0
                with open(filePath, 'rb') as f:
                    while True:
                        bytes_read = f.read(BUFFERSIZE)
                        send += len(bytes_read)
                        if not bytes_read:
                            break
                        client.sendall(bytes_read)
                        print(f"Sent {send} out of {size} of the {operation}")
                        if send == size:
                            break
                print("File Has Been Sent successfully!")

            operation = client.recv(2048).decode()
        break
    print('Connection to {} closed '.format(client_name))
    client.close()
    return


ThreadCount = 0


sock = socket()
sock.bind(('0.0.0.0', 5000))
sock.listen(5)


while True:
    print('Waiting for a client...')
    client, address = sock.accept()

    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(multi_threaded_client, (client, ))

    ThreadCount += 1

    print('Thread Number: ' + str(ThreadCount))
