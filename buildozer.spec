[app]
title = Fips App
package.name = fipsapp
package.domain = org.fips
source.include_exts = py,kv,png
source.dir = .
version = 1.0.0

# Dépendances (ajout de plyer pour les notifications)
requirements = python3,kivy,kivymd,pillow,urllib3,flask,requests,plyer

presplash.filename = %(source.dir)s/logo.png
icon.filename = %(source.dir)s/logo.png
orientation = portrait

# --- MODIFICATION : Ajout des permissions critiques pour notifications et arrière-plan ---
android.permissions = INTERNET,ACCESS_NETWORK_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,WAKE_LOCK,FOREGROUND_SERVICE,POST_NOTIFICATIONS

# Paramètres Android
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.presplash_color = #FFFFFF

# --- NOUVEAU : Configuration pour les services d'arrière-plan ---
# Si tu utilises un service pour écouter Firebase en continu
# android.services = FipsService:%(source.dir)s/service.py

[buildozer]
log_level = 2
warn_on_root = 1
