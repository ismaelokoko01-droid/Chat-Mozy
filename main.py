import random
import string
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
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

Window.softinput_mode = "below_target"
store = JsonStore('user_data.json')

# Base de données des codes pour l'ajout
annuaire_codes = {"1234": "Brother Canada", "5678": "Ami Manga"}

messages_data = {
    "Ismaël OKOKO": [],
    "Brother Canada": [],
    "Ami Manga": []
}

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
            source: 'aaaaa/logo.png'
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
            MDBoxLayout:
                pos_hint: {"center_y": .5}
                adaptive_size: True
                spacing: "10dp"
                padding: ["50dp", 0, 0, 0]
                Image:
                    source: 'aaaaa/logo.png'
                    size_hint: None, None
                    size: "35dp", "35dp"
                MDLabel:
                    id: titre_contact
                    text: ""
                    font_style: "H6"
                    adaptive_width: True
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
        ScrollView:
            MDBoxLayout:
                id: conteneur_messages
                orientation: 'vertical'
                adaptive_height: True
                padding: "10dp"
                spacing: "10dp"
        
        MDBoxLayout:
            size_hint_y: None
            height: "70dp"
            padding: "10dp"
            spacing: "10dp"
            canvas.before:
                Color:
                    rgba: 0.95, 0.95, 0.95, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [30, 30, 30, 30]
            MDTextField:
                id: input_message
                hint_text: "Message..."
                mode: "fill"
                fill_color_normal: 0, 0, 0, 0
                line_color_normal: 0, 0, 0, 0
            MDIconButton:
                icon: "send"
                theme_icon_color: "Custom"
                icon_color: (0.6, 0.4, 0.9, 1)
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
        self.theme_cls.primary_palette = "DeepPurple"
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

    def filtrer_contacts(self, texte):
        liste = self.root.get_screen('accueil').ids.conteneur_contacts
        for item in liste.children:
            item.opacity = 1 if texte.lower() in item.text.lower() else 0
            item.disabled = False if texte.lower() in item.text.lower() else True

    def charger_contacts(self):
        liste = self.root.get_screen('accueil').ids.conteneur_contacts
        liste.clear_widgets()
        for nom in messages_data.keys():
            item = OneLineAvatarListItem(text=nom)
            item.add_widget(ImageLeftWidget(source='aaaaa/logo.png'))
            item.on_release = lambda n=nom: self.entrer_discussion(n)
            liste.add_widget(item)

    def afficher_profil(self):
        if store.exists('user'):
            user = store.get('user')
            code = user.get('code_fips', 'N/A')
            info = f"Nom : {user['nom']}\nPrénom : {user['prenom']}\nCode Fips : {code}"
            if not self.dialog:
                self.dialog = MDDialog(
                    title="Ton Profil",
                    text=info,
                    buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())],
                )
            else:
                self.dialog.title = "Ton Profil"
                self.dialog.text = info
            self.dialog.open()

    def envoyer_message(self, texte):
        if texte.strip() and self.contact_actuel:
            messages_data[self.contact_actuel].append(texte)
            conteneur = self.root.get_screen('discussion').ids.conteneur_messages
            conteneur.add_widget(BulleMessage(message=texte, est_envoyeur=True))
            self.root.get_screen('discussion').ids.input_message.text = ""

    def entrer_discussion(self, nom_contact):
        self.contact_actuel = nom_contact
        self.root.get_screen('discussion').ids.titre_contact.text = nom_contact
        conteneur = self.root.get_screen('discussion').ids.conteneur_messages
        conteneur.clear_widgets()
        for msg in messages_data[nom_contact]:
            conteneur.add_widget(BulleMessage(message=msg, est_envoyeur=True))
        self.root.transition.duration = 0
        self.root.current = 'discussion'

    def retour_accueil(self):
        self.root.transition.duration = 0
        self.root.current = 'accueil'

    def verifier_et_sauvegarder(self, nom, prenom, email, code):
        # Sécurité ajoutée
        if not nom.strip() or not prenom.strip() or not email.strip() or not code.strip():
            self.afficher_erreur("Tous les champs sont obligatoires.")
            return
        if "@" not in email or "." not in email:
            self.afficher_erreur("Email invalide.")
            return
        if not (code.isdigit() and 4 <= len(code) <= 6):
            self.afficher_erreur("Code doit contenir 4 à 6 chiffres.")
            return
        
        chars = string.ascii_uppercase + string.digits
        code_fips = ''.join(random.choices(chars, k=6))
        store.put('user', nom=nom, prenom=prenom, email=email, code=code, code_fips=code_fips)
        self.charger_contacts()
        self.root.current = 'accueil'

    def afficher_erreur(self, message):
        dialog = MDDialog(
            title="Erreur",
            text=message,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())],
        )
        dialog.open()

    def ouvrir_menu(self, button):
        menu_items = [{"text": "Déconnexion", "on_release": lambda: self.deconnecter()}]
        self.menu = MDDropdownMenu(caller=button, items=menu_items, width_mult=3)
        self.menu.open()
        
    def ouvrir_menu_action_rapide(self, button):
        menu_items = [
            {"text": "Nouvelle Discussion", "icon": "chat", "on_release": lambda: self.action_nouvelle_discussion()},
            {"text": "Scanner Code Fips", "icon": "qrcode-scan", "on_release": lambda: print("Scan")},
            {"text": "Inviter un ami", "icon": "share-variant", "on_release": lambda: print("Invite")}
        ]
        self.menu_action = MDDropdownMenu(caller=button, items=menu_items, width_mult=4)
        self.menu_action.open()

    def action_nouvelle_discussion(self):
        self.menu_action.dismiss()
        self.input_field = MDTextField(hint_text="Entrer le Code Fips")
        self.dialog_ajout = MDDialog(title="Ajouter par Code", type="custom", content_cls=self.input_field,
            buttons=[MDFlatButton(text="ANNULER", on_release=lambda x: self.dialog_ajout.dismiss()),
                     MDFlatButton(text="AJOUTER", on_release=lambda x: self.valider_ajout_contact())])
        self.dialog_ajout.open()

    def valider_ajout_contact(self):
        code_saisi = self.input_field.text.upper()
        if code_saisi in annuaire_codes:
            nom_ami = annuaire_codes[code_saisi]
            if nom_ami not in messages_data:
                messages_data[nom_ami] = []
                self.charger_contacts()
            self.dialog_ajout.dismiss()
        else:
            self.afficher_erreur("Code inconnu.")

    def deconnecter(self):
        if store.exists('user'): store.delete('user')
        if hasattr(self, 'menu'): self.menu.dismiss()
        self.root.current = 'connexion'

if __name__ == '__main__':
    FipsApp().run()
