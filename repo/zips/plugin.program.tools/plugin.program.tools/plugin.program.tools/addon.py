import xbmc
import xbmcgui
import xbmcaddon
import urllib.request
import json

API_URL = "https://api.github.com/repos/Agaton111/repository.Agaton111/contents/repo/tools"
RAW_BASE = "https://raw.githubusercontent.com/Agaton111/repository.Agaton111/main/repo/tools/"

dialog = xbmcgui.Dialog()

# pobierz listę plików z GitHub API
req = urllib.request.Request(API_URL, headers={'User-Agent': 'Kodi'})
response = urllib.request.urlopen(req)
data = json.loads(response.read().decode("utf-8"))

addons = []
display = []

for item in data:
    if item["name"].endswith(".zip"):
        zip_name = item["name"]

        # próbujemy wyciągnąć addon_id z nazwy zip
        addon_id = zip_name.split("-")[0]

        # sprawdzenie czy zainstalowany
        try:
            xbmcaddon.Addon(addon_id)
            status = "✔"
        except:
            status = "❌"

        display.append(f"{status} {addon_id}")
        addons.append((addon_id, zip_name))

if not addons:
    dialog.ok("Tools", "Brak plików ZIP")
    exit()

choice = dialog.select("Tools", display)

if choice >= 0:
    addon_id, zip_name = addons[choice]

    try:
        xbmcaddon.Addon(addon_id)
        dialog.ok("Tools", "Już zainstalowane")
    except:
        zip_url = RAW_BASE + zip_name
        xbmc.executebuiltin(f'InstallAddon({zip_url})')
        dialog.ok("Tools", "Instalacja zakończona")