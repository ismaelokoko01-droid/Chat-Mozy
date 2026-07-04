import random
import string
import requests
import json
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock
from kivy.core.window import Window
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDIconButton, MDFloatingActionButton
from kivymd.uix.list import OneLineAvatarListItem, ImageLeftWidget
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivy.properties import StringProperty, BooleanProperty
from kivy.metrics import dp

# URL Firebase
FIREBASE_URL = "https://fipsapp-ffda0-default-rtdb.firebaseio.com/"

Window.softinput_mode = "below_target"
store = JsonStore('user_data.json')

annuaire_codes = {"1234": "Brother Canada", "5678": "Ami Manga"}
messages_data = {"Ismaël OKOKO": [], "Brother Canada": [], "Ami Manga": []}

KV = '''
<BulleMessage>:
    size_hint: None, None
    width: min(label.texture_size[0] + dp(30), dp(250))
    height: label.texture_size[1] + dp(20)
    padding: dp(10)
    radius: [15, 15, 15, 15]
    md_bg_color: (0.6, 0.4, 0.9, 1) if root.est_envoyeur else (0.9, 0.9, 0.9, 1)
    pos_hint: {"right": 1} if root.est_envoyeur else {"left": 1}
    MDLabel:
        id: label
        text: root.message
        text_size: (dp(230), None)
        halign: "left"
        color: (1, 1, 1, 1) if root.est_envoyeur else (0, 0, 0, 1)

ScreenManager:
    PageDemarrage:
    PageConnexion:
    PageAccueil:
    PageDiscussion:

<PageDemarrage>:
    name: 'demarrage'
    MDScreen:
        md_bg_color: 1, 1, 1, 1
        Image:
            source: 'logo.png'
            allow_stretch: True
            keep_ratio: True

<PageConnexion>:
    name: 'connexion'
    MDBoxLayout:
        orientation: 'vertical'
        padding: "20dp"
        spacing: "10dp"
        MDLabel:
            text: "Inscription Fips"
            halign: "center"
            font_style: "H4"
        MDTextField:
            id: nom
            hint_text: "Nom"
        MDTextField:
            id: prenom
            hint_text: "Prénom"
        MDTextField:
            id: email
            hint_text: "Email"
        MDTextField:
            id: code
            hint_text: "Code secret (4-6 chiffres)"
            password: True
        MDFloatingActionButton:
            icon: "arrow-right"
            pos_hint: {"center_x": .5}
            on_release: app.verifier_et_sauvegarder(nom.text, prenom.text, email.text, code.text)

<PageAccueil>:
    name: 'accueil'
    MDBoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            title: "Fips App"
            right_action_items: [["account-circle", lambda x: app.afficher_profil()], ["dots-vertical", lambda x: app.ouvrir_menu(x)]]
        MDBoxLayout:
            size_hint_y: None
            height: "60dp"
            padding: "10dp"
            MDTextField:
                id: search_field
                hint_text: "Rechercher..."
                mode: "round"
                icon_left: "magnify"
                on_text: app.filtrer_contacts(self.text)
        ScrollView:
            MDList:
                id: conteneur_contacts
    MDFloatingActionButton:
        icon: "plus"
        pos_hint: {"right": 0.95, "bottom": 0.05}
        md_bg_color: (0.6, 0.4, 0.9, 1)
        on_release: app.ouvrir_menu_action_rapide(self)

<PageDiscussion>:
    name: 'discussion'
    MDBoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            id: bar_discussion
            left_action_items: [["arrow-left", lambda x: app.retour_accueil()]]
            MDLabel:
                id: titre_contact
                text: ""
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
        ScrollView:
            MDBoxLayout:
                id: conteneur_messages
                orientation: 'vertical'
                adaptive_height: True
        MDBoxLayout:
            size_hint_y: None
            height: "70dp"
            MDTextField:
                id: input_message
                hint_text: "Message..."
            MDIconButton:
                icon: "send"
                on_release: app.envoyer_message(input_message.text)
'''

class BulleMessage(MDCard):
    message = StringProperty()
    est_envoyeur = BooleanProperty(True)

class PageDemarrage(Screen): pass
class PageConnexion(Screen): pass
class PageAccueil(Screen): pass
class PageDiscussion(Screen): pass

class FipsApp(MDApp):
    dialog = None
    contact_actuel = ""

    def build(self):
        self.root = Builder.load_string(KV)
        self.root.current = 'demarrage'
        Clock.schedule_once(self.verifier_session, 3)
        return self.root

    def verifier_session(self, dt):
        if store.exists('user'):
            self.root.current = 'accueil'
            self.charger_contacts()
        else:
            self.root.current = 'connexion'

    def charger_contacts(self):
        liste = self.root.get_screen('accueil').ids.conteneur_contacts
        liste.clear_widgets()
        for nom in messages_data.keys():
            item = OneLineAvatarListItem(text=nom)
            item.add_widget(ImageLeftWidget(source='logo.png'))
            item.on_release = lambda n=nom: self.entrer_discussion(n)
            liste.add_widget(item)

    def envoyer_message(self, texte):
        if texte.strip() and self.contact_actuel:
            # Envoi Firebase
            nom_expediteur = store.get('user')['nom']
            payload = {"message": texte, "expediteur": nom_expediteur}
            requests.post(f"{FIREBASE_URL}/messages/{self.contact_actuel}.json", json=payload)
            self.root.get_screen('discussion').ids.input_message.text = ""

    def verifier_nouveaux_messages(self, dt):
        if self.contact_actuel:
            try:
                reponse = requests.get(f"{FIREBASE_URL}/messages/{self.contact_actuel}.json")
                if reponse.status_code == 200 and reponse.json():
                    conteneur = self.root.get_screen('discussion').ids.conteneur_messages
                    conteneur.clear_widgets()
                    data = reponse.json()
                    for key in data:
                        msg = data[key]
                        est_moi = (msg['expediteur'] == store.get('user')['nom'])
                        conteneur.add_widget(BulleMessage(message=msg['message'], est_envoyeur=est_moi))
            except: pass

    def entrer_discussion(self, nom_contact):
        self.contact_actuel = nom_contact
        self.root.get_screen('discussion').ids.titre_contact.text = nom_contact
        self.root.current = 'discussion'
        # Démarrer la surveillance Firebase
        Clock.schedule_interval(self.verifier_nouveaux_messages, 2)

    def retour_accueil(self):
        Clock.unschedule(self.verifier_nouveaux_messages)
        self.root.current = 'accueil'

    # --- GARDER TOUTES TES FONCTIONS D'ORIGINE ---
    def verifier_et_sauvegarder(self, nom, prenom, email, code):
        code_fips = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        store.put('user', nom=nom, prenom=prenom, email=email, code=code, code_fips=code_fips)
        self.charger_contacts()
        self.root.current = 'accueil'

    def afficher_profil(self): pass # Ta logique ici
    def filtrer_contacts(self, texte): pass # Ta logique ici
    def ouvrir_menu(self, button): pass # Ta logique ici
    def ouvrir_menu_action_rapide(self, button): pass # Ta logique ici
    def deconnecter(self): 
        store.delete('user')
        self.root.current = 'connexion'

if __name__ == '__main__':
    FipsApp().run()
