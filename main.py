import random
import string
import requests
import os
import base64
from datetime import datetime

from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock
from kivy.core.window import Window
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.list import OneLineAvatarListItem, TwoLineAvatarListItem, ImageLeftWidget
from kivymd.uix.card import MDCard
from kivymd.uix.textfield import MDTextField
from kivy.properties import StringProperty, BooleanProperty
from kivy.metrics import dp
from kivy.uix.image import AsyncImage
from kivymd.uix.boxlayout import MDBoxLayout

Window.softinput_mode = "below_target"
store = JsonStore('user_data.json')
FIREBASE_URL = "https://fipsapp-ffda0-default-rtdb.firebaseio.com"

# Fonctions utilitaires de chiffrement (Base64)
def chiffrer_texte(texte):
    try:
        encoded = base64.b64encode(texte.encode('utf-8')).decode('utf-8')
        return f"ENC:{encoded}"
    except Exception:
        return texte

def dechiffrer_texte(texte):
    try:
        if texte.startswith("ENC:"):
            raw = texte.replace("ENC:", "")
            return base64.b64decode(raw.encode('utf-8')).decode('utf-8')
        return texte
    except Exception:
        return texte

KV = '''
<BulleMessage>:
    size_hint: None, None
    width: min(label.texture_size[0] + dp(60), dp(270))
    height: label.texture_size[1] + dp(30)
    padding: dp(8)
    radius: [15, 15, 15, 15]
    md_bg_color: (0.6, 0.4, 0.9, 1) if root.est_envoyeur else (0.2, 0.2, 0.2, 1) if app.theme_cls.theme_style == "Dark" else (0.9, 0.9, 0.9, 1)
    pos_hint: {"right": 1} if root.est_envoyeur else {"left": 1}
    on_release: app.options_message(root)
    
    MDBoxLayout:
        orientation: 'vertical'
        spacing: dp(2)
        
        MDLabel:
            id: label
            text: root.message
            text_size: (dp(200), None)
            font_style: "Body1"
            color: (1, 1, 1, 1) if (root.est_envoyeur or app.theme_cls.theme_style == "Dark") else (0, 0, 0, 1)
            
        MDBoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(14)
            spacing: dp(4)
            pos_hint: {"right": 1}
            
            MDLabel:
                text: root.heure
                font_style: "Caption"
                font_size: "10sp"
                halign: "right"
                color: (1, 1, 1, 0.7) if (root.est_envoyeur or app.theme_cls.theme_style == "Dark") else (0.4, 0.4, 0.4, 1)
                
            MDIcon:
                icon: root.statut_icon
                font_size: "12sp"
                theme_text_color: "Custom"
                text_color: (1, 1, 1, 0.8) if root.est_envoyeur else (0.5, 0.5, 0.5, 1)

ScreenManager:
    PageDemarrage:
    PageConnexion:
    PageAccueil:
    PageDiscussion:

<PageDemarrage>:
    name: 'demarrage'
    MDScreen:
        Image:
            source: 'micro/logo.png'
            allow_stretch: True
            keep_ratio: True

<PageConnexion>:
    name: 'connexion'
    MDBoxLayout:
        orientation: 'vertical'
        padding: "20dp"
        spacing: "10dp"
        MDLabel:
            text: "Inscription Zelyph"
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
            title: "Zelyph app"
            right_action_items: [["account-clock", lambda x: app.afficher_demandes_recues()], ["qrcode", lambda x: app.afficher_qr_code()], ["theme-light-dark", lambda x: app.changer_theme()], ["account-circle", lambda x: app.afficher_profil()], ["dots-vertical", lambda x: app.ouvrir_menu(x)]]
        
        MDBoxLayout:
            size_hint_y: None
            height: "60dp"
            padding: "10dp"
            MDTextField:
                id: search_field
                hint_text: "Rechercher un contact..."
                mode: "round"
                icon_left: "magnify"
        
        ScrollView:
            MDList:
                id: conteneur_contacts
    
    MDFloatingActionButton:
        icon: "account-plus"
        pos_hint: {"right": 0.95, "bottom": 0.05}
        md_bg_color: (0.6, 0.4, 0.9, 1)
        on_release: app.ouvrir_dialogue_ajouter_code()

<PageDiscussion>:
    name: 'discussion'
    MDBoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            id: bar_discussion
            title: ""
            subtitle: "En ligne"
            left_action_items: [["arrow-left", lambda x: app.retour_accueil()]]
        
        ScrollView:
            id: scroll_messages
            MDBoxLayout:
                id: conteneur_messages
                orientation: 'vertical'
                adaptive_height: True
                padding: "10dp"
                spacing: "10dp"
        
        MDBoxLayout:
            size_hint_y: None
            height: "70dp"
            padding: "5dp"
            spacing: "5dp"
            
            MDIconButton:
                icon: "emoticon-outline"
                on_release: app.ouvrir_panneau_emojis(self)
                
            MDIconButton:
                icon: "paperclip"
                on_release: app.choisir_et_envoyer_image()
                
            MDTextField:
                id: input_message
                hint_text: "Message..."
                mode: "round"
                
            MDIconButton:
                icon: "send"
                theme_icon_color: "Custom"
                icon_color: (0.6, 0.4, 0.9, 1)
                on_release: app.envoyer_message(input_message.text)
'''

class BulleMessage(MDCard):
    msg_id = StringProperty("")
    message = StringProperty("")
    heure = StringProperty("")
    est_envoyeur = BooleanProperty(True)
    statut_icon = StringProperty("check-all")

class PageDemarrage(Screen): pass
class PageConnexion(Screen): pass
class PageAccueil(Screen): pass
class PageDiscussion(Screen): pass

class ZelyphApp(MDApp):
    dialog = None
    contact_actuel = ""
    mon_code_zelyph = ""
    sync_event = None
    messages_charges = set()

    def build(self):
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.theme_style = "Light"
        self.root = Builder.load_string(KV)
        self.root.current = 'demarrage'
        Clock.schedule_once(self.verifier_session, 3)
        return self.root

    def changer_theme(self):
        self.theme_cls.theme_style = "Dark" if self.theme_cls.theme_style == "Light" else "Light"

    def verifier_session(self, dt):
        if store.exists('user'):
            user = store.get('user')
            self.mon_code_zelyph = user.get('code_zelyph', '')
            self.root.current = 'accueil'
            self.charger_contacts()
        else:
            self.root.current = 'connexion'

    def charger_contacts(self):
        """Affiche uniquement les utilisateurs avec qui une relation d'amitié a été acceptée."""
        liste = self.root.get_screen('accueil').ids.conteneur_contacts
        liste.clear_widgets()
      
        item_moi = OneLineAvatarListItem(text="Moi (Note à soi-même)")
        item_moi.add_widget(ImageLeftWidget(source='micro/logo.png'))
        item_moi.on_release = lambda: self.entrer_discussion("Moi", self.mon_code_zelyph)
        liste.add_widget(item_moi)
        
        try:
            # Récupérer la liste d'amis acceptés
            amis = requests.get(f"{FIREBASE_URL}/friends/{self.mon_code_zelyph}.json").json() or {}
            
            for code_ami in amis.keys():
                user_info = requests.get(f"{FIREBASE_URL}/users/{code_ami}.json").json()
                if user_info:
                    nom_affichage = f"{user_info.get('prenom', '')} {user_info.get('nom', '')}".strip()
                    avatar_url = user_info.get('avatar_url', 'micro/logo.png')
                    
                    item = OneLineAvatarListItem(text=nom_affichage)
                    item.add_widget(ImageLeftWidget(source=avatar_url))
                    item.on_release = lambda n=nom_affichage, c=code_ami: self.entrer_discussion(n, c)
                    liste.add_widget(item)
        except Exception as e:
            print("Erreur chargement contacts :", e)

    # --- NOUVEAU : Ajouter un ami via son code ---
    def ouvrir_dialogue_ajouter_code(self):
        self.input_code_ami = MDTextField(hint_text="Entrez le Code Zelyph (ex: ABC123)")
        
        self.dialog_add = MDDialog(
            title="Ajouter un contact",
            type="custom",
            content_cls=self.input_code_ami,
            buttons=[
                MDFlatButton(text="Annuler", on_release=lambda x: self.dialog_add.dismiss()),
                MDFlatButton(text="Rechercher", on_release=lambda x: self.rechercher_utilisateur_par_code(self.input_code_ami.text.strip().upper()))
            ]
        )
        self.dialog_add.open()

    def rechercher_utilisateur_par_code(self, code_cible):
        if not code_cible or code_cible == self.mon_code_zelyph:
            return
            
        if hasattr(self, 'dialog_add'):
            self.dialog_add.dismiss()

        try:
            user_info = requests.get(f"{FIREBASE_URL}/users/{code_cible}.json").json()
            if user_info:
                nom_complet = f"{user_info.get('prenom', '')} {user_info.get('nom', '')}".strip()
                self.demander_confirmation_invitation(code_cible, nom_complet)
            else:
                self.afficher_message_info("Erreur", "Aucun utilisateur trouvé avec ce code.")
        except Exception as e:
            print("Erreur recherche :", e)

    def demander_confirmation_invitation(self, code_cible, nom_complet):
        self.dialog_confirm = MDDialog(
            title="Profil trouvé",
            text=f"Voulez-vous envoyer une invitation à :\n\n👤 {nom_complet} (Code: {code_cible}) ?",
            buttons=[
                MDFlatButton(text="Annuler", on_release=lambda x: self.dialog_confirm.dismiss()),
                MDFlatButton(text="Envoyer l'invitation", on_release=lambda x: self.envoyer_invitation(code_cible))
            ]
        )
        self.dialog_confirm.open()

    def envoyer_invitation(self, code_cible):
        try:
            my_user = store.get('user')
            my_nom = f"{my_user.get('prenom', '')} {my_user.get('nom', '')}".strip()
            
            invitation_data = {
                "expediteur_code": self.mon_code_zelyph,
                "expediteur_nom": my_nom,
                "statut": "en_attente"
            }
            requests.put(f"{FIREBASE_URL}/demandes/{code_cible}/{self.mon_code_zelyph}.json", json=invitation_data)
            self.dialog_confirm.dismiss()
            self.afficher_message_info("Succès", f"Invitation envoyée à {code_cible} !")
        except Exception as e:
            print("Erreur envoi invitation :", e)

    # --- NOUVEAU : Afficher et Accepter les demandes reçues ---
    def afficher_demandes_recues(self):
        try:
            demandes = requests.get(f"{FIREBASE_URL}/demandes/{self.mon_code_zelyph}.json").json() or {}
            
            conteneur = MDBoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
            conteneur.bind(minimum_height=conteneur.setter('height'))

            if not demandes:
                conteneur.add_widget(MDFlatButton(text="Aucune demande en attente"))
            else:
                for code_exp, data in demandes.items():
                    nom_exp = data.get('expediteur_nom', 'Inconnu')
                    
                    item = TwoLineAvatarListItem(
                        text=nom_exp,
                        secondary_text=f"Code: {code_exp}"
                    )
                    item.add_widget(ImageLeftWidget(source='micro/logo.png'))
                    
                    # Clic pour accepter/refuser
                    item.on_release = lambda c=code_exp, n=nom_exp: self.choisir_accepter_refuser(c, n)
                    conteneur.add_widget(item)

            self.dialog_demandes = MDDialog(
                title="Demandes d'amis reçues",
                type="custom",
                content_cls=conteneur,
                buttons=[MDFlatButton(text="Fermer", on_release=lambda x: self.dialog_demandes.dismiss())]
            )
            self.dialog_demandes.open()

        except Exception as e:
            print("Erreur chargement demandes :", e)

    def choisir_accepter_refuser(self, code_exp, nom_exp):
        if hasattr(self, 'dialog_demandes'):
            self.dialog_demandes.dismiss()

        def accepter(x):
            # 1. Ajouter aux amis pour l'utilisateur A et B
            requests.put(f"{FIREBASE_URL}/friends/{self.mon_code_zelyph}/{code_exp}.json", json=True)
            requests.put(f"{FIREBASE_URL}/friends/{code_exp}/{self.mon_code_zelyph}.json", json=True)
            # 2. Supprimer la demande
            requests.delete(f"{FIREBASE_URL}/demandes/{self.mon_code_zelyph}/{code_exp}.json")
            
            self.dialog_choix.dismiss()
            self.charger_contacts()
            self.afficher_message_info("Ami ajouté", f"Vous êtes maintenant ami avec {nom_exp} !")

        def refuser(x):
            requests.delete(f"{FIREBASE_URL}/demandes/{self.mon_code_zelyph}/{code_exp}.json")
            self.dialog_choix.dismiss()

        self.dialog_choix = MDDialog(
            title="Invitation",
            text=f"Voulez-vous accepter l'invitation de {nom_exp} ?",
            buttons=[
                MDFlatButton(text="Refuser", theme_text_color="Error", on_release=refuser),
                MDFlatButton(text="Accepter", on_release=accepter)
            ]
        )
        self.dialog_choix.open()

    def afficher_message_info(self, titre, message):
        dialog_info = MDDialog(
            title=titre,
            text=message,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog_info.dismiss())]
        )
        dialog_info.open()

    # --- Restes des fonctions classiques ---
    def verifier_et_sauvegarder(self, nom, prenom, email, code):
        if not nom.strip() or not prenom.strip() or not email.strip() or not code.strip():
            return
        code_zelyph = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        self.mon_code_zelyph = code_zelyph
        user_data = {
            "nom": nom, 
            "prenom": prenom, 
            "email": email, 
            "code_zelyph": code_zelyph,
            "avatar_url": "micro/logo.png"
        }
        store.put('user', **user_data)
        
        try:
            requests.put(f"{FIREBASE_URL}/users/{code_zelyph}.json", json=user_data)
        except Exception as e:
            print("Erreur :", e)
            
        self.charger_contacts()
        self.root.current = 'accueil'

    def entrer_discussion(self, nom_contact, code_contact):
        self.contact_actuel = code_contact
        self.root.get_screen('discussion').ids.bar_discussion.title = nom_contact
        self.root.current = 'discussion'
        
        self.messages_charges.clear()
        conteneur = self.root.get_screen('discussion').ids.conteneur_messages
        conteneur.clear_widgets()
        
        self.charger_messages()
        if self.sync_event: self.sync_event.cancel()
        self.sync_event = Clock.schedule_interval(lambda dt: self.charger_messages(), 2)

    def charger_messages(self):
        if not self.contact_actuel: return
        chat_id = "_".join(sorted([self.mon_code_zelyph, self.contact_actuel]))
        conteneur = self.root.get_screen('discussion').ids.conteneur_messages
        scroll = self.root.get_screen('discussion').ids.scroll_messages
        
        try:
            res = requests.get(f"{FIREBASE_URL}/chats/{chat_id}.json").json()
            if res:
                nouveau_msg_ajoute = False
                for msg_id, msg_data in res.items():
                    if msg_id not in self.messages_charges:
                        self.messages_charges.add(msg_id)
                        est_moi = msg_data.get('expediteur') == self.mon_code_zelyph
                        texte_clair = dechiffrer_texte(msg_data.get('texte', ''))
                        heure_msg = msg_data.get('heure', '')
                        
                        conteneur.add_widget(
                            BulleMessage(
                                msg_id=msg_id,
                                message=texte_clair, 
                                heure=heure_msg,
                                est_envoyeur=est_moi, 
                                statut_icon="check-all"
                            )
                        )
                        nouveau_msg_ajoute = True
                
                if nouveau_msg_ajoute:
                    Clock.schedule_once(lambda dt: setattr(scroll, 'scroll_y', 0), 0.1)
        except Exception as e:
            print("Erreur synchro :", e)

    def envoyer_message(self, texte):
        if texte.strip() and self.contact_actuel:
            chat_id = "_".join(sorted([self.mon_code_zelyph, self.contact_actuel]))
            texte_chiffre = chiffrer_texte(texte)
            heure_actuelle = datetime.now().strftime("%H:%M")
            
            msg_payload = {
                "expediteur": self.mon_code_zelyph, 
                "texte": texte_chiffre,
                "heure": heure_actuelle
            }
            try:
                requests.post(f"{FIREBASE_URL}/chats/{chat_id}.json", json=msg_payload)
            except Exception as e:
                print("Erreur envoi :", e)
            self.root.get_screen('discussion').ids.input_message.text = ""
            self.charger_messages()

    def options_message(self, bulle):
        if not bulle.est_envoyeur:
            return  
            
        def supprimer_action(x):
            chat_id = "_".join(sorted([self.mon_code_zelyph, self.contact_actuel]))
            try:
                requests.delete(f"{FIREBASE_URL}/chats/{chat_id}/{bulle.msg_id}.json")
            except Exception as e:
                print("Erreur suppression :", e)
            
            conteneur = self.root.get_screen('discussion').ids.conteneur_messages
            conteneur.remove_widget(bulle)
            if bulle.msg_id in self.messages_charges:
                self.messages_charges.remove(bulle.msg_id)
            self.dialog_option.dismiss()

        self.dialog_option = MDDialog(
            title="Option du message",
            text="Voulez-vous supprimer ce message ?",
            buttons=[
                MDFlatButton(text="Annuler", on_release=lambda x: self.dialog_option.dismiss()),
                MDFlatButton(text="Supprimer", theme_text_color="Error", on_release=supprimer_action),
            ],
        )
        self.dialog_option.open()

    def ouvrir_panneau_emojis(self, button):
        emojis = ["👍", "❤️", "😂", "🔥", "🎉", "😊", "🙏", "😎"]
        menu_items = [{"text": e, "on_release": lambda x=e: self.ajouter_emoji(x)} for e in emojis]
        self.menu_emoji = MDDropdownMenu(caller=button, items=menu_items, width_mult=2)
        self.menu_emoji.open()

    def ajouter_emoji(self, emoji):
        input_field = self.root.get_screen('discussion').ids.input_message
        input_field.text += emoji
        if hasattr(self, 'menu_emoji'):
            self.menu_emoji.dismiss()

    def choisir_et_envoyer_image(self):
        self.dialog_img = MDDialog(
                        title="Envoyer une image",
            text="Choisissez une photo de démonstration :",
            buttons=[
                MDFlatButton(text="Photo 1", on_release=lambda x: self.envoyer_image_simulee("photo_1.jpg")),
                MDFlatButton(text="Photo 2", on_release=lambda x: self.envoyer_image_simulee("photo_2.jpg")),
                MDFlatButton(text="Annuler", on_release=lambda x: self.dialog_img.dismiss()),
            ],
        )
        self.dialog_img.open()

    def envoyer_image_simulee(self, nom_photo):
        self.envoyer_message(f"📷 Image : {nom_photo}")
        if hasattr(self, 'dialog_img'):
            self.dialog_img.dismiss()

    def afficher_qr_code(self):
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={self.mon_code_zelyph}"
        img_qr = AsyncImage(source=qr_url, size_hint=(None, None), size=(dp(200), dp(200)), pos_hint={'center_x': 0.5})
        
        self.dialog_qr = MDDialog(
            title=f"Mon QR Code ({self.mon_code_zelyph})",
            type="custom",
            content_cls=img_qr,
            buttons=[MDFlatButton(text="Fermer", on_release=lambda x: self.dialog_qr.dismiss())]
        )
        self.dialog_qr.open()

    def retour_accueil(self):
        if self.sync_event: self.sync_event.cancel()
        self.root.current = 'accueil'

    def afficher_profil(self):
        if store.exists('user'):
            user = store.get('user')
            info = f"Nom : {user.get('nom', '')}\nPrénom : {user.get('prenom', '')}\nEmail : {user.get('email', '')}\nCode Zelyph : {self.mon_code_zelyph}"
            
            self.dialog = MDDialog(
                title="Mon Profil", 
                text=info, 
                buttons=[
                    MDFlatButton(text="Modifier", on_release=lambda x: self.ouvrir_modification_profil()),
                    MDFlatButton(text="Fermer", on_release=lambda x: self.dialog.dismiss())
                ]
            )
            self.dialog.open()

    def ouvrir_modification_profil(self):
        if self.dialog:
            self.dialog.dismiss()
            
        user = store.get('user') if store.exists('user') else {}
        
        conteneur_mod = MDBoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, height=dp(180))
        
        self.input_edit_nom = MDTextField(text=user.get('nom', ''), hint_text="Nouveau nom")
        self.input_edit_prenom = MDTextField(text=user.get('prenom', ''), hint_text="Nouveau prénom")
        self.input_edit_avatar = MDTextField(text=user.get('avatar_url', ''), hint_text="Lien URL Image de Profil")
        
        conteneur_mod.add_widget(self.input_edit_nom)
        conteneur_mod.add_widget(self.input_edit_prenom)
        conteneur_mod.add_widget(self.input_edit_avatar)
        
        self.dialog_edit = MDDialog(
            title="Modifier le profil",
            type="custom",
            content_cls=conteneur_mod,
            buttons=[
                MDFlatButton(text="Annuler", on_release=lambda x: self.dialog_edit.dismiss()),
                MDFlatButton(text="Enregistrer", on_release=lambda x: self.sauvegarder_modification_profil()),
            ]
        )
        self.dialog_edit.open()

    def sauvegarder_modification_profil(self):
        nouveau_nom = self.input_edit_nom.text.strip()
        nouveau_prenom = self.input_edit_prenom.text.strip()
        nouvel_avatar = self.input_edit_avatar.text.strip() or "micro/logo.png"
        
        if not nouveau_nom or not nouveau_prenom:
            return
            
        if store.exists('user'):
            user = store.get('user')
            user['nom'] = nouveau_nom
            user['prenom'] = nouveau_prenom
            user['avatar_url'] = nouvel_avatar
            store.put('user', **user)
            
            try:
                requests.patch(f"{FIREBASE_URL}/users/{self.mon_code_zelyph}.json", json={
                    "nom": nouveau_nom,
                    "prenom": nouveau_prenom,
                    "avatar_url": nouvel_avatar
                })
            except Exception as e:
                print("Erreur mise à jour profil Firebase :", e)
                
        if hasattr(self, 'dialog_edit'):
            self.dialog_edit.dismiss()
            
        self.charger_contacts()

    def ouvrir_menu(self, button):
        menu_items = [{"text": "Déconnexion", "on_release": lambda: self.deconnecter()}]
        self.menu = MDDropdownMenu(caller=button, items=menu_items, width_mult=3)
        self.menu.open()

    def deconnecter(self):
        if store.exists('user'): store.delete('user')
        if hasattr(self, 'menu'): self.menu.dismiss()
        if self.sync_event: self.sync_event.cancel()
        self.root.current = 'connexion'

if __name__ == '__main__':
    ZelyphApp().run()
