import random, string, requests, os
from kivy.utils import platform
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.list import OneLineAvatarListItem
from plyer import notification

FIREBASE_URL = "https://fipsapp-ffda0-default-rtdb.firebaseio.com/"

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
        padding: "20dp"; spacing: "15dp"
        MDTextField: id: nom; hint_text: "Nom"
        MDTextField: id: prenom; hint_text: "Prénom"
        MDTextField: id: email; hint_text: "Email (ex: nom@domaine.com)"
        MDTextField: id: code_sec; hint_text: "Code secret"; password: True
        MDFloatingActionButton:
            icon: "check"; pos_hint: {"center_x": .5}
            on_release: app.verifier_et_sauvegarder(nom.text, prenom.text, email.text, code_sec.text)

<PageAccueil>:
    name: 'accueil'
    MDBoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            title: "Fips App"
            right_action_items: [["logout", lambda x: app.deconnecter()]]
        ScrollView:
            MDList:
                id: conteneur_contacts
    MDFloatingActionButton:
        icon: "plus"; pos_hint: {"right": 0.95, "bottom": 0.05}
        on_release: app.alerte("Info", "Ajout ami à venir")

<PageDiscussion>:
    name: 'discussion'
    MDBoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            title: "Moi (Notes)"
            left_action_items: [["arrow-left", lambda x: app.retour_accueil()]]
        ScrollView:
            MDList:
                id: conteneur_messages
        MDBoxLayout:
            size_hint_y: None; height: "60dp"; padding: "5dp"; spacing: "5dp"
            MDTextField:
                id: msg_input
                hint_text: "Écrire un message..."
            MDIconButton:
                icon: "send"
                on_release: app.envoyer_message(msg_input.text)
'''

class PageSplash(Screen): pass
class PageConnexion(Screen): pass
class PageAccueil(Screen): pass
class PageDiscussion(Screen): pass

class FipsApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # FIX 1 : Définition d'un emplacement de stockage 100% autorisé par Android
        if platform == 'android':
            dossier_data = self.user_data_dir
        else:
            dossier_data = "."
        self.store = JsonStore(os.path.join(dossier_data, 'user_data.json'))
        self.diag = None

    def build(self):
        return Builder.load_string(KV)

    def on_start(self):
        # FIX 2 : Demande en direct des permissions à l'écran de l'utilisateur (Android 13+)
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.INTERNET,
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.POST_NOTIFICATIONS
            ])
        Clock.schedule_once(self.route_vers_ecran, 3)

    def on_resume(self):
        # FIX 3 : On laisse vide pour empêcher l'application de crasher en boucle au démarrage
        pass

    def route_vers_ecran(self, dt):
        try:
            if self.store.exists('user'):
                self.root.current = 'accueil'
                Clock.schedule_once(lambda x: self.charger_contacts(), 0.2)
            else:
                self.root.current = 'connexion'
        except Exception:
            self.root.current = 'connexion'

    def charger_contacts(self):
        try:
            ecran_accueil = self.root.get_screen('accueil')
            if 'conteneur_contacts' in ecran_accueil.ids:
                liste = ecran_accueil.ids.conteneur_contacts
                liste.clear_widgets()
                item = OneLineAvatarListItem(text="Moi (Notes personnelles)")
                item.bind(on_release=lambda x: self.ouvrir_discussion())
                liste.add_widget(item)
        except Exception:
            pass

    def ouvrir_discussion(self):
        self.root.current = 'discussion'
        Clock.schedule_once(lambda x: self.charger_messages(), 0.1)

    def retour_accueil(self):
        self.root.current = 'accueil'

    def charger_messages(self):
        try:
            ecran_discussion = self.root.get_screen('discussion')
            if 'conteneur_messages' in ecran_discussion.ids:
                conteneur = ecran_discussion.ids.conteneur_messages
                conteneur.clear_widgets()
                if self.store.exists('messages_moi'):
                    for msg in self.store.get('messages_moi')['data']:
                        conteneur.add_widget(OneLineAvatarListItem(text=msg))
        except Exception:
            pass

    def envoyer_message(self, texte):
        if not texte: return
        try:
            msgs = self.store.get('messages_moi')['data'] if self.store.exists('messages_moi') else []
            msgs.append(texte)
            self.store.put('messages_moi', data=msgs)
            self.charger_messages()
            self.root.get_screen('discussion').ids.msg_input.text = ""
        except Exception:
            pass

    def verifier_et_sauvegarder(self, nom, prenom, email, code):
        if "@" not in email or "." not in email.split("@")[-1]:
            self.alerte("Erreur", "Email invalide")
            return
        if not all([nom, prenom, email, code]):
            self.alerte("Erreur", "Tous les champs sont requis")
            return

        code_fips = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        u_data = {'nom': nom, 'prenom': prenom, 'email': email, 'code_fips': code_fips}
        
        try:
            self.store.put('user', **u_data)
            requests.put(f"{FIREBASE_URL}/utilisateurs/{code_fips}.json", json=u_data, timeout=5)
            self.root.current = 'accueil'
            Clock.schedule_once(lambda x: self.charger_contacts(), 0.1)
        except Exception:
            # Mode hors-ligne : Permet d'accéder à l'application même sans internet
            self.root.current = 'accueil'
            Clock.schedule_once(lambda x: self.charger_contacts(), 0.1)

    def deconnecter(self):
        try:
            self.store.delete('user')
            self.root.current = 'connexion'
        except Exception:
            self.root.current = 'connexion'

    def alerte(self, titre, texte):
        self.diag = MDDialog(title=titre, text=texte, buttons=[MDFlatButton(text="OK", on_release=lambda x: self.diag.dismiss())])
        self.diag.open()

if __name__ == '__main__':
    FipsApp().run()
