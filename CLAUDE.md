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
  `APP_VERSION` in `index.html` immer gleich halten (Zeitstempel ohne `draft-coach-`): wird im Hinweis-Kasten als
  „App-Version“ angezeigt; die App lädt `sw.js` frisch (SW lässt sie durch) und meldet „Neue Version verfügbar“.
  **Changelog** (`CHANGELOG` in `index.html`, aufklappbar unter dem Verlauf): bei jedem Live-Update oben einen Eintrag mit
  `v` = neue APP_VERSION (Literal, nicht die Variable), Datum, Titel und einfachen Sätzen ergänzen. `update_data.py` fügt
  bei Daten-Updates automatisch „Daten aktualisiert“ ein.
- `data/buffies.js` – `window.BUFFIES` (Buffies 0–3 je Brawler für „Zweiter/Dritter Account“, ohne Playertags), erzeugt von
  `scripts/update_buffies.py` (bei Bedarf bzw. beim Daten-Update mit ausführen). App: Account-Auswahl unter der Pick-Position
  (`ACCT`, localStorage `rdc-acct`); eigener Pick −0,8 je fehlendem Buffy (nur Brawler in `avail`). Assassinen an Pick 4/5 vor
  Gegner-Last-Pick: halber Abzug, wenn sie alle sichtbaren Gegner laut Daten schlagen (≥ +2 %, ≥ 150 Spiele). Import trägt Notiz nur
  ein, wenn der Draft noch keine hat.
  Accounts heißen wie im Spiel (Dreamy = zweiter, kiora = dritter), Knöpfe oben im Header: „Maxed“ (= kein Abzug, für den ersten Account und andere Spieler mit allem), Dreamy, kiora.
  `nr` = nicht bereit (Power < 11, vorhandene Hypercharge fehlt, nicht freigeschaltet) → eigener Pick −25 (Trial-Brawler ausgenommen).
  „Konter frei“ (`freeCounters`) zählt nur Konter mit ≥ 1,5 % Pickrate auf der Map (Nutzer: Jacky in Bounty/Knockout nie).
  Gründe-Texte kurz halten (≤ 3 Wörter + Namen), Nutzer liest im Draft schnell.
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
- Auswertung 22.11. (Nutzer-Regeln): Gegner-Last-Pick an Pick 4/5 → Team braucht Werfer-Schutz (Assassine, eigener Werfer
  inkl. Mr. P, schnelle HP-Brawler wie Bibi eingeschränkt, Wallbreak nur auf Maps mit Wänden und nicht bei Tanks;
  Tanks zählen nicht (Frank/El Primo haben Wallbreak, Hank nicht), Hank wird von Werfern gekontert).
  Eigenes Team hat Last Pick → Last-Pick-Brawler (Edgar, Mortis …) an Pick 2/3 aufheben, mit Hinweis im Panel.
  Last Pick: Assassine +1,5, wenn noch keiner im Team. Gegen 3 Fernkämpfer mit Wallbreak: Assassine mit Abzug erlaubt.
  Mr. P gegen ≥2 Sniper nur leicht abwerten. Gigi nur ab Pick 4 (4./5./Last) weit oben, wenn Gegner viele Projektile haben
  (Amber, Griff, Meg, Gene, Colt, Rico, Tara, Shelly, Spike, 8-Bit; nicht Bull/Darryl), sonst Abzug.
  Antwort-Risiko an Pick 2/3: freier harter Konter (inkl. Mr. P gegen Einzelschuss-Sniper) = kleiner Abzug.
  Assassinen an Pick 5 vor Gegner-Last-Pick abwerten (Knockout stärker); Knockout-Map-Winrate ab 500 Spielen stärker.
  Frank nur als Last Pick ohne harten Konter beim Gegner (`FRANK_HARD`), an Pick 5 nur wenn alle harten Konter weg sind.
  Pick-Position: keine Quelle hat Winrates je Pick-Position (DraftMeta nur pick/ban/openPickRate, Corestats ohne Reihenfolge).
  Näherung: beim Last Pick zählt eine schwache Map-Winrate von Assassinen/Last-Pick-Brawlern/Gigi nur halb.
  Nach dem Draft „So spielt ihr“ (`teamHint`) + Spielplan; schlechtes Duell → „meiden“, in Heist „Safe angreifen“.
- Auswertung 22.11. abends (Nutzer-Regeln): Ziggy, Willow, Berry sind vollwertige Werfer (Klasse R, Hauptangriff wie Barley).
  Werfer an Pick 1–3 abwerten, solange starke Assassinen frei sind (Mr. P nur leicht); Ausnahme `MAP_BONUS` (Juju auf
  Parallel Plays wegen Wasser, auch als First Pick). Pick 4 bei eigenem Pick 5: Hinweis „höchstens einer nimmt einen Werfer“.
  Tanks an Pick 4/5 vor Gegner-Last-Pick: Abzug für freie `TANK_HARD` (halb, wenn schon ein Tank im Team).
  Frank: freier harter Konter vor Gegner-Pick −15, Konter beim Gegner −6 (`FRANK_HARD` inkl. Sirius; Meeple NICHT, zu wenig Schaden).
  Hank: Gegner-Wallbreak −3, Griff/Frank/Colette frei −3. Konter: Melodie > Bibi, Otis > Melodie, Assassinen > Squeak
  (Meta 7,5), Sirius > El Primo/Surge (Tank-Killer). Antwort-Risiko −1,5 bei Konter mit Meta ≥ 8.
  Lou auf Maps mit Wänden kaum Schutz vor Assassinen; starke Assassinen dort als Last-Pick-Ban (Team A).
  Assassinen an Pick 4/5 vor Gegner-Last-Pick: Bounty wie Knockout. Spieltipps `PLAY_TIPS` (Trunk>Mico, Colette>Bibi),
  Lou + Berry Zonen-Tipp, Heist mit 2 schnellen Brawlern: beide auf den Safe. Ash gegen Einzelschuss-Brawler (`ASH_PREY`: Surge, Meeple, Gus …; nicht Squeak, Explosion trifft alle Ratten) weit oben,
  v. a. Gem Grab/Brawl Ball. Ash-Konter: Griff, Emz, El Primo, Colette (Ash nicht in der allgemeinen Tank-Regel).
- Offene Konter für ALLE Brawler (`hardC`, `freeCounters`): solange Gegner noch picken, Abzug für freie harte Konter
  (Matchup-Daten ab 150 Spielen, sonst Atlas-Modell, plus `COUNTERED_BY`/`MRP_PREY`/`FRANK_HARD`; ab 0,8 = harter Konter,
  gewichtet nach Meta des Konters). Bester freier Konter zählt ×1,5, die nächsten 3 je ×0,35, max. −7; First Pick ×0,35.
  Alle harten Konter gebannt/gepickt = +1,5. Ersetzt das alte „X ist noch frei“-Antwort-Risiko.
  Nutzer-Konter in 3 Stufen: `COUNTERED_BY` (hart, +1,6), `SOFT_COUNTERS` (weich, +0,8), `SIT_COUNTERS` (situativ, +0,4), Funktion `userC`.
  Liste vom 22.11. (Sam, Lola, Pam, Jacky, Ollie, Janet, Sandy, Ziggy, Clancy, Glowy, Larry & Lawrie) mit Daten geprüft;
  unklare/widersprüchliche Einträge gestrichen → `NO_COUNTER` (zählen nie, auch nicht über Daten). Lola: keine Werfer-Konter
  (wird meist in Heist gespielt). Poco (Gadget Protective Tunes) weich gegen Ollie, Crow, Byron, Amber.
  Nutzer 24.11.: weich Nani>Piper, Nani>Bea (keine Matchup-Daten zu Piper). Video-Auswertung (Arthur 17.11., Drage 23.11.): weich Berry>Penny, Surge>Melodie/Shade/Kenji, Nori>Kaze/Colt.
  Creator-Aussagen immer gegen Daten prüfen; viele sind persönliche Vorlieben.
- Squeak = Nutzer-Favorit: auf Maps mit Pick-Rang ≤ 12 (`popRank`) +3 als Pick, +2,3 als Bann; +1 als Last Pick oder wenn
  alle Assassinen-Konter weg sind. Edgar kontert Juju hart, außer auf Wasser-Maps (`WATER_MAPS`, `ONWATER`): Nutzer-Erfahrung
  geht vor Daten (Daten sind Team-Ergebnisse, keine Einzel-Duelle).
- Draft-Guide Bobby (vor ~7 Monaten, Grundregeln mit Daten geprüft): `SPACE_MAKERS` (Bull, Bibi, Buzz, Carl, Mina, Chuck, Sam,
  Gigi, Darryl + Assassinen, `isSM`) zählen als Werfer-Schutz. Tank +2 gegen Space Maker, wenn Gegner keinen Anti-Tank (`isAT`) hat.
  `AGGRO_MODES` (gem, ball, hz, heist): Team ohne Anti-Tank → Anti-Tank +2,5 an Pick 4/5 bzw. beim dritten Team-Pick,
  sonst −1,5; schon 2 Anti-Tanks → −2. Heist gegen Chuck: `CHUCK_DEFENDERS` −2,5 (nicht, wenn Gegner
  auch eine Assassine hat, z. B. Melodie), `HEIST_HYPER` +1,5. Space-Maker-Werferschutz nur ab 3,5 % Map-Pickrate (`mapPr`).
  R-T zählt nur in Hot Zone (+ Knockout/Bounty) als Anti-Tank; Rico nie −1,5, auf Maps mit Wänden (walls ≥ 2) ohne Gegner-Wallbreak +1,2.
- Nutzer 23.11.: Brawler, die auf der Map kaum gespielt werden, abwerten (in `mapFit`, gilt auch für Bans): Pickrate < 3,5 % −2,5,
  < 1,5 % −4,5, < 0,5 % −7 (außer Top-Picks der Map und `MAP_BONUS`). Pickrate = Anteil der Spiele (Summe aller Brawler ≈ 6).
- Rang-Schalter „Dein Rang: Legendary · Masters+“ (`RANK`, localStorage `rdc-rank`, Standard Legendary; Nutzer spielt meist Legendary,
  zu Season-Beginn Mythic). Daten: `STATS.leg` (DraftMeta `rank=legendary`, I–III nur zusammen abrufbar; `{drafts, all, maps:{map:{name:[pr,wr,n]}}}`),
  nicht in der Rang-Gewichtung. Nur bei Legendary (`legS`): Map-Winrate 50/50 Masters+/Legendary (ab 300 Legendary-Spielen; Masters+ < 300 Spiele → Legendary-Anteil steigt bis 100 %);
  „kaum gespielt“-Abzug für eigene Picks halbiert, wenn Legendary-Pickrate ≥ 5 % und Winrate ≥ 50 % (Grund „Legendary-Pick (x %)“, z. B. Bo Gem Fort);
  Gegner-Seite (`mapFit(b,map,true)`: Banns, Gegner-Antworten beim First Pick; `freeCounters`) nutzt die höhere Pickrate (`enemyPr`),
  weil Legendary-Gegner z. B. Spike, Mico, Brock, Colt oft picken (meist mit < 50 % Winrate).
- Nutzer 25.11.: Bull auf Kaboom Canyon −2,5, als First Pick −10 („nie First Pick hier“). Brock Hideout `MAP_BONUS` +4,5 (Top 5 First Picks).
  Melodie ab Pick 4 +2 („stark ab Pick 4“, ersetzt „Assassine zu früh“), an Pick 1–3 −2.
- Nutzer 28.11.: Pick 4/5 mit Gegner-Last-Pick: Brawler, die eine der 3 wahrscheinlichsten freien Assassinen (Meta ≥ 7, nach `enemyPr`)
  hart kontern, +1,5/+0,8/+0,5 (×1,2 an Pick 5), nur wenn im Team noch keiner sie kontert („stoppt X“).
  Gigi zählt in `freeCounters` nur als Konter, wenn b oder ein Teammate in `MULTI_PROJ` ist. Weich: Edgar, Mortis > Vince.
  Hot Potato `MAP_BONUS` Rico/Colt +3 („Safe-Schaden“; Nutzer: Lou dort als First Pick leicht zu kontern). Top-Picks je Map (`mapPower`):
  Winrate-Anteil × n/(n+300), damit kleine Stichproben nicht reinrutschen (El Primo Hot Potato: 60 Spiele, 70 %).
  `PLAY_TIPS` Brock>Mortis (Daten: Mortis +2,5 %, deshalb kein Konter); `teamHint` Sirius: erst Schatten sammeln.
- Auswertung 23.11. abends: Panel zeigt „Bester Schutz vor Assassinen: X (Platz n)“, wenn Team-Check A schwach und Gegner noch picken
  (`aNote`, nur Brawler ab 3,5 % Pickrate). Vision-Gear-Tipp bei bush = 2 (Dry Season auf bush 1 gesetzt, Nutzer: wenig Büsche).
  Ring of Fire = offen, wenig Wände, viele Büsche außen (Nutzer). Cosmo `MAP_BONUS` Ring of Fire +6 (Nutzer; Daten: 48 % Map-Winrate, verliert gegen Mortis/Edgar/Mandy). Weich: Bo>Amber, Mr. P>Chester;
  situativ: Mina>Amber, Willow>Lou auf Maps mit Wänden (`WALLMAP`). `PLAY_TIPS` Gale>Doug, Colette>8-Bit; Tipp-Paare werden im Spielplan
  bevorzugt zugeteilt. Abgelehnt: Tipp „Lou in die gegnerische Zone“, 8-Bit-Gadget-Tipp, Knockout-Fokus-Tipp.
- Gray + Emz (Nutzer 23.11., Daten +3,2 %): Hot Zone außer `GE_OFF` (Parallel Plays). Zweiter Partner: Gegner hat Lou/Bo (`GE_STOP`) −2,
  Lou/Bo noch frei und Gegner picken noch +1, sonst +3. Erster Partner an Pick 2/4 (Doppel-Pick) +1, wenn Lou und Bo weg sind.
  Bann: Lou/Bo +0,8, solange Gray und Emz frei sind. Mr. P NICHT als Konter der Kombi (Nutzer: Portal-Teleport braucht viel Schaden).
  Chuck außerhalb von Heist/Hot Zone −8. Shelly in Heist −4 bis −10 (je seltener gepickt, desto mehr), außer Gegner haben 3 Tanks/Nahkämpfer.
- Export „Neu seit letztem Export“ (`EXPMARK` in localStorage `rdc-expmark`): nur neue oder geänderte Drafts (Ergebnis/Notiz),
  geänderte mit „AKTUALISIERT“. Jeder Export markiert die enthaltenen Drafts.
  Willow ist Anti-Assassine (Super), Werfer-Duo mit ihr und früher Pick nur halber Abzug.
  Bibi>Melodie/Frank>Meeple-Tipps bewusst nicht
  (Nutzer: Seite nicht überladen, Draft am iPad muss schnell gehen).
- Verlauf: fertige Drafts automatisch in localStorage (`rdc-hist`, max. 30), mit Sieg/Niederlage, Notiz, Öffnen, Löschen.
  Export „Heute/Alle kopieren“ (`exportHist`): Picks, Bans, Notiz und je eigenem Pick Platz + Top 5 + Gründe
  (mit aktuellen Regeln neu berechnet) sowie „Damals angezeigt“ (`live`, ab 22.11.2026 gespeichert). Nutzer fügt ihn im Chat ein.
- Nutzer-Top-Meta (mind. 9): Lou, Vince, Amber, Melodie, Mr. P, Gale, Colette, Rico, Chester, Mandy.
- Siegchance im Vorschlag relativ zum Durchschnitts-Pick; nach dem Draft Gewinnchance beider Teams + Spielplan
  (Lane/Mitte als Faustregel, Gegenüber/Fokus/Vorsicht mit Matchup-Winrates und Spielzahl).

## Ranked-Tracking (Variante A, im Chat)
- `scripts/ranked_log.py [#TAG] [--seit "24.11. 20:00"]`: Bilanz aus dem Kampfprotokoll (letzte 25 Runden, auch Trophäen-Spiele),
  über `bsproxy.royaleapi.dev` (Brawl-Stars-Proxy von RoyaleAPI; Key mit IP 45.79.218.79, als Netzwerk-Geheimnis der Umgebung
  hinterlegt, Proxy setzt ihn ein). Nutzer-Tags #PU98PGYP (dritter Account) und #29V99QQ20 (zweiter Account), ohne Tag-Argument werden beide abgerufen. Ranked = `battle.type == "soloRanked"`
  (`ranked` = Trophäen). Jede Runde einzeln → Matches nach gleichen Teams gruppiert. Enthält Bans beider Teams (`bannedBrawler`),
  Kills/Tode/Schaden, Star Player. Nutzer sagt „ich spiele Ranked“ / „fertig“ → am Ende einmal abrufen.
- Nach „fertig“: nummerierte Liste ausgeben, Nutzer kommentiert im Chat („1: …“). Dann `--import --notiz "1=Text"` (mehrfach) →
  Zeilen `RDC <ISO-Zeit mit Offset> | Map | Team | Gegner | W/L | Notiz`. App: „Letzte Drafts → Ergebnisse einfügen“
  (`importResults`): passender Draft über Map + ≥ 4 gleiche Brawler + ≤ 6 h Abstand; setzt Ergebnis, hängt Notiz an (keine Dopplung).
  Pick-Reihenfolge und Top-5-Vorschläge gibt es nur im App-Export, nicht im Kampfprotokoll.
- Vereinfachter Ablauf (Nutzer 24.11., Standard): Nutzer schickt nach der Session NUR den App-Export („Neu seit letztem Export“)
  plus Kommentare im Chat. Claude ruft dann selbst `ranked_log.py --seit <ältester Draft>` ab, ordnet Ergebnisse/Bans/Werte den
  Drafts zu (Map + Brawler) und wertet aus. Keine RDC-Zeilen zurück in die App, außer der Nutzer fragt danach.

- Geräte: Der Nutzer spielt auf dem iPad und nutzt die App parallel NUR auf dem MacBook (Verlassen des Spiels im Draft wird bestraft).
  Verlauf/Notizen liegen also im MacBook-Browser; keine Geräte-Synchronisierung nötig. Layout auch für Desktop-Breite testen.

## Arbeitsweise
- Antworten auf Deutsch, einsteigerfreundlich. Vor dem Live-Schalten kurz berichten, wenn der Nutzer das verlangt.
- Größere Änderungen erst auf einem Branch, nach OK per Fast-Forward nach `main`. Commits als `EvilTobi <EvilTobi@users.noreply.github.com>`.
- GitHub-Pages-Einstellungen und Pages-API sind für Claude gesperrt; Push auf `main` funktioniert.
- Testen mit Playwright (iPhone-14-Emulation) gegen `python3 -m http.server` im Repo; Google Fonts sind in der Sandbox blockiert (harmloser Fehler).
- Supercell-Hinweis (Fan Content Policy) im Footer behalten.
