import socket
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock

class ChatApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Zone d'affichage des messages (défilante)
        self.scroll = ScrollView(size_hint=(1, 0.8))
        self.chat_label = Label(text="=== Bienvenue dans le Chat ===\n", size_hint_y=None, halign='left', valign='top')
        self.chat_label.bind(texture_size=self.chat_label.setter('size'))
        self.scroll.add_widget(self.chat_label)
        self.layout.add_widget(self.scroll)
        
        # Zone d'écriture en bas
        self.input_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.2), spacing=10)
        self.message_input = TextInput(hint_text="Écris ton message ici...", multiline=False)
        self.send_button = Button(text="Envoyer", size_hint=(0.3, 1))
        self.send_button.bind(on_press=self.envoyer_message)
        
        self.input_layout.add_widget(self.message_input)
        self.input_layout.add_widget(self.send_button)
        self.layout.add_widget(self.input_layout)
        
        # Connexion réseau automatique en arrière-plan (Local pour le test)
        # Note : Pour tes amis, il faudra remplacer '127.0.0.1' par ton lien Termux/Ngrok
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect(('127.0.0.1', 5555))
            threading.Thread(target=self.recevoir_messages, daemon=True).start()
        except:
            self.chat_label.text += "[Erreur] Impossible de se connecter au serveur.\n"

        return self.layout

    def ajouter_message(self, message):
        self.chat_label.text += f"{message}\n"

    def recevoir_messages(self):
        while True:
            try:
                message = self.client.recv(1024).decode('utf-8')
                if message:
                    Clock.schedule_once(lambda dt, msg=message: self.ajouter_message(msg))
            except:
                break

    def envoyer_message(self, instance):
        texte = self.message_input.text.strip()
        if texte:
            try:
                self.client.send(f"Moi : {texte}".encode('utf-8'))
                self.ajouter_message(f"Moi : {texte}")
                self.message_input.text = ""
            except:
                self.ajouter_message("[Erreur] Message non envoyé.")

if __name__ == '__main__':
    ChatApp().run()
