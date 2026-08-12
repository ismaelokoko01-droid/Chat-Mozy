[app]

# (str) Title of your application
title = Zelyph App

# (str) Package name
package.name = zelyphapp

# (str) Package domain (needed for android/ios packaging)
package.domain = org.zelyph

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include
source.include_exts = py,kv,png,jpg,json,atlas

# (str) Application versioning
version = 1.0.0

# (list) Application requirements
# Note : pyzbar nécessite souvent la bibliothèque système libzbar (qui peut poser problème sur Android).
# On garde les dépendances pures et indispensables pour votre code :
requirements = python3,kivy==2.3.0,kivymd==1.2.0,pillow,urllib3,requests,plyer,android

# (str) Presplash image and Icon
presplash.filename = %(source.dir)s/logo.png
icon.filename = %(source.dir)s/logo.png

# (str) Supported orientation
orientation = portrait

# --- PERMISSIONS ANDROID ---
android.permissions = INTERNET, ACCESS_NETWORK_STATE, CAMERA, RECORD_AUDIO, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, READ_MEDIA_IMAGES, READ_PHONE_STATE

# --- CONFIGURATION CIBLE ANDROID ---
android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.presplash_color = #673AB7

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (bool) Accept SDK license automatically
android.accept_sdk_license = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 1
