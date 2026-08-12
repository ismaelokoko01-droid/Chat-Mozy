[app]

# (str) Title of your application
title = zelyph App

# (str) Package name
package.name = zelyphapp

# (str) Package domain (needed for android/ios packaging)
package.domain = org.zelyph

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (add json, txt if needed)
source.include_exts = py,kv,png,json,atlas

# (str) Application versioning
version = 1.0.0

# (list) Application requirements
# AJOUT DE : pyzbar, zbarcam, et des dépendances nécessaires
requirements = python3,kivy,kivymd,pillow,urllib3,flask,requests,plyer,pyzbar

# (str) Presplash image and Icon
presplash.filename = %(source.dir)s/logo.png
icon.filename = %(source.dir)s/logo.png

# (str) Supported orientation
orientation = portrait

# --- PERMISSIONS COMPLÈTES ANDROID ---
android.permissions = INTERNET, ACCESS_NETWORK_STATE, CAMERA, RECORD_AUDIO, POST_NOTIFICATIONS, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, READ_MEDIA_IMAGES, READ_MEDIA_VIDEO, READ_PHONE_STATE, CALL_PHONE, READ_CONTACTS, WRITE_CONTACTS, READ_CALL_LOG, BLUETOOTH_SCAN, BLUETOOTH_CONNECT, WAKE_LOCK

# --- CONFIGURATION CIBLE ANDROID ---
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.presplash_color = #FFFFFF

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = disable, 1 = enable)
warn_on_root = 1
