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

## Datenquellen
- Ranked-Map-Pool Season 51, Trial-Brawler, Map-Bilder: Brawl Stars Fandom-Wiki
- Pro-Scrims 11.–19.11.2026 (2.399 Spiele): corestats.pro
- Konter-Tipps: Fandom-Forum, r/BrawlStarsCompetitive, diverse Guides

Dieses Material ist inoffiziell und wird von Supercell nicht unterstützt.
Siehe Supercells Fan Content Policy: https://supercell.com/en/fan-content-policy/
