# Bedienungsanleitung – MindPic Desktop-Notiz-App

Diese Anleitung beschreibt die Bedienung der Anwendung **MindPic** als installierte Windows-Desktop-App (EXE). Es geht ausschließlich um die Nutzung der Oberfläche, nicht um Programmierung oder Code.

---

## 1. Zweck der Anwendung

MindPic ist eine schlanke Desktop-Notiz-App, die dauerhaft am Bildschirmrand „kleben“ kann. Sie eignet sich für:

- schnelle Gedanken und ToDo-Listen  
- dauerhafte Notizen direkt auf dem Desktop  
- Zeitprotokolle mit Zeitstempel je Eintrag  

Alle Texte und Einstellungen werden automatisch gespeichert und beim nächsten Start wiederhergestellt.

---

## 2. Start & Beenden

### Starten

- Start über das Startmenü, Desktop-Icon oder eine Verknüpfung (je nach Installation).
- Beim Start öffnet sich ein kleines Notizfenster mit dunklem Hintergrund und einem **„Save“**-Button unten rechts.

### Beenden

- Klicken Sie im Fenster rechts oben auf das **Schließen-Symbol (X)**,  
  **oder**
- wählen Sie im Kontextmenü (Rechtsklick im Fenster) **„Beenden“**,  
  **oder**
- wählen Sie im Tray-Menü (Icon in der Taskleiste) **„Beenden“**.

Beim Beenden werden Notizen und Fensterposition noch einmal gespeichert.

---

## 3. Grundbedienung im Notizfenster

### 3.1 Schreiben & Bearbeiten

- Klicken Sie in den Textbereich und tippen Sie Ihre Notizen.  
- Umbrüche mit **Enter**.  
- Der Text verhält sich wie ein einfaches Notizfeld (Zeilenumbruch ist aktiv).

### 3.2 Scrollen

- Wenn der Text länger wird, erscheint rechts eine schlanke vertikale Scrollleiste.  
- Scrollen mit:
  - Mausrad  
  - Klick auf die Scrollleiste  
  - Ziehen des Scrollbalkens  

### 3.3 Automatisches Speichern

- Während Sie schreiben, wird der Inhalt nach kurzer Pause automatisch gespeichert.  
- Es ist nicht nötig, ständig auf **„Save“** zu klicken, um die Notizen zu sichern – der Button hat eine besondere Funktion (siehe unten).

---

## 4. Einträge mit Zeitstempel & farbige Blöcke

### 4.1 „Save“-Button (Eintrag abschließen)

Beim Klicken auf **„Save“** passiert folgendes:

1. Falls die aktuelle Zeile nicht mit einem Zeilenumbruch endet, wird ein Zeilenumbruch eingefügt.  
2. In einer **neuen Zeile** wird automatisch ein **Zeitstempel** eingefügt, z. B.:  
   `[10-12-2025 21:37]`  
3. Der gesamte Text wird gespeichert.  
4. Die Einträge werden neu eingefärbt.

Damit eignet sich der Button ideal, um einen Eintrag abzuschließen.

### 4.2 Automatische Einfärbung

- Die Anwendung teilt den Text automatisch in **Blöcke**:
  - Ein Block beginnt nach einem Zeitstempel
  - und endet am nächsten Zeitstempel (inklusive der Zeitstempel-Zeile).
- Jeder Block bekommt eine **eigene Hintergrundfarbe**.
- Die Farben rotieren durch mehrere vordefinierte Töne.

So sind Einträge optisch voneinander getrennt und leichter zu überblicken.

---

## 5. Fensterposition, Größe & Andocken

### 5.1 Größe ändern

- Maus an den Fensterrand bewegen, bis der Größen-Cursor erscheint.  
- Mit gedrückter linker Maustaste ziehen.  
- Es gibt eine minimale Fenstergröße.

### 5.2 Fenster verschieben

- Im **Normalmodus** (mit Rand und Titelzeile):  
  - Klick in die Titelzeile und Ziehen.
- Im **Randlos-Modus** (siehe Kapitel 7.3):  
  - Klick irgendwo ins Fenster und Ziehen.

### 5.3 Andocken („Snap to Edges“)

Beim Loslassen der Maus nach dem Ziehen:

- Ist das Fenster nahe am Bildschirmrand, dockt es bündig an:
  - links  
  - rechts  
  - oben  
  - unten  

---

## 6. Ein- und Ausblenden (Hotkey & Auto-Hide)

### 6.1 Sichtbarkeit umschalten (F9)

Die App kann über eine Tastenkombination ein- und ausgeblendet werden.

- **Globaler Hotkey (Standard):** **F9**
  - Ist MindPic sichtbar → es wird **ausgeblendet**.  
  - Ist MindPic ausgeblendet → es wird **eingeblendet** und fokussiert.
- Falls der globale Hotkey auf Ihrem System nicht funktioniert, kann F9 zumindest innerhalb des Fensters verwendet werden, solange der Fokus im MindPic-Fenster liegt.

### 6.2 Auto-Hide bei Fokusverlust

Wenn **„Auto-Hide bei Fokusverlust“** aktiviert ist:

- Sobald MindPic den Fokus verliert (z. B. Klick in ein anderes Programm),  
- prüft die App kurz danach, ob sie immer noch keinen Fokus hat,  
- und blendet sich dann **automatisch aus**.

Zum Wiederherstellen:

- **F9** drücken oder  
- Icon im System-Tray verwenden (siehe Kapitel 8).

---

## 7. Kontextmenü im Fenster (Rechtsklick)

Ein Rechtsklick **im Textbereich** oder auf den Hintergrund des Fensters öffnet das **Kontextmenü** von MindPic.

### 7.1 Farben

**Menüpfad:** `Rechtsklick → Farben`

- **Textfarbe…**  
  Öffnet einen Farbdialog, mit dem Sie die Schriftfarbe der Notizen ändern.

- **Hintergrund…**  
  Öffnet einen Farbdialog für die Hintergrundfarbe des Notizfeldes.

- **Eintragsfarbe 1… / 2… / …**  
  Für jede Eintragsfarbe gibt es einen Menüpunkt.  
  - Wählen Sie eine Farbe, um die jeweilige Blockfarbe zu ändern.  
  - Nach Änderung werden die Einträge automatisch neu eingefärbt.

Alle Farbanpassungen werden gespeichert und beim nächsten Start wieder verwendet.

### 7.2 Schrift

**Menüpfad:** `Rechtsklick → Schrift`

- **„Aktuell: <Schriftname> <Größe>“**  
  Anzeige der aktuell verwendeten Schriftart und -größe (nicht anklickbar).

- **„Schrift wählen…“**  
  Öffnet ein kleines Einstellfenster:
  - oben: Dropdown-Liste mit allen verfügbaren System-Schriftarten  
  - unten: Eingabe der Schriftgröße (z. B. 9, 10, 11 …)  
  - **OK**: überträgt die Auswahl auf das Notizfeld und speichert die Einstellung  
  - **Abbrechen**: schließt die Auswahl ohne Änderung

### 7.3 Randlos (Borderless)

**Menüeintrag:** `Randlos (Borderless)` (Checkbox)

- **Aktiviert (Häkchen gesetzt):**
  - Das Fenster wird ohne Standard-Titelzeile und ohne Rahmen dargestellt.
  - Das Fenster lässt sich nun durch **Linksklick und Ziehen irgendwo im Fenster** verschieben.
- **Deaktiviert (kein Häkchen):**
  - Das Fenster erhält wieder den normalen Windows-Rahmen mit Titelzeile.

### 7.4 Transparenz

**Menüpfad:** `Rechtsklick → Transparenz`

Es stehen feste Stufen zur Auswahl, z. B.:

- 50 %  
- 70 %  
- 85 %  
- 95 %  
- 100 %  

Die aktuell aktive Stufe ist im Menü markiert.

Die Transparenz betrifft das gesamte Fenster inklusive Text und ist ideal, um MindPic „über“ anderen Fenstern schweben zu lassen.

### 7.5 Auto-Hide bei Fokusverlust

**Menüeintrag:** `Auto-Hide bei Fokusverlust` (Checkbox)

- **Aktiviert (Häkchen):**  
  MindPic blendet sich automatisch aus, wenn der Fokus auf ein anderes Programm wechselt.

- **Deaktiviert (kein Häkchen):**  
  Das Fenster bleibt sichtbar, bis Sie es manuell ausblenden (z. B. mit F9 oder über das Tray-Menü).

### 7.6 „Immer im Vordergrund umschalten“

**Menüeintrag:** `Immer im Vordergrund umschalten`

- Dieser Eintrag wirkt als **Schalter**:
  - Ist MindPic bisher normal im Fensterstapel → wird zu „Always on top“.  
  - Ist es bereits „Always on top“ → wird wieder in den normalen Fenstermodus zurückversetzt.

### 7.7 „Fenster ein-/ausblenden“

**Menüeintrag:** `Fenster ein-/ausblenden`

- Hat die gleiche Wirkung wie **F9**:
  - Ist das Fenster sichtbar → wird ausgeblendet.  
  - Ist es ausgeblendet → wird eingeblendet.

### 7.8 „Handbuch öffnen“

**Menüeintrag:** `Handbuch öffnen`

- Öffnet das Benutzerhandbuch (diese Anleitung) als PDF in der Standardanwendung für PDF-Dateien Ihres Systems.

### 7.9 „Beenden“

**Menüeintrag:** `Beenden`

- Speichert Inhalt und Fensterkonfiguration.  
- Beendet anschließend die Anwendung vollständig.

---

## 8. Tray-Symbol (System-Tray)

Nach dem Start legt MindPic ein Icon im **Infobereich der Taskleiste** (System-Tray) an, meist rechts unten neben der Uhr (ggf. im ausgeklappten Bereich).

### 8.1 Tray-Menü öffnen

- Rechtsklick auf das MindPic-Icon im System-Tray.

Das Menü enthält:

1. **„Tafel ein/aus“**  
   - Schaltet das Hauptfenster ein- und aus (wie F9 bzw. „Fenster ein-/ausblenden“ im Kontextmenü).

2. **„Auto-Hide bei Fokusverlust“** (mit Häkchen)  
   - Aktiviert/deaktiviert dieselbe Funktion wie im Fenster-Kontextmenü.  
   - Der aktuelle Zustand wird im Tray-Menü angezeigt.

3. **„Beenden“**  
   - Beendet die Anwendung (mit Speichern von Inhalt und Geometrie).

### 8.2 Typische Nutzung

- MindPic beim Systemstart öffnen (z. B. über Autostart/Verknüpfung).  
- Hauptfenster ausblenden.  
- Bei Bedarf:
  - über **F9** einblenden → Notiz schreiben → **„Save“** drücken,  
  - Fenster wieder ausblenden (F9 oder Tray-Menü).

So bleibt die App unauffällig im Hintergrund, aber jederzeit griffbereit.

---

## 9. Verhalten beim Neustart

Beim erneuten Start von MindPic werden automatisch wiederhergestellt:

- alle Notizen  
- Fensterposition und -größe  
- Farben, Schriftart, Schriftgröße  
- Transparenz  
- Randlos-Einstellung  
- Always-on-top-Status  
- Auto-Hide-Einstellung  

Die App startet also so, wie Sie sie beim letzten Beenden verlassen haben.

---

## 10. Kurzübersicht – wichtigste Funktionen

**Text & Einträge**

- Schreiben: direkt ins Hauptfenster.  
- Eintrag abschließen + Zeitstempel: **„Save“**-Button.  
- Farbliche Trennung von Einträgen: automatisch nach Zeitstempeln.

**Sichtbarkeit**

- Ein-/Ausblenden: **F9** oder
  - Kontextmenü → „Fenster ein-/ausblenden“  
  - Tray-Menü → „Tafel ein/aus“  

**Fenster**

- Verschieben: Titelzeile (normal) oder Fenster ziehen (borderless).  
- Andocken: Fenster an Bildschirmrand ziehen → beim Loslassen wird eingerastet.  
- Größe ändern: an den Fensterrändern ziehen.

**Optionen (Rechtsklick im Fenster)**

- Farben: Text, Hintergrund, Eintragsfarben.  
- Schrift: Schriftart & Schriftgröße.  
- Transparenz: 50–100 %.  
- Auto-Hide: bei Fokusverlust ein/aus.  
- Randlos: Borderless-Ansicht ein/aus.  
- Immer im Vordergrund: umschalten.  
- Handbuch öffnen: PDF-Benutzerhandbuch.  
- Beenden: App schließen.

---

MindPic ist damit als kleine, dauerhafte Desktop-Tafel nutzbar, die sich exakt an Ihre Arbeitsweise anpasst.
