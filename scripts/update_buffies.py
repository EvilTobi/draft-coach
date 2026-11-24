#!/usr/bin/env python3
"""Buffies je Account aus der Brawl-Stars-API → data/buffies.js (window.BUFFIES).

Aufruf:  SSL_CERT_FILE=/root/.ccr/ca-bundle.crt python3 scripts/update_buffies.py
Der API-Schlüssel wird vom Proxy der Cloud-Umgebung für bsproxy.royaleapi.dev eingesetzt (nicht im Code).
Die Datei ist öffentlich (GitHub Pages): nur Account-Bezeichnung und Anzahl Buffies (0–3) je Brawler, keine Playertags.
"""
import json, re, urllib.request, urllib.parse, datetime, pathlib

ACCOUNTS = [("2", "Dreamy", "#29V99QQ20"), ("3", "kiora", "#PU98PGYP")]  # Bezeichnung = Accountname im Spiel
ROOT = pathlib.Path(__file__).resolve().parent.parent

def norm(n):
    return re.sub(r"[^a-z0-9]", "", n.lower())

def fetch(tag):
    url = "https://bsproxy.royaleapi.dev/v1/" + ("brawlers" if tag is None else "players/" + urllib.parse.quote(tag))
    req = urllib.request.Request(url, headers={"Accept": "application/json", "Authorization": "Bearer proxy-injected"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def main():
    out = {"updated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), "accounts": {}, "avail": []}
    avail = set()
    # Brawler, die es im Spiel mit Hypercharge gibt
    hc_exists = {norm(x["name"]) for x in fetch(None)["items"] if x.get("hyperCharges")}
    all_b = {norm(x["name"]) for x in fetch(None)["items"]}
    for key, label, tag in ACCOUNTS:
        p = fetch(tag)
        b = {}
        for x in p["brawlers"]:
            n = sum(bool(v) for v in (x.get("buffies") or {}).values())
            b[norm(x["name"])] = n
            if n: avail.add(norm(x["name"]))
        # nicht bereit für Ranked: nicht freigeschaltet, unter Power 11 oder Hypercharge fehlt (falls es eine gibt)
        own = {norm(x["name"]): x for x in p["brawlers"]}
        nr = sorted(n for n in all_b if n not in own or own[n]["power"] < 11 or (n in hc_exists and not own[n].get("hyperCharges")))
        out["accounts"][key] = {"label": label, "b": b, "nr": nr}
        print(f"{label}: {len(nr)} Brawler nicht bereit (Power < 11, ohne Hypercharge oder nicht freigeschaltet)")
        print(f"{label}: {sum(1 for v in b.values() if v == 3)} Brawler mit allen Buffies, {sum(1 for v in b.values() if 0 < v < 3)} teilweise")
    out["avail"] = sorted(avail)  # Brawler, für die es Buffies gibt (bei mindestens einem Account vorhanden)
    (ROOT / "data" / "buffies.js").write_text("// Erzeugt von scripts/update_buffies.py – nicht von Hand bearbeiten\nwindow.BUFFIES=" +
        json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print("data/buffies.js geschrieben,", len(avail), "Brawler mit Buffies")

if __name__ == "__main__":
    main()
