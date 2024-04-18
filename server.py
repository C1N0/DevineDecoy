import customtkinter as ctk
import tkinter as tk
from tkinter import Toplevel, Button
import tkinter
import json
import socket
import threading
import os
import pyperclip

class Server:
    def __init__(self, master):
        self.master = master
        self.master.geometry('500x500')
        self.frame = ctk.CTkFrame(master=self.master)
        self.frame.pack(pady=20, padx=60, fill="both", expand=True)
        self.label = ctk.CTkLabel(master=self.frame, text="Login", font=("Arial", 20))
        self.label.pack(pady=12, padx=10)
        self.entry1 = ctk.CTkEntry(master=self.frame, placeholder_text="Username")
        self.entry1.pack(pady=12, padx=10)
        self.entry2 = ctk.CTkEntry(master=self.frame, placeholder_text="Password", show="*")
        self.entry2.pack(pady=12, padx=10)
        self.login_button = ctk.CTkButton(master=self.frame, text="Login", command=self.login)
        self.login_button.pack(pady=12, padx=10)
        self.clients = {}
        self.connected_clients = []
        self.client_sockets = {}
        self.server_running = False
        self.client_buttons = []
        self.clients_window = None

    def login(self):
        username = self.entry1.get()
        password = self.entry2.get()
        with open('users.json', 'r') as f:
            users = json.load(f)
        if username in users and users[username] == password:
            print("Login Successful")
            self.login_success()
        else:
            print("Login Failed")

    def login_success(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        success_label = ctk.CTkLabel(master=self.frame, text="DevineDecoy", font=("Aerial", 20))
        success_label.pack(pady=12, padx=10)
        start_button = ctk.CTkButton(master=self.frame, text="Start Server", command=self.server_start)
        start_button.pack(pady=12, padx=10)

    def server_start(self):
        self.server_running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('192.168.0.158', 12345))
        self.server_socket.listen(5)       
        self.status_label = ctk.CTkLabel(master=self.frame, text="Server started", font=("Aerial", 17))
        self.status_label.pack(pady=12, padx=10)
        self.show_clients_button = ctk.CTkButton(master=self.frame, text="Show Connected Clients", command=self.show_connected_clients)
        self.show_clients_button.pack(pady=12, padx=10)
        threading.Thread(target=self.handle_client, daemon=True).start()

    def handle_client(self):
            while self.server_running:
                try:
                    client_socket, address = self.server_socket.accept()
                except OSError:
                    break
                print("added",address)
                self.connected_clients.append(address)
                self.client_sockets[address[0]] = client_socket

                def receive_message(): 
                        while True:
                            try:
                                received_message = client_socket.recv(4096)
                                if received_message:
                                    print(received_message.decode())
                                if not received_message:
                                    break
                            except (BrokenPipeError, ConnectionResetError):
                                break
                        print("removed", address)
                        self.connected_clients.remove(address)
                        print(self.connected_clients)

                threading.Thread(target=receive_message, daemon=True).start()

    def show_connected_clients(self):
        if self.clients_window is None:
            self.clients_window = Toplevel()
            self.clients_window.geometry('400x400')
            self.clients_window.title('Connected Clients')
            self.refresh_button = tk.Button(self.clients_window, text="Refresh", command=self.show_connected_clients)
            self.refresh_button.pack()

        for button in self.client_buttons:
            button.destroy()
        self.client_buttons = []

        for client in self.connected_clients:
            client_ip, _= client
            client_button = Button(self.clients_window, text=str(client_ip), command=lambda ip=client_ip: self.handle_client_click(ip))
            client_button.pack(side='top',anchor='w')
            self.client_buttons.append(client_button)

    def handle_client_click(self, client_ip):
        self.client_window = tk.Toplevel(root)
        self.client_window.geometry('400x400')
        self.client_window.title(f"Client {client_ip}")
        self.chat_button = tk.Button(self.client_window, text="Chat", command=lambda: self.open_chat_window(client_ip))
        self.chat_button.pack()
        self.send_file_button = tk.Button(self.client_window, text="Send File", command=lambda: self.open_send_file_window(client_ip))
        self.send_file_button.pack()

    def open_chat_window(self, client_ip):
        self.chat_window = tk.Toplevel(root)
        self.chat_window.geometry('400x400')
        self.chat_window.title(f"Chat with {client_ip}")
        self.message_list = tk.Listbox(self.chat_window,height=20, width=50)
        self.message_list.pack()
        self.message_entry = tk.Entry(self.chat_window)
        self.message_entry.pack()
        self.send_button = tk.Button(self.chat_window, text="Send", command=lambda: self.send_message(client_ip))
        self.send_button.pack()
        self.paste_button = tk.Button(self.chat_window, text="Paste", command=self.paste)
        self.paste_button.pack()

    def paste(self):
            clipboard_text = pyperclip.paste()
            self.message_entry.delete(0, tk.END)
            self.message_entry.insert(0, clipboard_text)

    def open_send_file_window(self, client_ip):
        self.send_file_window = tk.Toplevel(root)
        self.send_file_window.geometry('400x400')
        self.send_file_window.title(f"Send File to {client_ip}")
        self.file_path = tk.StringVar()
        self.file_path_label = tk.Label(self.send_file_window, textvariable=self.file_path)
        self.file_path_label.pack()
        self.select_file_button = tk.Button(self.send_file_window, text="Select File", command=self.select_file)
        self.select_file_button.pack()
        self.send_file_button = tk.Button(self.send_file_window, text="Send File", command=lambda: self.send_file(self.client_sockets[client_ip], self.file_path.get()))
        self.send_file_button.pack()

    def select_file(self):
        file_path = tkinter.filedialog.askopenfilename()
        self.file_path.set(file_path)

    def send_message(self, ip):
        message = self.message_entry.get()
        client_socket = self.client_sockets[ip]
        client_socket.send(message.encode())
        self.message_list.insert(tk.END, "You: " + message)
        self.message_entry.delete(0, tk.END)

    def send_file(self, client_socket, file_path):
        client_socket.send(b"FILE\n")
        name = os.path.basename(file_path)
        client_socket.send(name.encode())
        client_socket.send(b"\n")
        with open(file_path, "rb") as file:
            for line in file:
                client_socket.send(line)
        client_socket.send(b"EOF")
    
    def close_server(self):
        if hasattr(self, 'server_socket') and isinstance(self.server_socket, socket.socket):
            self.server_socket.close()
            self.server_running = False
            print("Server socket closed")
        root.destroy()


root = ctk.CTk()
app = Server(root)
root.protocol("WM_DELETE_WINDOW", app.close_server)
root.mainloop()




