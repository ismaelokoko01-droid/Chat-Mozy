import random, string, requests, json
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock
from kivy.core.window import Window
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.card import MDCard
from kivymd.uix.list import OneLineAvatarListItem
from kivy.properties import StringProperty, BooleanProperty
from kivy.metrics import dp

# Configuration
FIREBASE_URL = "https://fipsapp-ffda0-default-rtdb.firebaseio.com/"
store = JsonStore('user_data.json')

KV = '''
ScreenManager:
    PageSplash:
    PageConnexion:
    PageAccueil:
    PageDiscussion:

<PageSplash>:
    name: 'splash'
    MDScreen:
        Image:
            source: 'logo.png'
            size_hint: None, None
            size: "200dp", "200dp"
            pos_hint: {"center_x": .5, "center_y": .5}

<PageConnexion>:
    name: 'connexion'
    MDBoxLayout:
        orientation: 'vertical'
        padding: "20dp"
        spacing: "15dp"
        MDLabel:
            text: "Inscription / Reconnexion"
            halign: "center"
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
            id: code_sec
            hint_text: "Code de reconnexion (secret)"
            password: True
        MDFloatingActionButton:
            icon: "check"
            pos_hint: {"center_x": .5}
            on_release: app.verifier_et_sauvegarder(nom.text, prenom.text, email.text, code_sec.text)

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
'''

class PageSplash(Screen): pass
class PageConnexion(Screen): pass
class PageAccueil(Screen): pass
class PageDiscussion(Screen): pass

class FipsApp(MDApp):
    def build(self):
        return Builder.load_string(KV)

    def on_start(self):
        # 1. Splash Screen pendant 3 secondes
        Clock.schedule_once(self.verifier_session, 3)

    def verifier_session(self, dt):
        if store.exists('user'):
            self.root.current = 'accueil'
            self.verifier_invitations()
        else:
            self.root.current = 'connexion'

    def verifier_et_sauvegarder(self, nom, prenom, email, code):
        if not all([nom, prenom, email, code]):
            self.afficher_message("Erreur", "Tous les champs sont requis.")
            return
            
        code_partage = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        user_data = {'nom': nom, 'prenom': prenom, 'email': email, 'code_reconnexion': code, 'code_fips': code_partage}
        store.put('user', **user_data)
        requests.put(f"{FIREBASE_URL}/utilisateurs/{code_partage}.json", json=user_data)
        self.root.current = 'accueil'

    def action_nouvelle_discussion(self):
        self.input_field = MDTextField(hint_text="Entrer le Code FIPS de l'ami")
        self.dialog_ajout = MDDialog(
            title="Ajouter par Code", 
            type="custom", 
            content_cls=self.input_field,
            buttons=[
                MDFlatButton(text="ANNULER", on_release=lambda x: self.dialog_ajout.dismiss()),
                MDFlatButton(text="VÉRIFIER", on_release=lambda x: self.verifier_code_ami())
            ]
        )
        self.dialog_ajout.open()

    def verifier_code_ami(self):
        code = self.input_field.text.upper()
        res = requests.get(f"{FIREBASE_URL}/utilisateurs/{code}.json").json()
        if res:
            # Pré-vérification : On affiche le nom
            self.dialog_ajout.dismiss()
            self.dialog_confirm = MDDialog(
                title="Ami trouvé",
                text=f"Confirmez-vous vouloir inviter {res['nom']} {res['prenom']} ?",
                buttons=[
                    MDFlatButton(text="ANNULER", on_release=lambda x: self.dialog_confirm.dismiss()),
                    MDFlatButton(text="INVITER", on_release=lambda x: self.envoyer_invitation(res['nom']))
                ]
            )
            self.dialog_confirm.open()
        else:
            self.afficher_message("Erreur", "Code introuvable.")

    def envoyer_invitation(self, nom_ami):
        requests.post(f"{FIREBASE_URL}/demandes/{nom_ami}.json", json={"de": store.get('user')['nom']})
        self.dialog_confirm.dismiss()
        self.afficher_message("Succès", "Invitation envoyée !")

    def verifier_invitations(self):
        nom = store.get('user')['nom']
        req = requests.get(f"{FIREBASE_URL}/demandes/{nom}.json").json()
        if req:
            for id_d, info in req.items():
                self.afficher_message("Nouvelle invitation", f"{info['de']} veut discuter.", self.accepter_invit)

    def accepter_invit(self, *args):
        # Logique d'acceptation ici...
        pass

    def afficher_message(self, titre, texte, callback=None):
        MDDialog(title=titre, text=texte, buttons=[MDFlatButton(text="OK", on_release=lambda x: self.stop_dialog(x, callback))]).open()

    def stop_dialog(self, instance, callback):
        instance.parent.parent.parent.parent.dismiss()
        if callback: callback()

    def afficher_profil(self):
        u = store.get('user')
        self.afficher_message("Profil", f"{u['nom']} {u['prenom']}\nCode FIPS: {u['code_fips']}")

if __name__ == '__main__':
    FipsApp().run()
        
