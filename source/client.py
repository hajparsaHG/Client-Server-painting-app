from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from screens.canvas_screen import CanvasScreen
from utils.constants import HOST
import socket
import threading
import json
import time
from kivy.clock import Clock
import struct

PORT = 9999

class DrawingApp(App):
    def build(self):
        self.socket = None
        self.send_buffer = []
        self.connect_to_server()
        
        sm = ScreenManager()
        initial_canvas = CanvasScreen(send_to_server_callback=self.send_drawing_event, name='canvas_0')
        sm.add_widget(initial_canvas)
        return sm

    def connect_to_server(self):
        def _connect():
            try:
                print(f"[CLIENT] Connecting to server at {HOST}:{PORT}...")
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((HOST, PORT))
                self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                print("[CLIENT] Connected to server.")
                
                # Start receive thread
                threading.Thread(target=self._receive_data, daemon=True).start()
            except Exception as e:
                print(f"[CLIENT] Could not connect to server: {e}")

        t = threading.Thread(target=_connect, daemon=True)
        t.start()

    def _receive_data(self):
        """Receive data from server."""
        while True:
            try:
                # First receive the message length
                length_data = self.sock.recv(4)
                if not length_data:
                    break
                    
                message_length = struct.unpack('!I', length_data)[0]
                
                # Then receive the actual message
                received_data = b''
                while len(received_data) < message_length:
                    chunk = self.sock.recv(message_length - len(received_data))
                    if not chunk:
                        break
                    received_data += chunk
                
                if received_data:
                    event = json.loads(received_data.decode('utf-8'))
                    current_screen = self.root.current_screen
                if hasattr(current_screen, 'draw_input'):
                    Clock.schedule_once(
                        lambda dt: current_screen.draw_input.draw_received_line(event)
                    )
                    
            except Exception as e:
                print(f"[CLIENT] Error receiving data: {e}")
                self.reconnect()
                break

    def reconnect(self):
        """Try to reconnect to server"""
        while True:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((HOST, PORT))
                self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                print("[CLIENT] Reconnected to server")
                # Start receive thread again
                threading.Thread(target=self._receive_data, daemon=True).start()
                break
            except:
                print("[CLIENT] Reconnection failed, retrying in 5 seconds...")
                time.sleep(5)
    
    def send_drawing_event(self, event):
        """Send a drawing event to the server."""
        try:
            if self.sock:
                message = json.dumps(event).encode('utf-8')
                # First send the length of the message
                message_length = struct.pack('!I', len(message))
                self.sock.sendall(message_length)
                # Then send the actual message
                self.sock.sendall(message)
        except Exception as e:
            print(f"[CLIENT] Error sending drawing event: {e}")

if __name__ == "__main__":
    DrawingApp().run()