[app]

# --- App Info ---
title = Chama App
package.name = chamaApp
package.domain = org.peenztechnologies
version = 0.1

source.dir = .
source.include_exts = py,kv,png,jpg,db

# --- Python / Kivy requirements ---
requirements = python3,kivymd,reportlab
environment = REPORTLAB_NO_CEXT=1

# --- Orientation & Display ---
orientation = portrait
fullscreen = 0

# --- Android SDK / NDK / Ant ---
android.sdk_path = /home/peenzsoftwares/.buildozer/android/platform/android-sdk
android.ndk_path = /home/peenzsoftwares/.buildozer/android/platform/android-ndk-r25c
android.ant_path = /home/peenzsoftwares/.buildozer/android/platform/apache-ant-1.9.4

# --- Android API & architecture ---
android.api = 33
android.minapi = 21
android.ndk_api = 21
android.archs = armeabi-v7a
# Later, you can add: android.archs = armeabi-v7a,arm64-v8a

# --- Permissions ---
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# --- App Icons ---
icon.filename = %(source.dir)s/family.png
icon.adaptive_foreground.filename = %(source.dir)s/family.png
icon.adaptive_background.filename = %(source.dir)s/family.png

# --- Bootstrap & Python-for-Android ---
p4a.bootstrap = sdl2
p4a.branch = master
p4a.local_python = /home/peenzsoftwares/.buildozer/android/platform/python-for-android/hostpython3_3.12.3/bin/python3.12
p4a.hostpython_dir = /home/peenzsoftwares/.buildozer/android/platform/python-for-android/hostpython3_3.12.3

# --- Python Compilation & Security ---
android.python3Compiler = nuitka
p4a.cython = False
p4a.pyc = True
p4a.extra_args = --remove-output --no-pyi-file --nofollow-import-to=kivy --nofollow-import-to=kivymd
# Note: --lto=yes is omitted for now to prevent clang failures

# --- Copy required libraries ---
android.copy_libs = True

[buildozer]

log_level = 2
warn_on_root = 1
