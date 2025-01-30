from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line
from kivy.metrics import dp
from kivy.properties import ListProperty
from kivy.core.window import Window

class ResponsiveButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self.update_text_size)
        Window.bind(on_resize=self.update_text_size)
        
    def update_text_size(self, *args):
        self.font_size = min(self.width / 10, self.height / 2)

class CircularColorButton(ButtonBehavior, Widget):
    color = ListProperty([1, 1, 1, 1])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(40), dp(40))
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        self.bind(color=self.update_canvas)
        
    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(1, 1, 1, 1)
            Ellipse(pos=self.pos, size=self.size)
            Color(*self.color)
            Ellipse(pos=(self.pos[0] + dp(2), self.pos[1] + dp(2)),
                   size=(self.size[0] - dp(4), self.size[1] - dp(4)))

class EraserButton(ButtonBehavior, Widget):
    active = ListProperty([False])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(40), dp(40))
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        self.bind(active=self.update_canvas)
        
    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(1, 1, 1, 1)
            Ellipse(pos=self.pos, size=self.size)
            Color(0.7, 0.7, 0.7, 1)
            Ellipse(pos=(self.pos[0] + dp(8), self.pos[1] + dp(8)),
                   size=(self.size[0] - dp(16), self.size[1] - dp(16)))
            if self.active[0]:
                Color(0, 0.8, 1, 1)
                Line(circle=(self.pos[0] + self.size[0]/2, 
                           self.pos[1] + self.size[1]/2,
                           self.size[0]/2 - dp(2)), width=2)