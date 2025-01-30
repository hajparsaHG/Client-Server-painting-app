from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.metrics import dp
from .buttons import CircularColorButton, EraserButton
from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivy.graphics import Color, Ellipse, Line
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import NumericProperty
from kivy.properties import ListProperty


class PencilSizeButton(ButtonBehavior, Widget):
    size_value = NumericProperty(2)
    color = ListProperty([1, 1, 1, 1])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(40), dp(40))
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        self.bind(color=self.update_canvas, size_value=self.update_canvas)
        
    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            # Draw white border circle
            Color(1, 1, 1, 1)
            Ellipse(pos=self.pos, size=self.size)
            # Draw inner colored circle with size indicator
            Color(*self.color)
            center_x = self.pos[0] + self.size[0]/2
            center_y = self.pos[1] + self.size[1]/2
            radius = min(self.size_value, 15)  # Cap the visual size
            Ellipse(pos=(center_x - radius, center_y - radius),
                   size=(radius * 2, radius * 2))

class PencilSizeDropDown(DropDown):
    def __init__(self, size_callback, **kwargs):
        super().__init__(**kwargs)
        self.size_callback = size_callback
        
        sizes = [2, 4, 6, 8, 10, 12]
        for size in sizes:
            btn = Button(
                text=f'{size}px',
                size_hint_y=None,
                height=dp(35),
                background_color=(0.9, 0.9, 0.9, 1)
            )
            btn.bind(on_release=lambda btn, s=size: self.select_size(s))
            self.add_widget(btn)

    def select_size(self, size):
        self.size_callback(size)
        self.dismiss()

class ColorDropDown(DropDown):
    def __init__(self, color_callback, **kwargs):
        super().__init__(**kwargs)
        self.color_callback = color_callback
        
        colors = {
            'White': (1, 1, 1, 1),
            'Gray': (0.5, 0.5, 0.5, 1),
            'Red': (1, 0, 0, 1),
            'Orange': (1, 0.65, 0, 1),
            'Yellow': (1, 1, 0, 1),
            'Green': (0, 1, 0, 1),
            'Blue': (0, 0, 1, 1),
            'Purple': (0.5, 0, 0.5, 1)
        }
        
        for color_name, color_value in colors.items():
            btn = CircularColorButton(color=color_value)
            btn.size = (dp(30), dp(30))
            btn.bind(on_release=lambda btn, color=color_value: self.select_color(color))
            self.add_widget(btn)

    def select_color(self, color):
        self.color_callback(color)
        self.dismiss()

class DrawingTools(BoxLayout):
    def __init__(self, color_callback, eraser_callback, pencil_size_callback, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(50)
        self.padding = [dp(10), dp(5)]
        self.spacing = dp(10)
        
        # Create color picker button
        self.color_button = CircularColorButton(color=[1, 1, 1, 1])
        self.color_button.bind(on_release=self.show_color_dropdown)
        
        # Create pencil size button
        self.pencil_button = PencilSizeButton(color=[1, 1, 1, 1])
        self.pencil_button.bind(on_release=self.show_pencil_size_dropdown)
        
        # Create eraser button
        self.eraser_button = EraserButton()
        self.eraser_button.bind(on_release=self.toggle_eraser)
        
        # Create dropdowns
        self.color_dropdown = ColorDropDown(self.on_color_select)
        self.pencil_dropdown = PencilSizeDropDown(self.on_pencil_size)
        
        # Add widgets to layout
        self.add_widget(self.color_button)
        self.add_widget(self.pencil_button)
        self.add_widget(self.eraser_button)
        
        # Store callbacks
        self.color_callback = color_callback
        self.eraser_callback = eraser_callback
        self.pencil_size_callback = pencil_size_callback

    def show_pencil_size_dropdown(self, instance):
        self.pencil_dropdown.open(instance)

    def on_pencil_size(self, size):
        self.pencil_button.size_value = size
        self.pencil_size_callback(size)
        self.eraser_button.active[0] = False

    def show_color_dropdown(self, instance):
        self.color_dropdown.open(instance)

    def update_color_button(self, color):
        self.color_button.color = color
        self.eraser_button.active[0] = False

    def toggle_eraser(self, instance):
        self.eraser_button.active[0] = not self.eraser_button.active[0]
        self.eraser_callback(self.eraser_button.active[0])

    def on_color_select(self, color):
        self.color_callback(color)
        self.eraser_button.active[0] = False

    def on_eraser_size(self, size):
        self.eraser_callback(True, size)