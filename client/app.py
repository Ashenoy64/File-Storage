import streamlit as st
import numpy as np
import pandas as pd
import ssl
import socket
import os

context = ssl.create_default_context()
context.load_verify_locations("./serverCert/rootCA.pem")

path = ".\clientFiles"


class Response(Exception):
    def __init__(self, msg):
        self.msg = msg


if not os.path.exists(path):
    os.mkdir(".\clientFiles")

BUFFERSIZE = 4096
if 'submit' not in st.session_state:
    st.session_state.submit = True

if 'clientName' not in st.session_state:
    st.session_state.clientName = ""

if 'serverIP' not in st.session_state:
    st.session_state.serverIP = ""

if 'password' not in st.session_state:
    st.session_state.password = ""


def perform(filename, operation):
    if operation == "Upload":
        fileName = filename
        filePath = path+'/'+st.session_state.clientName+"/"+fileName
        sock = st.session_state.sock
        if (os.path.isfile(filePath)):

            sock.send(str('sending').encode())
            size = os.path.getsize(filePath)
            sock.send(f"{fileName} {size}".encode())

            send = 0

            with open(filePath, 'rb') as f:
                progress = st.progress(0.0,text="Uploading ... ")
                while True:
                    bytes_read = f.read(BUFFERSIZE)
                    if not bytes_read:
                        break
                    sock.sendall(bytes_read)
                    send += len(bytes_read)
                    progress.progress(send/size,text='Uploading ...')
                    if size == send:
                        break

            progress.empty()
            updateServerFiles()
            st.success("File Has Been Sent successfully!")
        else:
            st.error("No such file exist")

    else:
        sock = st.session_state.sock
        fileName = filename
        sock.send(filename.encode())
        filename, size = sock.recv(BUFFERSIZE).decode().split(' ')

        filePath = path+'/'+st.session_state.clientName+'/'+fileName
        size = int(size)
        read = 0

        with open(filePath, 'wb') as f:
            progress = st.progress(0.0,text="Downloading ... ")
            while True:
                bytes_read = sock.recv(BUFFERSIZE)
                if not bytes_read:
                    break
                read += len(bytes_read)
                f.write(bytes_read)
                progress.progress(read/size,text="Downloading ...")
                if read == size:
                    break
        progress.empty()
        updateServerFiles()
        st.success("File Has Been Recived successfully!")


def logout():
    st.session_state.sock.send("Done".encode())
    st.session_state.sock.close()
    st.session_state.pop("sock")
    st.session_state.submit = True


def updateServerFiles():
    sock = st.session_state.sock
    sock.send("listdir".encode())
    size = int(sock.recv(2048).decode())
    files = sock.recv(size).decode()
    serverSide = pd.DataFrame(
        np.array(files.split(',')), columns=["Server Files"])
    st.session_state.serverSide = serverSide


def updateClientFiles():
    files = os.listdir(os.path.join(path, st.session_state.clientName))
    serverSide = pd.DataFrame(np.array(files), columns=["Client Files"])
    st.session_state.clientSide = serverSide


def toggle():
    connection = ""
    if st.session_state.client != "" and st.session_state.serverIP != "" and st.session_state.password != "":
        with st.spinner("Connecting to server..."):
            try:
                st.session_state.clientName = st.session_state.client
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sSock = context.wrap_socket(sock, server_hostname="localhost")
                sSock.connect((st.session_state.serverIP, 5000))
                st.session_state["sock"] = sSock

                sock = st.session_state.sock
                sock.send((st.session_state.clientName+'&' +
                          st.session_state.password).encode())

                response = sock.recv(2048).decode()
                if response == "Login Failed":
                    raise Response(response)
                size = int(sock.recv(2048).decode())
                files = sock.recv(size).decode()

                if (files == "no"):
                    serverSide = []
                    st.session_state.serverSide = pd.DataFrame(
                        serverSide, columns=["Server Files"])
                else:
                    st.session_state.serverSide = pd.DataFrame(
                        np.array(files.split(",")), columns=["Server Files"])

                if not os.path.exists(os.path.join(path, st.session_state.clientName)):
                    os.mkdir(os.path.join(path, st.session_state.clientName))

                clientside = os.listdir(os.path.join(
                    path, st.session_state.clientName))
                clientSide = pd.DataFrame(
                    np.array(clientside), columns=["Client Files"])
                
                st.session_state.clientSide =clientSide

            except Response as e:
                connection = e.msg
            except Exception as e:
                print(e)
                connection = "Connection Failed Reason Unkown " 

            if connection != "":
                st.error(connection)
            else:
                st.success("Connected To Server")
                st.session_state.submit = not st.session_state.submit


if st.session_state.submit:
    with st.container():
        st.text_input("Username", key="client")
        st.text_input("Password", key="password")
        st.text_input("Server IP", key="serverIP")
        st.button("Submit", on_click=toggle)


else:

    clientName = st.session_state.clientName
    serverIP = st.session_state.serverIP
    password = st.session_state.password
    updateClientFiles()
    with st.container():
        col1, col2 = st.columns(2)
        col1.markdown("<h2 style='position:relative; bottom:20px; '>{}</h2>".format(
            st.session_state.clientName), unsafe_allow_html=True)

        col2.button("Logout", on_click=logout)
    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            st.header("Client Side")
            with st.container():
                st.dataframe(st.session_state.clientSide, width=400)

                st.button("Refresh", on_click=updateClientFiles)

        with col2:
            st.header("Server Side")
            with st.container():
                st.dataframe(st.session_state.serverSide, width=400)

    with st.container():
        operation = st.radio("", ['Upload', 'Download'])
        filename = ""
        if operation == 'Upload':
            filename = st.selectbox(
                "Select File To Upload", st.session_state.clientSide)
        else:
            filename = st.selectbox(
                "Select File To Download", st.session_state.serverSide)

        st.button(operation, on_click=perform, args=(filename, operation))
