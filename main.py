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
from kivymd.uix.textfield import MDTextField
from kivy.properties import StringProperty, BooleanProperty
from kivy.metrics import dp

FIREBASE_URL = "https://fipsapp-ffda0-default-rtdb.firebaseio.com/"
Window.softinput_mode = "below_target"
store = JsonStore('user_data.json')

annuaire_codes = {"1234": "Brother Canada", "5678": "Ami Manga"}
messages_data = {"Brother Canada": [], "Ami Manga": []}

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

<PageConnexion>:
    name: 'connexion'
    MDBoxLayout:
        orientation: 'vertical'
        padding: "20dp"
        spacing: "10dp"
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
            hint_text: "Code secret"
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
        ScrollView:
            MDList:
                id: conteneur_contacts
    MDFloatingActionButton:
        icon: "plus"
        pos_hint: {"right": 0.95, "bottom": 0.05}
        on_release: app.action_nouvelle_discussion()

<PageDiscussion>:
    name: 'discussion'
    MDBoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            left_action_items: [["arrow-left", lambda x: app.retour_accueil()]]
            title: ""
            id: bar_discussion
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

    def obtenir_id_discussion(self, contact):
        nom_moi = store.get('user')['nom']
        noms = sorted([nom_moi, contact])
        return f"{noms[0]}_{noms[1]}"

    def charger_contacts(self):
        liste = self.root.get_screen('accueil').ids.conteneur_contacts
        liste.clear_widgets()
        for nom in messages_data.keys():
            item = OneLineAvatarListItem(text=nom)
            item.on_release = lambda n=nom: self.entrer_discussion(n)
            liste.add_widget(item)

    def envoyer_message(self, texte):
        if texte.strip() and self.contact_actuel:
            id_chat = self.obtenir_id_discussion(self.contact_actuel)
            payload = {"message": texte, "expediteur": store.get('user')['nom']}
            requests.post(f"{FIREBASE_URL}/discussions/{id_chat}.json", json=payload)
            self.root.get_screen('discussion').ids.input_message.text = ""

    def verifier_nouveaux_messages(self, dt):
        if self.contact_actuel:
            id_chat = self.obtenir_id_discussion(self.contact_actuel)
            try:
                reponse = requests.get(f"{FIREBASE_URL}/discussions/{id_chat}.json")
                if reponse.status_code == 200 and reponse.json():
                    conteneur = self.root.get_screen('discussion').ids.conteneur_messages
                    conteneur.clear_widgets()
                    data = reponse.json()
                    for key in data:
                        msg = data[key]
                        conteneur.add_widget(BulleMessage(message=msg['message'], est_envoyeur=(msg['expediteur'] == store.get('user')['nom'])))
            except: pass

    def entrer_discussion(self, nom_contact):
        self.contact_actuel = nom_contact
        self.root.get_screen('discussion').ids.bar_discussion.title = nom_contact
        self.root.current = 'discussion'
        Clock.schedule_interval(self.verifier_nouveaux_messages, 2)

    def retour_accueil(self):
        Clock.unschedule(self.verifier_nouveaux_messages)
        self.root.current = 'accueil'

    def verifier_et_sauvegarder(self, nom, prenom, email, code):
        code_fips = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        store.put('user', nom=nom, prenom=prenom, email=email, code=code, code_fips=code_fips)
        self.root.current = 'accueil'
        self.charger_contacts()

    def afficher_profil(self):
        user = store.get('user')
        dialog = MDDialog(title="Profil", text=f"Nom: {user['nom']}\nCode: {user['code_fips']}")
        dialog.open()

    def ouvrir_menu(self, button):
        menu = MDDropdownMenu(caller=button, items=[{"text": "Déconnexion", "on_release": lambda: self.deconnecter()}], width_mult=3)
        menu.open()

    def action_nouvelle_discussion(self):
        self.input_field = MDTextField(hint_text="Entrer le Code Fips")
        self.dialog = MDDialog(title="Ajouter contact", type="custom", content_cls=self.input_field,
            buttons=[MDFlatButton(text="AJOUTER", on_release=lambda x: self.valider_ajout_contact())])
        self.dialog.open()

    def valider_ajout_contact(self):
        code = self.input_field.text.upper()
        if code in annuaire_codes:
            nom = annuaire_codes[code]
            if nom not in messages_data:
                messages_data[nom] = []
                self.charger_contacts()
        self.dialog.dismiss()

    def deconnecter(self):
        store.delete('user')
        self.root.current = 'connexion'

if __name__ == '__main__':
    FipsApp().run()
        
