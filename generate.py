# -*- coding: utf-8 -*-
import os
import zipfile
import hashlib

REPO_DIR = "repo/zips"
OUTPUT_XML = "addons.xml"
OUTPUT_MD5 = "addons.xml.md5"

addons = []

for root, dirs, files in os.walk(REPO_DIR):
    for file in files:
        if file.endswith(".zip"):
            zip_path = os.path.join(root, file)

            with zipfile.ZipFile(zip_path, 'r') as z:
                for name in z.namelist():
                    if name.endswith("addon.xml"):
                        with z.open(name) as f:
                            xml = f.read().decode("utf-8")
                            addons.append(xml.strip())
                        break

# budowa addons.xml
with open(OUTPUT_XML, "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<addons>\n')

    for addon in addons:
        f.write(addon + "\n")

    f.write('</addons>\n')

# MD5
with open(OUTPUT_XML, "rb") as f:
    md5 = hashlib.md5(f.read()).hexdigest()

with open(OUTPUT_MD5, "w") as f:
    f.write(md5)

print("Gotowe: addons.xml + addons.xml.md5")