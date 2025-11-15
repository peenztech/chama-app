[app]

title = Chama App
package.name = chamaApp
package.domain = org.peenztechnologies
version = 0.1

source.dir = .
source.include_exts = py,kv,png,jpg,db

requirements = python3,kivymd,reportlab
environment = REPORTLAB_NO_CEXT=1

orientation = portrait
fullscreen = 0

android.api = 33
android.minapi = 21
android.ndk_api = 21
android.archs = armeabi-v7a

android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

icon.filename = %(source.dir)s/family.png
icon.adaptive_foreground.filename = %(source.dir)s/family.png
icon.adaptive_background.filename = %(source.dir)s/family.png

p4a.bootstrap = sdl2
p4a.branch = master

android.copy_libs = True

[buildozer]
log_level = 2
warn_on_root = 1
