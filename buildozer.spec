[app]
title = Fips
package.name = fips
package.domain = org.fips
source.dir = .
source.main = main.py
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy
orientation = portrait
fullscreen = 1
icon.filename = %(source.dir)s/logo.png
android.archs = arm64-v8a
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33

[buildozer]
log_level = 2
warn_on_root = 1
