# -*- coding: utf-8 -*-
import os
import zipfile
import hashlib

REPO_DIR = "repo/zips"
OUTPUT_XML = "addons.xml"
OUTPUT_MD5 = "addons.xml.md5"

addons = []

for root, dirs, files in os.walk(REPO_DIR):
    dirs.sort()
    files.sort()

    for file in files:
        if not file.endswith(".zip"):
            continue

        zip_path = os.path.join(root, file)

        try:
            with zipfile.ZipFile(zip_path, 'r') as z:
                found = False

                for name in z.namelist():
                    if name.endswith("addon.xml"):
                        found = True

                        with z.open(name) as f:
                            raw = f.read()

                            # usuwa BOM + bezpieczne dekodowanie
                            xml = raw.decode("utf-8-sig", errors="ignore")

                            # usuń nagłówki XML
                            lines = xml.splitlines()
                            lines = [
                                line for line in lines
                                if not line.strip().startswith("<?xml")
                            ]

                            # usuń puste linie na początku i końcu
                            xml = "\n".join(lines).strip()

                            if xml:
                                addons.append(xml)

                        break

                if not found:
                    print(f"[WARN] Brak addon.xml w: {zip_path}")

        except zipfile.BadZipFile:
            print(f"[ERROR] Uszkodzony ZIP: {zip_path}")
        except Exception as e:
            print(f"[ERROR] {zip_path}: {e}")

# zapis addons.xml
with open(OUTPUT_XML, "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<addons>\n')

    for addon in addons:
        f.write(addon + "\n")

    f.write('</addons>\n')

# generowanie MD5
with open(OUTPUT_XML, "rb") as f:
    md5 = hashlib.md5(f.read()).hexdigest()

with open(OUTPUT_MD5, "w", encoding="utf-8") as f:
    f.write(md5)

print("✅ Gotowe: addons.xml + addons.xml.md5")