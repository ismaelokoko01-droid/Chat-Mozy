import random, string, requests, json
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock
from kivy.core.window import Window
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.list import OneLineAvatarListItem, ImageLeftWidget
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivy.properties import StringProperty, BooleanProperty
from kivy.metrics import dp

Window.softinput_mode = "below_target"
store = JsonStore('user_data.json')
FIREBASE_URL = "https://fipsapp-ffda0-default-rtdb.firebaseio.com/"

messages_data = {}

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
        color: (1, 1, 1, 1) if root.est_envoyeur else (0, 0, 0, 1)

ScreenManager:
    PageConnexion:
    PageAccueil:
    PageDiscussion:

<PageConnexion>:
    name: 'connexion'
    MDBoxLayout:
        orientation: 'vertical'
        padding: "20dp"
        spacing: "10dp"
        MDLabel:
            text: "Inscription Fips"
            halign: "center"
        MDTextField:
            id: nom
            hint_text: "Nom"
        MDTextField:
            id: email
            hint_text: "Email"
        MDFloatingActionButton:
            icon: "arrow-right"
            pos_hint: {"center_x": .5}
            on_release: app.verifier_et_sauvegarder(nom.text, email.text)

<PageAccueil>:
    name: 'accueil'
    MDBoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            title: "Fips App"
            right_action_items: [["account-circle", lambda x: app.afficher_profil()]]
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

class FipsApp(MDApp):
    contact_actuel = ""

    def build(self):
        return Builder.load_string(KV)

    def on_start(self):
        if store.exists('user'):
            self.root.current = 'accueil'
            self.verifier_invitations()
        else:
            self.root.current = 'connexion'

    def verifier_et_sauvegarder(self, nom, email):
        code_fips = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        user_data = {'nom': nom, 'code_fips': code_fips}
        store.put('user', **user_data)
        requests.put(f"{FIREBASE_URL}/utilisateurs/{code_fips}.json", json=user_data)
        self.root.current = 'accueil'

    def action_nouvelle_discussion(self):
        self.input_field = MDTextField(hint_text="Entrer le Code FIPS")
        self.dialog_ajout = MDDialog(title="Ajouter par Code", type="custom", content_cls=self.input_field,
            buttons=[MDFlatButton(text="ANNULER", on_release=lambda x: self.dialog_ajout.dismiss()),
                     MDFlatButton(text="INVITER", on_release=lambda x: self.valider_ajout_contact())])
        self.dialog_ajout.open()

    def valider_ajout_contact(self):
        code = self.input_field.text.upper()
        res = requests.get(f"{FIREBASE_URL}/utilisateurs/{code}.json").json()
        if res:
            requests.post(f"{FIREBASE_URL}/demandes/{res['nom']}.json", json={"de": store.get('user')['nom']})
            self.dialog_ajout.dismiss()

    def verifier_invitations(self):
        nom = store.get('user')['nom']
        req = requests.get(f"{FIREBASE_URL}/demandes/{nom}.json").json()
        if req:
            for id_d, info in req.items():
                self.afficher_invitation(id_d, info['de'])

    def afficher_invitation(self, id_d, nom_exp):
        dialog = MDDialog(title="Invitation", text=f"{nom_exp} veut discuter.",
            buttons=[MDFlatButton(text="REFUSER", on_release=lambda x: dialog.dismiss()),
                     MDFlatButton(text="ACCEPTER", on_release=lambda x: self.accepter(id_d, nom_exp, dialog))])
        dialog.open()

    def accepter(self, id_d, nom_exp, dialog):
        messages_data[nom_exp] = []
        self.charger_contacts()
        requests.delete(f"{FIREBASE_URL}/demandes/{store.get('user')['nom']}/{id_d}.json")
        dialog.dismiss()

    def charger_contacts(self):
        liste = self.root.get_screen('accueil').ids.conteneur_contacts
        liste.clear_widgets()
        for nom in messages_data.keys():
            item = OneLineAvatarListItem(text=nom)
            item.on_release = lambda n=nom: self.entrer_discussion(n)
            liste.add_widget(item)

    def envoyer_message(self, texte):
        if texte and self.contact_actuel:
            messages_data[self.contact_actuel].append(texte)
            self.root.get_screen('discussion').ids.conteneur_messages.add_widget(BulleMessage(message=texte))
            self.root.get_screen('discussion').ids.input_message.text = ""

    def entrer_discussion(self, nom):
        self.contact_actuel = nom
        self.root.current = 'discussion'

    def retour_accueil(self):
        self.root.current = 'accueil'

    def afficher_profil(self):
        MDDialog(title="Profil", text=f"Code: {store.get('user')['code_fips']}").open()

if __name__ == '__main__':
    FipsApp().run()
    
