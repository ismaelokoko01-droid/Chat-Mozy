[app]
title = Fips App
package.name = fipsapp
package.domain = org.fips
source.include_exts = py,kv,png
source.dir = .
version = 1.0.0

# --- CORRECTION : Ajout de l'API cible et mode d'affichage ---
requirements = python3,kivy,kivymd,pillow,urllib3,flask,requests,plyer

presplash.filename = %(source.dir)s/logo.png
icon.filename = %(source.dir)s/logo.png
orientation = portrait

# Permissions Android complètes
android.permissions = INTERNET,ACCESS_NETWORK_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,WAKE_LOCK,FOREGROUND_SERVICE,POST_NOTIFICATIONS

# --- IMPORTANT : Configuration pour Android 13+ (API 33) ---
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.presplash_color = #FFFFFF

# Ajout du support pour les services (à décommenter si tu crées le fichier service.py)
# android.services = FipsService:%(source.dir)s/service.py

[buildozer]
log_level = 2
warn_on_root = 1
