# Ranked Draft Coach – Projektwissen

Draft-Hilfe für Brawl Stars Ranked (Deutsch). Statische PWA, live unter https://eviltobi.github.io/draft-coach/
(GitHub Pages, Branch `main`, Ordner `/`). Kein Build-Schritt, keine Abhängigkeiten.

## Dateien
- `index.html` – komplette App (Brawler-Daten `RAW`, Maps `DEFAULT_MAPS`, Regeln, UI). Vanilla JS, Zustand in localStorage (`rdc-state`).
- `data/stats.js` – `window.STATS`, erzeugt von `scripts/update_data.py` (nicht von Hand bearbeiten).
- `scripts/update_data.py` – lädt alle Quellen (~15 min). Lokal: `SSL_CERT_FILE=/root/.ccr/ca-bundle.crt python3 scripts/update_data.py`;
  optional `DRAFT_CACHE=<ordner>` als Download-Zwischenspeicher. Erhöht automatisch `VERSION` in `sw.js`.
  Kurz nach Season-Start nutzt es trotzdem die neue Atlas-Season (aktuelle Balance); fehlende Rang-Gruppen bekommen den
  Skill der höchsten vorhandenen. Nur bei < 300 Masters-Spielen: `ATLAS_FALLBACK=<data.json>` oder bisheriges Modell.
- Nutzer-Wunsch: kaum Daten vor der letzten Balance-Änderung (zuletzt 11.11.2026). DraftMeta 7 Tage, Corestats 9 Tage.
- `sw.js` – Offline-Cache. **Bei jeder Änderung `VERSION` erhöhen**, sonst bekommen installierte Apps das Update nicht.
- `manifest.webmanifest`, `icons/`, `maps/*.webp` (Map-Bilder aus dem Fandom-Wiki).

## Ranked-Kontext (Stand 19.11.2026, Season 51)
- Map-Pool: Gem Grab (Hard Rock Mine, Gem Fort, Undermine, Double Swoosh), Brawl Ball (Center Stage, Pinball Dreams,
  Sneaky Fields, Triple Dribble), Heist (Safe Zone, Hot Potato, Kaboom Canyon, Bridge Too Far), Hot Zone (Dueling Beetles,
  Open Business, Parallel Plays, Ring of Fire), Knockout (Belle's Rock, Flaring Phoenix, New Horizons, Out in the Open),
  Bounty (Shooting Star, Hideout, Layer Cake, Dry Season). Quelle: brawlstars.fandom.com/wiki/Ranked.
- Trial-Brawler: Frank, Mico, Spike, Bonnie, Max, Amber. Seasons starten am 3. Donnerstag im Monat.
- Draft-Reihenfolge 1-2-2-1: Team A pickt 1, 4, 5; Team B 2, 3, 6. Ab Diamond bannt jeder Spieler 1 (nur eigene Team-Bans sichtbar).
- Rey, Ruby, Thunder Frogs ausgeblendet (`NOT_YET_RANKED`), erscheinen automatisch, sobald sie in Pro-Scrims vorkommen.

## Daten und Gewichtung
Rang-Gewichtung: **Pro 40 %, Masters III 35 %, Masters I+II 25 %**, kleine Stichproben zum Masters+-Wert geschrumpft.
- DraftMeta API `/api/brawl-stars/battle-stats?endpoint=bans&rank=pro|masters-iii|masters-i,masters-ii&map=<Name>`:
  Pick-, Win-, Banrate gesamt und pro Map. Draft-Opening ist rang-unabhängig → bewusst nicht genutzt.
- Brawl Atlas `assets/data.json`: Siegmodell (w, syn, att, def, ctx, map, mode, v_skill; Skill je Rang, Pro = Masters III,
  weil Atlas keine Pro-Lobbys hat) und Map-Winrates je Rang (Rangskala 19–21 Masters I–III, 22 Pro).
- Corestats `/scrims?date=YYYY-MM-DD` (RSC-Payload): Pro-Scrims der letzten 9 Tage, Matchups, Kombis.
- BrawlLab `/analytics/brawler_matchups|brawler_teammates?brawler_id=…` (rang-unabhängig, niedriger gewichtet).
- BrawlPick `/brawlers/<slug>/counters` („vs expected“).
- Nicht nutzbar: Brawlify (blockt Bots, nicht umgehen), BrawlDraft (eigener API-Host), keine Quelle für First-Pick-Rate.
- Erlaubte Hosts der Cloud-Umgebung sind bereits eingetragen (corestats, draftmeta, atlas, brawllab, brawlpick, fandom, github.io).

## Bewertungslogik (Wünsche des Nutzers, nicht zurückbauen)
- Bans je Position: First Pick → Top 2 offen lassen; Team A sonst Top 1 offen + Last-Pick-Gefahren bannen;
  Team B (2/3) → stärkste Blind-Picks; Last Pick → stärkste Blind-Picks. Banrate pro Map fließt ein.
- Picks je Position: First Pick = schwer zu kontern (Modell: Siegchance nach bestem Gegner-Konter, als Perzentil);
  Pick 4/5 mit Gegner-Last-Pick = Team-Check (Schutz vor Assassinen, vor Werfern, Schaden gegen Tanks);
  Last Pick = Konter gegen alle 3 Gegner.
- Assassinen vor allem spät (Pick 1–3 abgewertet). Auf offenen Maps und gegen ≥2 Sniper abwerten; beim Last Pick erlaubt,
  wenn Gegner weder Wallbreak noch Schutz (Tank, Nahkampf-DD, CC, Anti-Assassine) haben.
- Schaden gegen Tanks: bester Tank-Stopper zählt (Griff, Pierce, Lou, Otis, Colette …); Sniper haben wenig Tank-Schaden.
- Brawler ohne Reichweite (z. B. Kenji) auf offenen Maps an Pick 3/4 abwerten. Zwei Sniper auf offenen Maps okay.
- Frank auf offenen Maps und in Heist abwerten, stärker wenn Colette/Lou frei sind.
- Gegner mit wenig Schaden (Stu, Mr. P, Tick, Ollie, Gene …): Tank mit viel HP stark, mit Max oder Heiler noch stärker;
  Bonus klein, wenn Gegner einen Tank-Killer hat. Gegen Mr. P + Werfer: Assassinen und Tanks.
- Tanks in Knockout/Bounty stark abgewertet (Modus-Abzug, Konter-Vorteile zählen nur halb).
- Zwei Werfer (Klasse R) nur als eigener Last Pick und nur ohne Gegner-Assassinen. Mr. P ist Controller, aber werfer-ähnlich
  (zählt im Duo mit einem Werfer halb). Gegner mit mittlerer Range/viel HP füttern seine Super (Bonus);
  Gegner-Sniper (Mandy, Piper …) auf offenen Maps = Abzug, weil er weniger Reichweite hat.
- Verlauf: fertige Drafts automatisch in localStorage (`rdc-hist`, max. 30), mit Sieg/Niederlage, Öffnen, Löschen.
- Nutzer-Top-Meta (mind. 9): Lou, Vince, Amber, Melodie, Mr. P, Gale, Colette, Rico, Chester, Mandy.
- Siegchance im Vorschlag relativ zum Durchschnitts-Pick; nach dem Draft Gewinnchance beider Teams + Spielplan
  (Lane/Mitte als Faustregel, Gegenüber/Fokus/Vorsicht mit Matchup-Winrates und Spielzahl).

## Arbeitsweise
- Antworten auf Deutsch, einsteigerfreundlich. Vor dem Live-Schalten kurz berichten, wenn der Nutzer das verlangt.
- Größere Änderungen erst auf einem Branch, nach OK per Fast-Forward nach `main`. Commits als `EvilTobi <EvilTobi@users.noreply.github.com>`.
- GitHub-Pages-Einstellungen und Pages-API sind für Claude gesperrt; Push auf `main` funktioniert.
- Testen mit Playwright (iPhone-14-Emulation) gegen `python3 -m http.server` im Repo; Google Fonts sind in der Sandbox blockiert (harmloser Fehler).
- Supercell-Hinweis (Fan Content Policy) im Footer behalten.
