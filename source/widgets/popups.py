from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from widgets.buttons import ResponsiveButton

class SetNamePopup(Popup):
    def __init__(self, set_name_callback, **kwargs):
        super().__init__(**kwargs)
        self.title = "Set Drawing Name"
        self.size_hint = (0.8, 0.4)
        self.set_name_callback = set_name_callback

        content = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(10)
        )
       
        self.input = TextInput(
            hint_text="Enter drawing name",
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            font_size=dp(16),
            padding=[dp(10), dp(10), dp(10), dp(10)]
        )
       
        save_button = ResponsiveButton(
            text="Set Name",
            size_hint_y=None,
            height=dp(50),
            background_color=(0.3, 0.6, 1, 1)
        )
        save_button.bind(on_press=self.on_save)

        content.add_widget(self.input)
        content.add_widget(save_button)
        self.content = content
        
        self.background_color = (0.9, 0.9, 0.9, 1)
        self.separator_color = (0.8, 0.8, 0.8, 1)

    def on_save(self, instance):
        name = self.input.text.strip()
        if name:
            self.set_name_callback(name)
            self.dismiss()