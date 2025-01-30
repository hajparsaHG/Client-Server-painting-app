from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Line, Rectangle
from kivy.clock import Clock
import socket
import json
import threading
import struct
import math
import sys
import os

class CanvasWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.drawings = []
        with self.canvas.before:
            Color(0, 0, 0, 1)
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(size=self._update_bg)

    def _update_bg(self, instance, value):
        self.bg.pos = self.pos
        self.bg.size = self.size
        
    def draw_line(self, event):
        with self.canvas:
            if event["type"] == "down":
                Color(*event.get("color", [1, 1, 1, 1]))
                line = Line(points=[event["x"], event["y"]], width=event.get("width", 2))
                self.drawings.append(line)
            elif event["type"] == "move" and self.drawings:
                self.drawings[-1].points += [event["x"], event["y"]]
            elif event["type"] == "erase":
                self.erase_at_point(event["x"], event["y"], event["radius"])
            elif event["type"] == "erase_all":
                for line in self.drawings[:]:
                    self.canvas.remove(line)
                self.drawings.clear()

    def erase_at_point(self, x, y, radius):
        lines_to_remove = []
        for line in self.drawings:
            if self.line_intersects_circle(line, (x, y), radius):
                lines_to_remove.append(line)
                    
        for line in lines_to_remove:
            self.canvas.remove(line)
            self.drawings.remove(line)

    def line_intersects_circle(self, line, center, radius):
        points = line.points
        for i in range(0, len(points)-2, 2):
            ax, ay = points[i], points[i+1]
            bx, by = points[i+2], points[i+3]
            
            vx = bx - ax
            vy = by - ay
            wx = center[0] - ax
            wy = center[1] - ay
            
            c1 = wx * vx + wy * vy
            if c1 <= 0:
                if math.dist(center, (ax, ay)) <= radius:
                    return True
                continue
                
            c2 = vx * vx + vy * vy
            if c2 <= c1:
                if math.dist(center, (bx, by)) <= radius:
                    return True
                continue
                
            t = c1 / c2
            closest = (ax + t * vx, ay + t * vy)
            if math.dist(center, closest) <= radius:
                return True
                
        return False

    def save_canvas(self, filename):
        temp_file = f"temp_{filename}.png"
        self.export_to_png(temp_file)
        with open(temp_file, 'rb') as f:
            data = f.read()
        os.remove(temp_file)
        return data

class DisplayLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical')
        self.title_label = Label(
            text="Untitled",
            size_hint_y=None,
            height='40dp',
            font_size='20dp'
        )
        self.canvas_widget = CanvasWidget()
        
        self.add_widget(self.title_label)
        self.add_widget(self.canvas_widget)
    
    def set_title(self, title):
        self.title_label.text = title

class DisplayManager(App):
    def __init__(self, port):
        super().__init__()
        self.port = port
        self.layout = None
        self.server_socket = None
        self.client_connection = None
        
    def build(self):
        self.layout = DisplayLayout()
        threading.Thread(target=self.listen_for_events, daemon=True).start()
        return self.layout

    def handle_event(self, event):
        try:
            if event["type"] == "save":
                data = self.layout.canvas_widget.save_canvas(event["filename"])
                response = {
                    "type": "save_response",
                    "data": list(data),
                    "filename": event["filename"]
                }
                data = json.dumps(response).encode()
                length = struct.pack('!I', len(data))
                self.client_connection.sendall(length + data)
            elif event["type"] == "set_title":
                self.layout.set_title(event["title"])
            elif event["type"] == "exit":
                self.stop()
                sys.exit()
            else:
                self.layout.canvas_widget.draw_line(event)
        except Exception as e:
            print(f"Error handling event: {e}")
        
    def listen_for_events(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind(('localhost', self.port))
            self.server_socket.listen(1)
            print(f"Display manager listening on port {self.port}")
            
            while True:
                self.client_connection, addr = self.server_socket.accept()
                print(f"Display connected to {addr}")
                
                while True:
                    length_data = self.client_connection.recv(4)
                    if not length_data:
                        break
                        
                    message_length = struct.unpack('!I', length_data)[0]
                    data = self.client_connection.recv(message_length)
                    if data:
                        event = json.loads(data.decode())
                        Clock.schedule_once(lambda dt, e=event: self.handle_event(e))
                
                self.client_connection.close()
                
        except Exception as e:
            print(f"Error in display manager: {e}")
        finally:
            self.cleanup()

    def cleanup(self):
        if self.client_connection:
            self.client_connection.close()
        if self.server_socket:
            self.server_socket.close()

    def on_stop(self):
        self.cleanup()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python display_manager.py <port>")
        sys.exit(1)
    
    try:
        port = int(sys.argv[1])
        DisplayManager(port).run()
    except ValueError:
        print("Port must be a number")
        sys.exit(1)