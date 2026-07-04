import random
import string
import requests
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.storage.jsonstore import JsonStore
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.properties import StringProperty, BooleanProperty
from kivymd.uix.card import MDCard
from kivy.metrics import dp

# URL Firebase (la tienne)
FIREBASE_URL = "https://fipsapp-ffda0-default-rtdb.firebaseio.com/"
store = JsonStore('user_data.json')

KV = '''
ScreenManager:
    PageConnexion:
    PageAccueil:
    PageDiscussion:

<PageConnexion>:
    name: 'connexion'
    MDBoxLayout:
        orientation: 'vertical'
        padding: "20dp"
        MDLabel:
            text: "Bienvenue sur FipsApp"
            halign: "center"
        MDTextField:
            id: nom
            hint_text: "Nom"
        MDFloatingActionButton:
            icon: "arrow-right"
            pos_hint: {"center_x": .5}
            on_release: app.verifier_et_sauvegarder(nom.text)

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
            title: "Discussion"
            left_action_items: [["arrow-left", lambda x: app.retour_accueil()]]
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

class FipsApp(MDApp):
    # C'est ici que tu gardes TA logique d'isolation
    id_discussion_actuelle = "" 

    def build(self):
        return Builder.load_string(KV)

    def on_start(self):
        if store.exists('user'):
            self.root.current = 'accueil'
        else:
            self.root.current = 'connexion'

    def verifier_et_sauvegarder(self, nom):
        code_fips = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        user_data = {'nom': nom, 'code_fips': code_fips}
        store.put('user', **user_data)
        # Enregistrement global pour que les gens puissent te trouver
        requests.put(f"{FIREBASE_URL}/utilisateurs/{code_fips}.json", json=user_data)
        self.root.current = 'accueil'

    # --- La nouvelle fonctionnalité sécurisée ---
    def action_nouvelle_discussion(self):
        self.input_field = MDTextField(hint_text="Entrer le Code FIPS")
        self.label_info = MDLabel(text="Nom: -", theme_text_color="Secondary")
        box = MDBoxLayout(orientation='vertical', adaptive_height=True, spacing="10dp")
        box.add_widget(self.input_field)
        box.add_widget(self.label_info)
        
        self.dialog = MDDialog(title="Ajouter un contact", type="custom", content_cls=box,
            buttons=[
                MDFlatButton(text="VÉRIFIER", on_release=lambda x: self.verifier_code()),
                MDFlatButton(text="INVITER", on_release=lambda x: self.envoyer_invitation())
            ])
        self.dialog.open()

    def verifier_code(self):
        code = self.input_field.text.upper()
        res = requests.get(f"{FIREBASE_URL}/utilisateurs/{code}.json").json()
        self.label_info.text = f"Trouvé : {res['nom']}" if res else "Code inconnu"

    def envoyer_invitation(self):
        code = self.input_field.text.upper()
        res = requests.get(f"{FIREBASE_URL}/utilisateurs/{code}.json").json()
        if res:
            # On envoie une demande dans le dossier de la personne
            nom_ami = res['nom']
            requests.post(f"{FIREBASE_URL}/demandes/{nom_ami}.json", json={"de": store.get('user')['nom'], "code": code})
            self.dialog.dismiss()

    # --- TA logique de messagerie (inchangée) ---
    def envoyer_message(self, texte):
        if texte and self.id_discussion_actuelle:
            nom_moi = store.get('user')['nom']
            # On envoie DANS LE DOSSIER UNIQUE (id_discussion_actuelle)
            requests.post(f"{FIREBASE_URL}/discussions/{self.id_discussion_actuelle}.json", 
                          json={"message": texte, "expediteur": nom_moi})
            self.root.get_screen('discussion').ids.input_message.text = ""

    def retour_accueil(self):
        self.root.current = 'accueil'

    def afficher_profil(self):
        user = store.get('user')
        MDDialog(title="Mon Profil", text=f"Nom: {user['nom']}\nCode: {user['code_fips']}").open()

if __name__ == '__main__':
    FipsApp().run()
    
