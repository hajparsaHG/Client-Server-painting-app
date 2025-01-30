import socket
import json
import threading
import struct
import subprocess
import sys
import time
import os

PORT = 9999
HOST = "0.0.0.0"

class DrawingServer:
    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port
        self.connections = {}
        self.displays = {}
        self.next_display_port = 5000
        self.processes = {}
        self.save_dir = "server_pics"
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        
    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"[SERVER] Listening on {self.host}:{self.port}...")

        try:
            while True:
                conn, addr = server_socket.accept()
                client_id = len(self.connections)
                print(f"[SERVER] Connected by {addr} (ID: {client_id})")
                
                display_port = self.next_display_port
                self.next_display_port += 1
                
                process = subprocess.Popen(
                    [sys.executable, 'display_manager.py', str(display_port)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                self.processes[client_id] = process
                
                display_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                retries = 0
                while retries < 10:
                    try:
                        display_sock.connect(('localhost', display_port))
                        break
                    except:
                        retries += 1
                        time.sleep(0.5)
                
                if retries == 10:
                    print(f"[SERVER] Failed to connect to display for client {client_id}")
                    process.kill()
                    conn.close()
                    continue
                
                self.connections[client_id] = conn
                self.displays[client_id] = display_sock
                
                threading.Thread(target=self.handle_client, args=(client_id,), daemon=True).start()
                
        except KeyboardInterrupt:
            print("\n[SERVER] Shutting down...")
        finally:
            self.cleanup()
            server_socket.close()
        
    def handle_client(self, client_id):
        conn = self.connections[client_id]
        display = self.displays[client_id]
        
        try:
            while True:
                length_data = conn.recv(4)
                if not length_data:
                    break
                    
                message_length = struct.unpack('!I', length_data)[0]
                data = conn.recv(message_length)
                if not data:
                    break
                
                event = json.loads(data.decode())
                if event["type"] == "save":
                    display.sendall(length_data + data)
                    
                    resp_length = struct.unpack('!I', display.recv(4))[0]
                    resp_data = display.recv(resp_length)
                    response = json.loads(resp_data.decode())
                    
                    if response["type"] == "save_response":
                        filename = f"{response['filename']}.png"
                        filepath = os.path.join(self.save_dir, filename)
                        with open(filepath, 'wb') as f:
                            f.write(bytes(response["data"]))
                        print(f"[SERVER] Saved drawing to {filepath}")
                        
                elif event["type"] == "exit":
                    display.sendall(length_data + data)
                    break
                else:
                    display.sendall(length_data + data)
                    
        except Exception as e:
            print(f"[SERVER] Error handling client {client_id}: {e}")
        finally:
            self.cleanup_client(client_id)

    def cleanup_client(self, client_id):
        if client_id in self.connections:
            self.connections[client_id].close()
            del self.connections[client_id]
        
        if client_id in self.displays:
            self.displays[client_id].close()
            del self.displays[client_id]
            
        if client_id in self.processes:
            self.processes[client_id].kill()
            del self.processes[client_id]

    def cleanup(self):
        for client_id in list(self.connections.keys()):
            self.cleanup_client(client_id)

if __name__ == "__main__":
    server = DrawingServer()
    server.start()