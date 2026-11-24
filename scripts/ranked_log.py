#!/usr/bin/env python3
"""Ranked-Bilanz aus dem Brawl-Stars-Kampfprotokoll (letzte 25 Runden).

Aufruf:  SSL_CERT_FILE=/root/.ccr/ca-bundle.crt python3 scripts/ranked_log.py [#TAG] [--seit "24.11. 20:00"]
Der API-Schlüssel wird vom Proxy der Cloud-Umgebung für bsproxy.royaleapi.dev eingesetzt (nicht im Code).
Nur Ranked (battle.type == "soloRanked"); Runden mit gleichen Teams werden zu einem Match (Best of 3) zusammengefasst.
"""
import json, sys, urllib.request, urllib.parse, datetime
from zoneinfo import ZoneInfo

TAGS = ["#PU98PGYP", "#29V99QQ20"]  # dritter und zweiter Account des Nutzers
BERLIN = ZoneInfo("Europe/Berlin")

def fetch(tag):
    url = "https://bsproxy.royaleapi.dev/v1/players/" + urllib.parse.quote(tag) + "/battlelog"
    req = urllib.request.Request(url, headers={"Accept": "application/json", "Authorization": "Bearer proxy-injected"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["items"]

def nice(n):
    return " ".join(w.capitalize() if w not in ("&",) else w for w in n.lower().split(" ")).replace("8-bit", "8-Bit").replace("Mr. p", "Mr. P").replace("R-t", "R-T")

def main():
    args = sys.argv[1:]
    tags = [a for a in args if a.startswith("#")] or TAGS
    since = None
    if "--seit" in args:
        s = args[args.index("--seit") + 1]
        now = datetime.datetime.now(BERLIN)
        since = datetime.datetime.strptime(f"{now.year} {s}", "%Y %d.%m. %H:%M").replace(tzinfo=BERLIN)
    rounds = []
    for tag, x in [(t, x) for t in tags for x in fetch(t)]:
        b = x["battle"]
        if b.get("type") != "soloRanked":
            continue
        t = datetime.datetime.strptime(x["battleTime"], "%Y%m%dT%H%M%S.%fZ").replace(tzinfo=datetime.timezone.utc).astimezone(BERLIN)
        if since and t < since:
            continue
        mi = next(i for i, tm in enumerate(b["teams"]) if any(p["tag"] == tag for p in tm))
        my, en = b["teams"][mi], b["teams"][1 - mi]
        me = next(p for p in my if p["tag"] == tag)
        rounds.append(dict(acc=tag, t=t, map=x["event"]["map"], mode=x["event"]["mode"], res=b.get("result"),
            my=[nice(p["brawler"]["name"]) for p in my], en=[nice(p["brawler"]["name"]) for p in en],
            me=nice(me["brawler"]["name"]), st=me.get("stats", {}), star=(b.get("starPlayer") or {}).get("tag") == tag,
            bans_my=[nice(p["bannedBrawler"]["name"]) for p in my if p.get("bannedBrawler")],
            bans_en=[nice(p["bannedBrawler"]["name"]) for p in en if p.get("bannedBrawler")]))
    rounds.sort(key=lambda r: r["t"])
    matches = []
    for r in rounds:
        key = (r["acc"], r["map"], tuple(sorted(r["my"])), tuple(sorted(r["en"])))
        if matches and matches[-1]["key"] == key and (r["t"] - matches[-1]["r"][-1]["t"]).seconds < 900:
            matches[-1]["r"].append(r)
        else:
            matches.append({"key": key, "r": [r]})
    w = l = 0
    out = []
    for m in matches:
        rs = m["r"]; f = rs[0]
        rw = sum(x["res"] == "victory" for x in rs); rl = sum(x["res"] == "defeat" for x in rs)
        res = "SIEG" if rw > rl else "NIEDERLAGE" if rl > rw else "offen"
        w += res == "SIEG"; l += res == "NIEDERLAGE"
        k = sum(x["st"].get("kills", 0) for x in rs); d = sum(x["st"].get("deaths", 0) for x in rs)
        dmg = sum(x["st"].get("damageDealt", 0) for x in rs)
        out.append(f"{f['t']:%d.%m. %H:%M} · {f['map']} · {res} {rw}:{rl} · du: {f['me']}{' (' + f['acc'] + ')' if len(tags) > 1 else ''}"
                   f"{' · Star Player' if any(x['star'] for x in rs) else ''}\n"
                   f"   Team: {', '.join(f['my'])} | Gegner: {', '.join(f['en'])}\n"
                   f"   Bans eigenes Team: {', '.join(f['bans_my']) or '-'} | Bans Gegner: {', '.join(f['bans_en']) or '-'}\n"
                   f"   Deine Werte: {k} Kills, {d} Tode, {dmg:,} Schaden".replace(f"{dmg:,}", f"{dmg:,}".replace(",", ".")))
    print(f"Accounts: {', '.join(tags)}")
    print(f"Ranked-Bilanz: {w} Siege, {l} Niederlagen ({len(rounds)} Runden in {len(matches)} Matches)\n")
    print("\n".join(out))

if __name__ == "__main__":
    main()
