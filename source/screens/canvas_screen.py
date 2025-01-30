import os
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp
from kivy.properties import NumericProperty, StringProperty
from kivy.core.window import Window

from widgets.buttons import ResponsiveButton
from widgets.canvas import DrawInput
from widgets.tools import DrawingTools
from widgets.popups import SetNamePopup
from utils.constants import BUTTON_HEIGHT, PADDING, SPACING

class CanvasScreen(Screen):
    button_height = NumericProperty(BUTTON_HEIGHT)
    current_name = StringProperty("Untitled")

    def __init__(self, send_to_server_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.send_to_server_callback = send_to_server_callback
        self.draw_input = DrawInput(send_to_server_callback=send_to_server_callback)
        
        main_layout = BoxLayout(
            orientation='vertical',
            padding=PADDING,
            spacing=SPACING
        )
        
        self.drawing_tools = DrawingTools(
            color_callback=self.set_color,
            eraser_callback=self.set_eraser,
            pencil_size_callback=self.set_pencil_size
        )
        
        nav_tools_layout = BoxLayout(
            size_hint_y=None,
            height=self.button_height,
            spacing=SPACING
        )
        
        sys_layout = BoxLayout(size_hint_x=0.4, spacing=SPACING)
        
        # Set Name button
        self.set_name_button = ResponsiveButton(
            text='Set Name',
            on_press=self.open_set_name_popup
        )

        # Erase All button
        self.erase_all_button = ResponsiveButton(
            text='Erase All',
            on_press=self.erase_all
        )
        
        # Save button
        self.save_button = ResponsiveButton(
            text='Save',
            on_press=self.save_drawing
        )
        
        # Exit button
        self.exit_button = ResponsiveButton(
            text='Exit',
            on_press=self.exit_app
        )
        
        sys_layout.add_widget(self.set_name_button)
        sys_layout.add_widget(self.erase_all_button)  
        sys_layout.add_widget(self.save_button)
        sys_layout.add_widget(self.exit_button)
        
        nav_tools_layout.add_widget(sys_layout)
        
        main_layout.add_widget(self.drawing_tools)
        main_layout.add_widget(self.draw_input)
        main_layout.add_widget(nav_tools_layout)
        
        self.add_widget(main_layout)
        
        Window.bind(on_resize=self.update_layout)

    def set_pencil_size(self, size):
        self.draw_input.set_pencil_size(size)

    def set_color(self, color):
        self.draw_input.change_color(color)
        self.drawing_tools.update_color_button(color)

    def set_eraser(self, active):
        self.draw_input.set_eraser_mode(active)

    def update_layout(self, instance, width, height):
        self.button_height = height * 0.08

    def erase_all(self, instance):
        self.draw_input.erase_all()

    def set_drawing_name(self, name):
        self.current_name = name
        if self.send_to_server_callback:
            self.send_to_server_callback({
                "type": "set_title",
                "title": name
            })

    def open_set_name_popup(self, instance):
        popup = SetNamePopup(self.set_drawing_name)
        popup.open()

    def save_drawing(self, instance):
        if self.send_to_server_callback:
            self.send_to_server_callback({
                "type": "save",
                "filename": self.current_name
            })

    def exit_app(self, instance):
        if self.send_to_server_callback:
            self.send_to_server_callback({
                "type": "exit"
            })
        from kivy.app import App
        App.get_running_app().stop()