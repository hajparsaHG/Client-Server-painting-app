import math
from kivy.metrics import dp
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Line, Ellipse
from kivy.core.window import Window

class DrawInput(Widget):
    def __init__(self, send_to_server_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.current_color = (1, 1, 1, 1)
        self.eraser_mode = False
        self.eraser_size = 30
        self.pencil_size = 2
        self.drawings = []
        self.send_to_server_callback = send_to_server_callback
        
        with self.canvas.before:
            Color(0, 0, 0, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)

    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def erase_at_point(self, pos):
        if self.send_to_server_callback:
            self.send_to_server_callback({
                "type": "erase",
                "x": pos[0],
                "y": pos[1],
                "radius": self.eraser_size
            })
            
        lines_to_remove = []
        for line in self.drawings:
            if self.line_intersects_circle(line, pos, self.eraser_size):
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

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.eraser_mode:
                self.erase_at_point(touch.pos)
            else:
                with self.canvas:
                    Color(*self.current_color)
                    line = Line(points=(touch.x, touch.y), width=self.pencil_size)
                    touch.ud["line"] = line
                    self.drawings.append(line)
                    if self.send_to_server_callback:
                        self.send_to_server_callback({
                            "type": "down",
                            "x": touch.x,
                            "y": touch.y,
                            "color": self.current_color,
                            "width": self.pencil_size,
                        })

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            if self.eraser_mode:
                self.erase_at_point(touch.pos)
            elif "line" in touch.ud:
                touch.ud["line"].points += (touch.x, touch.y)
                if self.send_to_server_callback:
                    self.send_to_server_callback({
                        "type": "move",
                        "x": touch.x,
                        "y": touch.y,
                    })
    def erase_all(self):
        for line in self.drawings[:]:  
            self.canvas.remove(line)
        self.drawings.clear()
        if self.send_to_server_callback:
            self.send_to_server_callback({
                "type": "erase_all"
            })

    def change_color(self, color):
        self.current_color = color
        self.eraser_mode = False

    def set_eraser_mode(self, active):
        self.eraser_mode = active

    def set_pencil_size(self, size):
        self.pencil_size = size

    def save_canvas(self, filepath):
        self.export_to_png(filepath)