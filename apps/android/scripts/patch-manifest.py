# Fügt den gravityloop://-Deep-Link in die Android-Hauptaktivität ein (Rückkehr nach dem Google-Login).
import re, sys
p = 'android/app/src/main/AndroidManifest.xml'
s = open(p, encoding='utf-8').read()
if 'android:scheme="gravityloop"' in s:
    sys.exit(0)
f = '''
            <intent-filter>
                <action android:name="android.intent.action.VIEW" />
                <category android:name="android.intent.category.DEFAULT" />
                <category android:name="android.intent.category.BROWSABLE" />
                <data android:scheme="gravityloop" />
            </intent-filter>
'''
s, n = re.subn(r'(</activity>)', f + r'        \1', s, count=1)
assert n == 1, 'Kein <activity>-Ende gefunden'
open(p, 'w', encoding='utf-8').write(s)
print('Deep-Link eingetragen')
