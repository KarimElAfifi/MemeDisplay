# MemeDisplay

MemeDisplay erkennt Handgesten mit der Webcam und blendet passend dazu ein Meme in das Kamerabild ein. Das fertige Bild wird über die **OBS Virtual Camera** ausgegeben und kann so in Videoanrufen, zum Beispiel in Discord oder der WhatsApp-Desktop-App, verwendet werden.

> **Plattformhinweis:** Die virtuelle Kamera ist für OBS unter Windows eingerichtet. Die Kamera und OBS müssen installiert und funktionsfähig sein.

## Funktionen

- Erkennt bis zu zwei Hände mit MediaPipe Hand Landmarker.
- Wertet Finger- und Handpositionen aus, um Gesten zu unterscheiden.
- Zeigt den passenden Sticker groß und zentriert im Bild.
- Zeichnet erkannte Handpunkte zur visuellen Kontrolle ein.
- Gibt das verarbeitete Kamerabild an die OBS Virtual Camera aus.

## Voraussetzungen

- Windows
- Python mit Unterstützung für die installierten MediaPipe- und OpenCV-Pakete
- OBS Studio mit installierter OBS Virtual Camera
- Eine Webcam
- Die Dateien `hand_landmarker.task` und die Meme-Bilder im `images`-Ordner

## Installation

Öffne PowerShell im Projektordner und installiere die Python-Abhängigkeiten:

```powershell
python -m pip install opencv-python mediapipe pyvirtualcam
```

Wenn dein Python-Launcher `python` nicht verfügbar ist, verwende stattdessen den Befehl für deine installierte Version, zum Beispiel:

```powershell
py -3.13 -m pip install opencv-python mediapipe pyvirtualcam
```

Stelle sicher, dass `hand_landmarker.task` im Projektordner liegt und dass alle verwendeten Sticker in `images/` vorhanden sind.

## Starten

1. Beende in OBS die Virtual Camera, falls sie gerade läuft. Die Python-Anwendung startet die Ausgabe selbst.
2. Starte das Programm im Projektordner:

   ```powershell
   python main.py
   ```

3. Wähle in der gewünschten Videoanruf-Anwendung **OBS Virtual Camera** als Kamera aus.
4. Zum Beenden drücke `q`, während das OpenCV-Kamerafenster aktiv ist.

Falls die OBS Virtual Camera bereits von OBS gestartet wurde, kann `pyvirtualcam` den Bildstrom möglicherweise nicht initialisieren. In diesem Setup sollte OBS Studio installiert sein, aber seine Virtual Camera vor dem Start des Skripts ausgeschaltet bleiben.

## Gesten und Sticker

Die aktuell implementierten Zuordnungen:

| Geste | Sticker |
|---|---|
| Eine Faust, Handfläche oder Handrücken zur Kamera | `Jerry` – `images/jerry look at this guy.png` |
| Eine Faust, zur Seite gedreht, sodass die Handkante zur Kamera zeigt | `Baby-Dats-Crazy` – `images/baby dats crazy.jpg` |
| Zwei Hände mit ausgestrecktem Daumen, Zeige- und Mittelfinger | `Pistolen` – `images/sybau.jpg` |
| Zwei offene Hände, eine vertikal und eine horizontal | `Stopp` – `images/shaq stop.jpg` |
| Zwei vertikale, nah beieinander liegende Hände | `Beten` – `images/god pls.jpg` |

Die Gestenerkennung verwendet MediaPipes 3D-Hand-Landmarks und feste Regeln für Gelenkwinkel und Handorientierung. Sie ist keine trainierte Klassifikation und kann je nach Kamerawinkel, Beleuchtung, Handposition und Erkennungsqualität variieren. Sorge dafür, dass die Hand vollständig und deutlich sichtbar ist.

`images/images.jpg` ist derzeit keiner Geste zugeordnet. Eine zuverlässige Facepalm-Erkennung ist nicht implementiert, da sie zusätzlich Gesichtserkennung oder eine andere Gesichtsreferenz benötigen würde.

## Eigene Sticker verwenden

1. Lege das Bild im Ordner `images/` ab.
2. Ergänze die Zuordnung in `stickers.py` in `GESTURE_STICKERS`.
3. Passe die Gestenlogik in `gesture_recognition.py` an, wenn eine neue Geste erkannt werden soll. Der zurückgegebene Name muss dem Schlüssel in `GESTURE_STICKERS` entsprechen.

Die Sticker werden auf bis zu 80 % der Kamerabildbreite und -höhe skaliert, zentriert und proportional dargestellt.

## Projektstruktur

```text
MemeDisplay/
├── main.py                 # Programmeinstieg
├── camera_app.py           # Webcam, MediaPipe und virtuelle Kamera
├── gesture_recognition.py  # Regeln zur Gestenerkennung
├── stickers.py             # Sticker laden und einblenden
├── hand_landmarker.task    # MediaPipe-Handmodell
└── images/                 # Meme-Sticker
```

## Fehlerbehebung

### `OBS Virtual Camera ... virtual camera output could not be started`

- Beende die OBS Virtual Camera in OBS – die Schaltfläche sollte danach „Virtuelle Kamera starten“ anzeigen.
- Schließe weitere laufende Instanzen von `main.py`.
- Starte `main.py` erneut.

### OBS Virtual Camera wird in Discord oder WhatsApp nicht angeboten

- Vergewissere dich, dass `main.py` ohne Fehler läuft.
- Wähle **OBS Virtual Camera** in den Kameraeinstellungen der Anwendung aus.
- Beende die Videoanruf-Anwendung vollständig und öffne sie erneut, wenn die Kamera nicht in der Liste erscheint.

### `Kamera konnte nicht geöffnet werden`

Die Anwendung verwendet aktuell die erste Windows-Kamera (`VideoCapture(0)`). Schließe andere Programme, die die Webcam verwenden. Wenn mehrere Kameras angeschlossen sind, muss gegebenenfalls der Kameraindex in `camera_app.py` angepasst werden.

### Ein Sticker wird nicht geladen

Prüfe, dass der Dateiname im Ordner `images/` genau dem Eintrag in `GESTURE_STICKERS` in `stickers.py` entspricht.

## Lizenz und Bildrechte

Prüfe die Nutzungsrechte der Meme-Bilder und des MediaPipe-Modells, bevor du dieses Projekt oder seine Assets weiterveröffentlichst. Füge eine Lizenzdatei hinzu, wenn du eine konkrete Lizenz für den eigenen Code festlegen möchtest.
