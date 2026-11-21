# Ranked Draft Coach – Web-App

Draft-Hilfe für Brawl Stars Ranked. Statische Web-App ohne Server, ohne Konto, ohne Tracking.
Läuft offline und lässt sich auf dem iPhone über Safari → Teilen → „Zum Home-Bildschirm“ installieren.

## Dateien
- `index.html` – die komplette App (Daten, Logik, Design)
- `manifest.webmanifest`, `icons/` – App-Name und App-Symbol
- `sw.js` – Offline-Speicher. **Bei jedem Update `VERSION` erhöhen**, damit alle Geräte die neue Fassung bekommen.
- `maps/` – Map-Vorschaubilder (Quelle: Brawl Stars Fandom-Wiki)

## Veröffentlichen (kostenlos)
Die Dateien müssen über **https** ausgeliefert werden (sonst kein Offline-Modus und keine Installation).

**GitHub Pages:** neues öffentliches Repository anlegen → alle Dateien dieses Ordners hochladen
(„Add file → Upload files“) → Settings → Pages → Branch `main`, Ordner `/ (root)` → Save.
Nach 1–2 Minuten ist die App unter `https://<name>.github.io/<repo>/` erreichbar.

**Netlify Drop:** https://app.netlify.com/drop öffnen und diesen Ordner hineinziehen.
Ohne Konto wird die Seite nach einer Stunde gelöscht; mit kostenlosem Konto bleibt sie dauerhaft.

## Datenquellen und Gewichtung
`data/stats.js` wird von `scripts/update_data.py` erzeugt. Die Rang-Gruppen sind gewichtet:
**Pro 40 % · Masters III 35 % · Masters I+II 25 %**. Kleine Stichproben werden zum Masters+-Wert hin gezogen.

| Kennzahl | Quelle |
|---|---|
| Pickrate, Winrate, Banrate je Rang (gesamt und pro Map) | DraftMeta (Ranked-Drafts der letzten 7 Tage) |
| Map-Winrate je Rang | DraftMeta + Brawl Atlas (Ranked-Spiele der letzten Season) |
| Counter- und Synergie-Winrate | Brawl Atlas Modell, BrawlLab, BrawlPick, Corestats (Pro-Scrims) |
| Draft-Siegchance | Brawl-Atlas-Modell, ausgewertet für das gewichtete Rang-Niveau |
| First-Pick-Wert | Brawl-Atlas-Modell: Siegchance nach dem besten Gegner-Konter (Masters/Pro-Niveau) |
| Pro-Daten | Corestats Scrims (9 Tage) + DraftMeta Rang „Pro“ |
| Map-Pool, Trial-Brawler, Map-Bilder | Brawl Stars Fandom-Wiki |

### Daten aktualisieren
```bash
python3 scripts/update_data.py
```
Das Skript braucht nur Python 3 (keine Pakete) und läuft einige Minuten. Es erhöht automatisch die
Cache-Version in `sw.js`, damit installierte Apps die neuen Daten laden.

Direkt nach einem Season-Start hat Brawl Atlas noch kaum Masters-Spiele. Das Skript nutzt trotzdem die neue
Season (aktuelle Balance) und überträgt den Skill der höchsten vorhandenen Rang-Gruppe auf die fehlenden.

Dieses Material ist inoffiziell und wird von Supercell nicht unterstützt.
Siehe Supercells Fan Content Policy: https://supercell.com/en/fan-content-policy/
