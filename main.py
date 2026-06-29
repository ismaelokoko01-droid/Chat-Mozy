from kivy.app import App
from kivy.uix.label import Label

class ChatApp(App):
    def build(self):
        return Label(text='Bienvenue dans Chat-Mozy !')

if __name__ == '__main__':
    ChatApp().run()
