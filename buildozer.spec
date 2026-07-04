[app]
title = Fips App
package.name = fipsapp
package.domain = org.fips
source.include_exts = py,kv,png
source.dir = .
version = 1.0.0
requirements = python3,kivy,kivymd,kvdroid,pillow

# Pointage direct à la racine
presplash.filename = %(source.dir)s/logo.png
icon.filename = %(source.dir)s/logo.png

orientation = portrait
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
