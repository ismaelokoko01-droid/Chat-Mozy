[app]

# (str) Title of your application
title = Fips App

# (str) Package name
package.name = fipsapp

# (str) Package domain (needed for android/ios packaging)
package.domain = org.test

# (str) Source code where the main.py live
source.include_exts = py,kv

# (list) Source files to include (omit to include all the files)
source.include_patterns = assets/*,images/*.png

# (str) Application versioning
version = 0.1

# (list) Application requirements
requirements = python3,kivy,kivymd

# (str) Presplash of the application
# presplash.filename = %(source.dir)s/logo.png

# (str) Icon of the application
# icon.filename = %(source.dir)s/logo.png

# (str) Supported orientations (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) Permissions
android.permissions = INTERNET

# (int) Target Android API
android.api = 33

# (int) Minimum API required
android.minapi = 21

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2
