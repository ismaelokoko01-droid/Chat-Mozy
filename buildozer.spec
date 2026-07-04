[app]

# (str) Titre de ton application
title = Fips

# (str) Nom du paquet (tout en minuscules, pas d'espaces)
package.name = fips

# (str) Nom du domaine
package.domain = org.fips

# (str) Fichier principal
source.main = main.py

# (list) Dossiers source à inclure
source.include_exts = py,png,jpg,kv,atlas

# (str) Version de l'application
version = 0.1

# (list) Dépendances
requirements = python3,kivy

# (str) Orientation
orientation = portrait

# (bool) Plein écran
fullscreen = 1

# (str) Chemin vers ton logo
icon.filename = %(source.dir)s/logo.png

# (list) Architectures Android
android.archs = arm64-v8a, armeabi-v7a

# (int) API Android
android.api = 33
android.minapi = 21

[buildozer]
log_level = 2
warn_on_root = 1
