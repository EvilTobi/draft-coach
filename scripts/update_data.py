#!/usr/bin/env python3
"""
Lädt aktuelle Ranked- und Pro-Daten und schreibt data/stats.js für den Draft Coach.

Quellen
  DraftMeta (draftmeta.com)      Pick-, Win- und Banrate je Rang-Gruppe, gesamt und pro Map
  Brawl Atlas (brawlstars-atlas)  Siegwahrscheinlichkeits-Modell (Synergie, Konter, Map, Skill)
                                 und Map-Winrates je Rang aus Millionen Ranked-Spielen
  Corestats (corestats.pro)       Pro-Scrims: Picks, Siege, Bans, Matchups, Kombis
  BrawlLab (brawllab.gg)          Ranked-Matchups und Teammate-Winrates
  BrawlPick (brawlpick.app)       Konter-Winrates mit "vs expected"

Gewichtung der Rang-Gruppen: Pro 40 %, Masters III 35 %, Masters I+II 25 %.
Kleine Stichproben werden zum Masters+-Gesamtwert hin gezogen.

Aufruf:  python3 scripts/update_data.py
"""
import collections, datetime, itertools, json, math, os, re, ssl, sys, time, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "stats.js")
SW = os.path.join(ROOT, "sw.js")
WEIGHTS = {"pro": 0.40, "m3": 0.35, "m12": 0.25}
DM_RANKS = {"pro": "pro", "m3": "masters-iii", "m12": "masters-i,masters-ii"}
ATLAS_RANKS = {"m12": (19, 20), "m3": (21,), "pro": (22,)}   # Atlas-Skala: 19 = Masters I … 22 = Pro
UA = "DraftCoachDataBot/1.0"
CTX = ssl.create_default_context(cafile=os.environ.get("SSL_CERT_FILE") or None)

RANKED_MAPS = {  # Ranked Season 51 (ab 19.11.2026)
    "Hard Rock Mine": "gemGrab", "Gem Fort": "gemGrab", "Undermine": "gemGrab", "Double Swoosh": "gemGrab",
    "Center Stage": "brawlBall", "Pinball Dreams": "brawlBall", "Sneaky Fields": "brawlBall", "Triple Dribble": "brawlBall",
    "Safe Zone": "heist", "Hot Potato": "heist", "Kaboom Canyon": "heist", "Bridge Too Far": "heist",
    "Dueling Beetles": "hotZone", "Open Business": "hotZone", "Parallel Plays": "hotZone", "Ring of Fire": "hotZone",
    "Belle's Rock": "knockout", "Flaring Phoenix": "knockout", "New Horizons": "knockout", "Out in the Open": "knockout",
    "Shooting Star": "bounty", "Hideout": "bounty", "Layer Cake": "bounty", "Dry Season": "bounty",
}

def log(*a): print(*a, file=sys.stderr, flush=True)

CACHE = os.environ.get("DRAFT_CACHE")  # optional: Ordner für Zwischenspeicher, z. B. bei Fehlersuche
def get(url, kind="json", tries=3, pause=0.35):
    if CACHE:
        import hashlib
        path = os.path.join(CACHE, hashlib.sha1(url.encode()).hexdigest() + ".cache")
        if os.path.exists(path):
            body = open(path, "rb").read()
            return json.loads(body) if kind == "json" else body.decode("utf-8", "ignore")
    body = _fetch(url, tries, pause)
    if body is None: return None
    if CACHE:
        os.makedirs(CACHE, exist_ok=True); open(path, "wb").write(body)
    try:
        return json.loads(body) if kind == "json" else body.decode("utf-8", "ignore")
    except ValueError:
        log("  ! keine gültige Antwort:", url); return None

def _fetch(url, tries, pause):
    err = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json, text/html;q=0.9"})
            with urllib.request.urlopen(req, timeout=120, context=CTX) as r:
                body = r.read()
            time.sleep(pause)
            return body
        except Exception as e:  # Netzwerkfehler: kurz warten, erneut versuchen
            err = e
            time.sleep(2 * (i + 1))
    log("  ! fehlgeschlagen:", url, err)
    return None

# ---------- Namen vereinheitlichen (Schreibweise aus index.html) ----------
html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
raw = html[html.index("const RAW = `") + 13:]
NAMES = [l.split("|")[0] for l in raw[:raw.index("`")].split("\n")]
LOW = {re.sub(r"[^a-z0-9]", "", n.lower()): n for n in NAMES}
def nm(x):
    k = re.sub(r"[^a-z0-9]", "", str(x).lower())
    return LOW.get(k, str(x).title())

ID2NAME = {}
def r4(x): return None if x is None else round(x, 4)
def shrink(v, n, prior, k):  # kleine Stichprobe -> Richtung prior
    if v is None or n is None: return prior
    return (v * n + prior * k) / (n + k)

today = datetime.datetime.now(datetime.timezone.utc).date()
d_to = today.strftime("%Y%m%d"); d_from = (today - datetime.timedelta(days=7)).strftime("%Y%m%d")
sources = {}

# ---------- DraftMeta: Raten je Rang-Gruppe ----------
def dm_bans(rank, mp=None):
    q = {"endpoint": "bans", "from": d_from, "to": d_to, "rank": rank}
    if mp: q["map"] = mp
    d = get("https://draftmeta.com/api/brawl-stars/battle-stats?" + urllib.parse.urlencode(q))
    if not d or not d.get("ok"): return None
    data = d["data"]; rows = {}
    for b in data.get("brawlers", []):
        ID2NAME[b["brawlerId"]] = nm(b["name"])
        rows[nm(b["name"])] = {"pr": b.get("pickRate"), "br": b.get("banRate"), "wr": b.get("winRate"), "n": b.get("games", 0)}
    return {"drafts": data.get("drafts", 0), "rows": rows}

log("DraftMeta: Gesamtwerte …")
DM = {"all": {}, "maps": collections.defaultdict(dict)}
for g, rank in DM_RANKS.items():
    DM["all"][g] = dm_bans(rank)
log("DraftMeta: Werte pro Map …")
for mp in RANKED_MAPS:
    for g, rank in DM_RANKS.items():
        DM["maps"][mp][g] = dm_bans(rank, mp)
sources["draftmeta"] = {"from": d_from, "to": d_to,
    "drafts": {g: (DM["all"][g] or {}).get("drafts", 0) for g in DM_RANKS}}

# Hinweis: DraftMeta bietet auch eine Draft-Opening-Analyse, die ist aber rang-unabhängig
# ("rank-blind") und passt nicht zu Masters/Pro. Den First-Pick-Wert berechnet die App deshalb
# selbst mit dem Brawl-Atlas-Modell auf dem gewichteten Rang-Niveau.

# ---------- Corestats: Pro-Scrims der letzten 9 Tage ----------
def rsc_payload(t):
    return "".join(json.loads(m.group(1)) for m in re.finditer(r'self\.__next_f\.push\(\[1,("(?:[^"\\]|\\.)*")\]\)', t))
def rsc_arrays(p, key):
    dec = json.JSONDecoder(); i = 0; out = []
    while True:
        i = p.find('"%s":' % key, i)
        if i < 0: return out
        try: out.append(dec.raw_decode(p, i + len(key) + 3)[0])
        except Exception: pass
        i += 1

log("Corestats: Pro-Scrims …")
matches = {}
for k in range(9):
    day = (today - datetime.timedelta(days=k)).isoformat()
    t = get("https://corestats.pro/scrims?date=" + day, kind="text", pause=1.0)
    if not t: continue
    for arr in rsc_arrays(rsc_payload(t), "scrims"):
        if isinstance(arr, list):
            for s in arr:
                if isinstance(s, dict) and s.get("id"): matches[s["id"]] = s
MODES = {"gemGrab", "brawlBall", "heist", "hotZone", "knockout", "bounty"}
M = [m for m in matches.values() if m.get("mode") in MODES and m.get("winner") in (0, 1) and len(m.get("sides", [])) == 2]
SC = collections.defaultdict(lambda: [0, 0, 0])                      # picks, wins, bans
SC_VS = collections.defaultdict(lambda: [0, 0]); SC_SYN = collections.defaultdict(lambda: [0, 0])
for m in M:
    sides = [[nm(p["brawler"]) for p in s.get("players", [])] for s in m["sides"]]
    for b in {nm(x["name"]) for s in m["sides"] for x in s.get("bans", [])}:
        SC[b][2] += 1
    for i, side in enumerate(sides):
        w = 1 if m["winner"] == i else 0
        for b in side:
            SC[b][0] += 1; SC[b][1] += w
        for a, c in itertools.combinations(sorted(set(side)), 2):
            SC_SYN[(a, c)][0] += 1; SC_SYN[(a, c)][1] += w
        for x in side:
            for y in sides[1 - i]:
                SC_VS[(x, y)][0] += 1; SC_VS[(x, y)][1] += w
NSC = len(M)
sources["corestats"] = {"sets": NSC, "from": (today - datetime.timedelta(days=8)).isoformat(), "to": today.isoformat()}
log(f"  {NSC} Scrim-Spiele")

# ---------- Brawl Atlas: Modell + Map-Winrates je Rang ----------
log("Brawl Atlas …")
A = get("https://brawlstars-atlas.pages.dev/assets/app.js", kind="text")
ver = re.search(r'assets/data\.json\?v=([a-z0-9]+)', A or "")
AT = get("https://brawlstars-atlas.pages.dev/assets/data.json" + ("?v=" + ver.group(1) if ver else ""), pause=0.5)
MODEL = None; ATLAS_MAP = {}; ATLAS_NOTE = None
# Kurz nach Season-Start hat Atlas kaum Masters-Spiele (Rang-Reset). Das Modell der neuen Season ist trotzdem
# brauchbar (aktuelle Balance); fehlende Rang-Gruppen bekommen den Skill der höchsten vorhandenen Gruppe.
# Nur wenn fast gar keine Masters-Spiele da sind: ATLAS_FALLBACK=<data.json> oder bisheriges Modell behalten.
def masters_games(at): return sum(c[4] for c in at["ratings"]["cells"] if c[2] >= 19)
if AT and masters_games(AT) < 300:
    log(f"  neue Atlas-Season {AT['season']['season']}: nur {masters_games(AT)} Masters-Spiele, zu wenig")
    fb = os.environ.get("ATLAS_FALLBACK")
    AT = json.load(open(fb)) if fb and os.path.exists(fb) else None
    if AT: ATLAS_NOTE = "Rückfall auf andere Season"; log("  nutze", AT["season"]["season"])
    else:
        try:
            old = json.loads(open(OUT, encoding="utf-8").read().split("=", 1)[1].strip().rstrip(";"))
            MODEL = old.get("model"); sources["atlas"] = dict(old.get("sources", {}).get("atlas", {}), note="Modell aus letzter Aktualisierung behalten")
            log("  behalte bisheriges Atlas-Modell")
        except Exception as e: log("  ! kein altes Modell:", e)
if AT:
    mo, se = AT["model"], AT["season"]
    vocab = [nm(v) for v in mo["vocab"]]
    rmin, nranks = se["rank_min"], se["rank_max"] - se["rank_min"] + 1
    skill = {}
    for g, ranks in ATLAS_RANKS.items():
        n = s = 0
        for d, mi, r, _, cn, csum, band in AT["ratings"]["cells"]:
            if r in ranks: n += cn; s += csum
        skill[g] = s / n if n else None
    order = ["m12", "m3", "pro"]   # Atlas hat keine Pro-Lobbys; fehlende Gruppen: nächstniedrigere vorhandene
    for i, g in enumerate(order):
        if skill.get(g) is None: skill[g] = next((skill[h] for h in reversed(order[:i]) if skill.get(h) is not None), 0.0)
    rnd = lambda v: [round(x, 4) for x in v]
    MODEL = {
        "names": vocab, "w": rnd(mo["w"]),
        "syn": [rnd(v) for v in mo["e_syn"]], "att": [rnd(v) for v in mo["e_att"]],
        "def": [rnd(v) for v in mo["e_def"]], "ctx": [rnd(v) for v in mo["e_ctx"]],
        "maps": {mp: rnd(mo["m_map"][mo["maps"].index(mp)]) for mp in RANKED_MAPS if mp in mo["maps"]},
        "modes": {md: rnd(mo["m_mode"][i]) for i, md in enumerate(mo["modes"])},
        "vskill": rnd(mo["v_skill"]),
        "skill": {g: round(v, 4) for g, v in skill.items()},
        "skillW": round(sum(WEIGHTS[g] * skill[g] for g in WEIGHTS), 4),
    }
    days = len(AT["ratings"]["days"]); maps = se["maps"]
    for c in AT["characters"]:
        name = nm(c["name"]); grid = c["daily_rank_grid"]
        for mp in RANKED_MAPS:
            if mp not in maps: continue
            mi = maps.index(mp); out = {}
            for g, ranks in ATLAS_RANKS.items():
                n = w = 0
                for d in range(days):
                    for r in ranks:
                        at = ((d * len(maps) + mi) * nranks + (r - rmin)) * 2
                        n += grid[at]; w += grid[at + 1]
                out[g] = (n, w)
            ATLAS_MAP.setdefault(mp, {})[name] = out
    sources["atlas"] = {"season": se["season"], "games": se["games"], "from": se["first_day"], "to": se["last_day"]}
    if ATLAS_NOTE: sources["atlas"]["note"] = ATLAS_NOTE

# ---------- BrawlLab: Matchups und Teammates (Ranked, alle Ränge) ----------
LAB_VS = {}; LAB_SYN = {}
ids = sorted(ID2NAME)
log(f"BrawlLab: {len(ids)} Brawler …")
for bid in ids:
    for kind, key, store in (("brawler_matchups", "opponent_id", LAB_VS), ("brawler_teammates", "teammate_id", LAB_SYN)):
        rows = get(f"https://brawllab.gg/analytics/{kind}?brawler_id={bid}&min_games=5&limit=5000", pause=0.25)
        if not isinstance(rows, list): continue
        agg = collections.defaultdict(lambda: [0, 0])
        for r in rows:
            if r.get("brawler_id") != bid or not r.get(key): continue
            agg[r[key]][0] += r.get("ranked_decided_games") or 0
            agg[r[key]][1] += r.get("ranked_wins") or 0
        tot_n = sum(v[0] for v in agg.values()); tot_w = sum(v[1] for v in agg.values())
        base = tot_w / tot_n if tot_n else 0.5
        for oid, (n, w) in agg.items():
            if n >= 40 and oid in ID2NAME:
                store[(ID2NAME[bid], ID2NAME[oid])] = (n, shrink(w / n, n, base, 30) - base)
sources["brawllab"] = {"pairs_vs": len(LAB_VS), "pairs_syn": len(LAB_SYN)}

# ---------- BrawlPick: Konter-Tabellen ----------
log("BrawlPick …")
BP_VS = {}
idx = get("https://www.brawlpick.app/brawlers", kind="text") or ""
slugs = sorted(set(re.findall(r'href="/brawlers/([a-z0-9-]+)"', idx)))
row = re.compile(r"\| ([A-Z0-9][A-Za-z0-9.&' -]*?) \|(?: \|)* ([\d.]+) \| % \|(?: \|)* \d+ \| – \| \d+ \| % \|(?: \|)* (?:\+ \| )?(-?[\d.]+) \|(?: \|)* ([\d,]+) \|")
for slug in slugs:
    t = get(f"https://www.brawlpick.app/brawlers/{slug}/counters", kind="text", pause=0.3)
    if not t: continue
    txt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " | ", re.sub(r"(?s)<(script|style).*?</\1>", "", t)))
    head = re.search(r"Which brawlers beat \| ([^|]+?) \|", txt)
    if not head: continue
    target = nm(head.group(1).strip())
    for name, wr, vs, games in row.findall(txt[txt.find("Best counters to"):]):
        n = int(games.replace(",", ""))
        BP_VS[(nm(name), target)] = (n, float(vs) / 100)
sources["brawlpick"] = {"pairs": len(BP_VS)}

# ---------- Zusammenführen ----------
def group_stats(rows_by_group, scrim=None, nsc=0):
    """rows_by_group: {g: {pr,br,wr,n}} -> gewichtete Werte mit Schrumpfung."""
    present = {g: r for g, r in rows_by_group.items() if r}
    if not present: return None
    tot_n = sum(r["n"] for r in present.values()) or 1
    prior_wr = sum((r["wr"] or .5) * r["n"] for r in present.values()) / tot_n
    pri_pr = sum((r["pr"] or 0) for r in present.values()) / len(present)
    pri_br = sum((r["br"] or 0) for r in present.values()) / len(present)
    out = {}
    for g in WEIGHTS:
        r = present.get(g) or {"wr": None, "pr": None, "br": None, "n": 0}
        wr = shrink(r["wr"], r["n"], prior_wr, 150)
        pr = r["pr"] if r["pr"] is not None else pri_pr   # Raten beziehen sich auf alle Drafts der Gruppe
        br = r["br"] if r["br"] is not None else pri_br
        if g == "pro" and scrim and nsc:  # Pro = Ranked-Pro-Rang und Pro-Scrims, nach Stichprobe gemischt
            p, w, b = scrim; sw = smw(w, p)
            npro = r["n"] or 0
            wr = (wr * npro + sw * p) / (npro + p) if npro + p else wr
            pr = (pr + p / nsc) / 2       # Anteil der Scrim-Spiele, in denen er gepickt wurde
            br = (br + b / nsc) / 2
        out[g] = (wr, pr, br, r["n"])
    W = lambda i: sum(WEIGHTS[g] * out[g][i] for g in WEIGHTS)
    return {"wr": r4(W(0)), "pr": r4(W(1)), "br": r4(W(2)), "n": sum(o[3] for o in out.values()),
            "g": {g: [r4(o[0]), r4(o[1]), r4(o[2]), o[3]] for g, o in out.items()}}
def smw(w, n, k=10): return (w + .5 * k) / (n + k)

brawlers = {}
for name in NAMES:
    rows = {g: (DM["all"][g] or {"rows": {}})["rows"].get(name) for g in WEIGHTS}
    st = group_stats(rows, SC.get(name), NSC)
    if st:
        if name in SC: st["scrim"] = SC[name]
        brawlers[name] = st

maps = {}
for mp in RANKED_MAPS:
    maps[mp] = {}
    for name in NAMES:
        rows = {}
        for g in WEIGHTS:
            dm = (DM["maps"][mp].get(g) or {"rows": {}})["rows"].get(name)
            an, aw = (ATLAS_MAP.get(mp, {}).get(name, {}).get(g) or (0, 0))
            if dm or an:  # DraftMeta (aktuell) und Atlas (vorige Season) nach Spielen mischen
                dn = dm["n"] if dm else 0
                dwr = (dm.get("wr") or .5) if dm else .5
                wr = (dwr * dn + aw) / (dn + an) if dn + an else None
                rows[g] = {"wr": wr, "pr": dm["pr"] if dm else None, "br": dm["br"] if dm else None, "n": dn + an}
        st = group_stats(rows) if rows else None
        if not st: continue
        st.pop("g", None)
        maps[mp][name] = st

def merge_pairs(parts):
    """parts: [(weight, {(a,b): (n, adv)})] -> {(a,b): [adv, n]} gewichtet nach Quelle und Stichprobe."""
    acc = collections.defaultdict(lambda: [0.0, 0.0, 0])
    for wsrc, d in parts:
        for key, (n, adv) in d.items():
            c = wsrc * n / (n + 100)
            acc[key][0] += c * adv; acc[key][1] += c; acc[key][2] += n
    return {k: [round(v[0] / v[1], 4), v[2]] for k, v in acc.items() if v[1] > 0 and abs(v[0] / v[1]) >= 0.02}

base = {b: smw(v[1], v[0]) for b, v in SC.items()}
cs_vs = {(a, b): (n, smw(w, n, 8) - base[a]) for (a, b), (n, w) in SC_VS.items() if n >= 12}
cs_syn = {(a, b): (n, smw(w, n, 8) - (base[a] + base[b]) / 2) for (a, b), (n, w) in SC_SYN.items() if n >= 12}
lab_syn = {tuple(sorted(k)): v for k, v in LAB_SYN.items()}
# BrawlLab und BrawlPick haben keinen Datumsfilter (können Spiele vor dem letzten Balance-Update enthalten): halbe Gewichtung
VS = merge_pairs([(WEIGHTS["pro"], cs_vs), (0.15, LAB_VS), (0.15, BP_VS)])
SYN = merge_pairs([(WEIGHTS["pro"], cs_syn), (0.3, lab_syn)])

stats = {
    "generated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    "weights": WEIGHTS, "sources": sources,
    "brawlers": brawlers, "maps": maps, "model": MODEL,
    "vs": {f"{a}|{b}": v for (a, b), v in VS.items()},
    "syn": {f"{a}|{b}": v for (a, b), v in SYN.items()},
}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write("// Automatisch erzeugt von scripts/update_data.py – nicht von Hand bearbeiten.\n")
    f.write("window.STATS = " + json.dumps(stats, ensure_ascii=False, separators=(",", ":")) + ";\n")
# Offline-Cache-Version erhöhen, damit installierte Apps die neuen Daten laden
sw = open(SW, encoding="utf-8").read()
sw = re.sub(r'const VERSION = "[^"]*";', f'const VERSION = "draft-coach-{datetime.datetime.now(datetime.timezone.utc):%Y%m%d%H%M}";', sw)
open(SW, "w", encoding="utf-8").write(sw)
log(f"Fertig: {OUT} ({os.path.getsize(OUT) // 1024} KB) · {len(brawlers)} Brawler · {len(VS)} Matchups · {len(SYN)} Kombis")
