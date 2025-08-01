[app]

# معلومات التطبيق الأساسية
title = SilentBackgroundClient
package.name = silentclient
package.domain = org.example

# إعدادات الإصدار
version = 1.0.0
requirements = python3==3.9.13,kivy==2.3.1,plyer==2.1.0,requests==2.32.4,pyjnius==1.5.0,numpy==1.26.4

# إعدادات الملفات
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json,txt
orientation = portrait
fullscreen = 0
android.entrypoint = org.kivy.android.PythonActivity

[android]

# إعدادات الأندرويد
arch = armeabi-v7a
api = 30
minapi = 21
targetapi = 30
p4a.branch = master

# صلاحيات الأندرويد (محدثة)
android.permissions = INTERNET, ACCESS_NETWORK_STATE, ACCESS_WIFI_STATE, READ_PHONE_STATE, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, FOREGROUND_SERVICE

# إعدادات الخدمة الخلفية
android.service = True
android.background_service = True

[buildozer]

# إعدادات Buildozer
log_level = 2
warn_on_root = 1
