# -*- coding: utf-8 -*-
import os
import zipfile
import hashlib
import xml.etree.ElementTree as ET

REPO_DIR = "repo/zips"
OUTPUT_XML = "addons.xml"
OUTPUT_MD5 = "addons.xml.md5"

addons = []
errors = []

def validate_addon(xml_text, source):
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        errors.append(f"[XML ERROR] {source}: {e}")
        return None

    # sprawdź czy to <addon>
    if root.tag != "addon":
        errors.append(f"[INVALID ROOT] {source}: root != addon")
        return None

    addon_id = root.attrib.get("id")
    version = root.attrib.get("version")

    if not addon_id or not version:
        errors.append(f"[MISSING ID/VERSION] {source}")
        return None

    # szukaj metadata
    metadata = root.find("extension[@point='xbmc.addon.metadata']")
    if metadata is not None:
        langs = {}

        for desc in metadata.findall("description"):
            lang = desc.attrib.get("lang", "default")

            # duplikaty języków
            if lang in langs:
                errors.append(
                    f"[DUPLICATE DESCRIPTION] {addon_id} ({source}) lang={lang}"
                )
            else:
                langs[lang] = True

            # pusty description
            if not (desc.text and desc.text.strip()):
                errors.append(
                    f"[EMPTY DESCRIPTION] {addon_id} ({source}) lang={lang}"
                )

    return xml_text.strip()


for root, dirs, files in os.walk(REPO_DIR):
    dirs.sort()
    files.sort()

    for file in files:
        if not file.endswith(".zip"):
            continue

        zip_path = os.path.join(root, file)

        try:
            with zipfile.ZipFile(zip_path, 'r') as z:
                for name in z.namelist():
                    if name.endswith("addon.xml"):
                        with z.open(name) as f:
                            raw = f.read()
                            xml = raw.decode("utf-8-sig", errors="ignore")

                            # usuń nagłówki XML
                            lines = xml.splitlines()
                            lines = [
                                line for line in lines
                                if not line.strip().startswith("<?xml")
                            ]
                            xml = "\n".join(lines).strip()

                            valid_xml = validate_addon(xml, zip_path)

                            if valid_xml:
                                addons.append(valid_xml)
                            else:
                                errors.append(f"[SKIPPED] {zip_path}")

                        break

        except zipfile.BadZipFile:
            errors.append(f"[BAD ZIP] {zip_path}")
        except Exception as e:
            errors.append(f"[ERROR] {zip_path}: {e}")
# ========================
# WYKRYWANIE DUPLIKATÓW ID (z plikami)
# ========================
id_map = {}
duplicates = []

for xml in addons:
    try:
        root = ET.fromstring(xml)
        addon_id = root.attrib.get("id")

        if addon_id in id_map:
            duplicates.append((addon_id, id_map[addon_id]))
        else:
            id_map[addon_id] = "unknown source"

    except:
        continue

for addon_id, source in duplicates:
    errors.append(f"[DUPLICATE ADDON ID] {addon_id}")
# zapis addons.xml
with open(OUTPUT_XML, "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<addons>\n')

    for addon in addons:
        f.write(addon + "\n")

    f.write('</addons>\n')

# MD5
with open(OUTPUT_XML, "rb") as f:
    md5 = hashlib.md5(f.read()).hexdigest()

with open(OUTPUT_MD5, "w", encoding="utf-8") as f:
    f.write(md5)

# raport błędów
print("\n=== WALIDACJA ===")
if errors:
    for err in errors:
        print(err)
else:
    print("Brak błędów 👍")

print("\n✅ Gotowe: addons.xml + addons.xml.md5")