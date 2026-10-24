<html lang="fi"><body>#!/usr/bin/env python3
"""Rakentaa GitHub Pages -sivuston Claude Docs -viennin HTML-tiedostoista."""
import re, html, os, pathlib

SRC = pathlib.Path(__file__).parent / "src"
OUT = pathlib.Path(__file__).parent / "docs"
OUT.mkdir(exist_ok=True)

PAGES = [
    ("index.html", "Politiikkasuositus.html", "Politiikkasuositus"),
    ("hallituksen-linja.html", "Hallituksen linja.html", "Hallituksen linja"),
    ("liberaali-vaihtoehto.html", "Liberaali sote-politiikka.html", "Liberaali sote-politiikka"),
    ("alue-erittely.html", "Alue-erittely.html", "Alue-erittely"),
    ("sote-tehtavat.html", "app:sote-tehtavat.html", "Sote-tehtävät laissa"),
    ("laki-ja-palvelukokonaisuudet.html", "app:laki-ja-palvelukokonaisuudet.html", "Laki ja palvelukokonaisuudet"),
    ("sanasto.html", "Sanasto.html", "Sanasto"),
]
ROOT = pathlib.Path(__file__).parent

# Interaktiiviset sivut (alkuperäiset Claude-artefaktit), upotetaan iframeen
APP_OVERRIDE = """
"""

def build_app(name):
    s = (ROOT / "apps_src" / name).read_text()
    s = re.sub(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com/css2\?[^" ]*"="">',
               '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&amp;family=Raleway:ital,wght@0,400;0,500;0,600;0,700;1,400&amp;display=swap">', s)
    s = s.replace('href="https://claude.ai/artifact/3hMHCQ342XTMvqZuJodMiq"', 'href="../sote-tehtavat.html" target="_top"')
    s = s.replace("", APP_OVERRIDE + "\n", 1)
    (OUT / "apps").mkdir(exist_ok=True)
    (OUT / "apps" / name).write_text(s)
SITE_TITLE = "Parempi hoiva vähentämällä hukkaa"

# ---------- kaaviot (inline SVG) ----------
def fmt(v, d=1):
    return f"{v:.{d}f}".replace(".", ",")

def line_chart():
    rows = {
        "Perusura": [24.94,25.16,25.39,25.61,25.84,26.07,26.30,26.54,26.77,27.01,27.25],
        "Skenaario 1": [24.94,25.16,25.14,25.11,25.14,25.19,25.38,25.56,25.77,25.99,26.20],
        "Skenaario 2": [24.94,25.16,24.79,24.41,24.14,24.07,24.30,24.54,24.72,24.91,25.15],
    }
    years = list(range(2025, 2036))
    W, H, L, R, T, B = 720, 340, 56, 110, 16, 36
    ymin, ymax = 23.5, 27.5
    X = lambda i: L + i * (W - L - R) / (len(years) - 1)
    Y = lambda v: T + (ymax - v) / (ymax - ymin) * (H - T - B)
    g = []
    for t in [24, 25, 26, 27]:
        g.append(f'<line class="grid" x1="{L}" x2="{W-R}" y1="{Y(t):.1f}" y2="{Y(t):.1f}">'
                 f'<text class="tick" x="{L-8}" y="{Y(t)+4:.1f}" text-anchor="end">{t}</text>')
    for i, yr in enumerate(years):
        if i % 2 == 0:
            g.append(f'<text class="tick" x="{X(i):.1f}" y="{H-B+18}" text-anchor="middle">{yr}</text>')
    for k, (name, vals) in enumerate(rows.items()):
        pts = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(vals))
        g.append(f'<polyline class="s{k+1}" fill="none" stroke-width="2" points="{pts}">')
        g.append(f'<text class="dlabel" x="{X(len(vals)-1)+8:.1f}" y="{Y(vals[-1])+4:.1f}">{name} {fmt(vals[-1])}</text>')
        for i, v in enumerate(vals):
            g.append(f'<circle class="hit s{k+1}f" cx="{X(i):.1f}" cy="{Y(v):.1f}" r="4" '="" f'data-tip="{name}, {years[i]}: {fmt(v,2)} mrd €">')
    table = "".join(f"{y}" + "".join(f"{fmt(rows[n][i],2)}" for n in rows) + ""
                    for i, y in enumerate(years))
    return figure("Menot 2035: 27,3 – 26,2 – 25,2 mrd €",
                  "Sote-nettokäyttökustannukset, Manner-Suomi, mrd € vuoden 2025 hinnoin. Perusura = palvelutarpeen kasvu 0,89 % vuodessa (VM:n rahoituslaskelma 2027).",
                  f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Menoura 2025–2035 kolmessa skenaariossa">{"".join(g)}</svg>',
                  legend=[("s1", "Perusura"), ("s2", "Skenaario 1"), ("s3", "Skenaario 2")],
                  table=f"Vuosi{''.join(f'{n}' for n in rows)}{table}")

def index_chart():
    data = [("Keski-Suomi",1.08,1.058,1.091),("Kymenlaakso",1.073,1.038,1.093),("Etelä-Savo",1.071,1.058,1.08),
            ("Keski-Uusimaa",1.06,1.044,1.07),("Etelä-Karjala",1.028,1.001,1.053),("Etelä-Pohjanmaa",1.023,0.996,1.049),
            ("Pohjanmaa",1.018,1.013,1.023),("Satakunta",1.015,1.006,1.029),("Helsinki",1.007,1.0,1.016),
            ("Vantaa ja Kerava",1.005,0.945,1.056),("Pohjois-Savo",1.001,0.984,1.018),("Kanta-Häme",1.0,0.989,1.006),
            ("Pirkanmaa",0.993,0.981,1.014),("Kainuu",0.99,0.977,1.008),("Itä-Uusimaa",0.988,0.963,1.005),
            ("Lappi",0.981,0.976,0.99),("Pohjois-Pohjanmaa",0.974,0.966,0.985),("Länsi-Uusimaa",0.972,0.953,1.005),
            ("Varsinais-Suomi",0.964,0.944,0.977),("Päijät-Häme",0.962,0.941,0.994),("Keski-Pohjanmaa",0.948,0.945,0.951),
            ("Pohjois-Karjala",0.927,0.896,0.949)]
    W, L, R, T, rowh = 720, 140, 30, 10, 22
    H = T + rowh * len(data) + 34
    xmin, xmax = 0.88, 1.12
    X = lambda v: L + (v - xmin) / (xmax - xmin) * (W - L - R)
    g = []
    for t in [0.90, 0.95, 1.00, 1.05, 1.10]:
        g.append(f'<line class="{" ref"="" if="" t="=1" else="" "grid"}"="" x1="{X(t):.1f}" x2="{X(t):.1f}" y1="{T}" y2="{H-30}">'
                 f'<text class="tick" x="{X(t):.1f}" y="{H-12}" text-anchor="middle">{fmt(t,2)}</text>')
    g.append(f'<text class="tick" x="{X(1)+4:.1f}" y="{T+8}">Keskitaso</text>')
    for i, (a, v, lo, hi) in enumerate(data):
        y = T + rowh * i + rowh / 2
        cls = "s2f" if v &gt;= 1.03 else "s1f"
        g.append(f'<text class="tick" x="{L-8}" y="{y+4:.1f}" text-anchor="end">{a}</text>'
                 f'<line class="whisk" x1="{X(lo):.1f}" x2="{X(hi):.1f}" y1="{y:.1f}" y2="{y:.1f}">'
                 f'<circle class="{cls} hit" cx="{X(v):.1f}" cy="{y:.1f}" r="5" '="" f'data-tip="{a}: {fmt(v,3)} (vaihteluväli {fmt(lo,3)}–{fmt(hi,3)})">')
    table = "".join(f"{a}{fmt(v,3)}{fmt(lo,3)}–{fmt(hi,3)}" for a, v, lo, hi in data)
    return figure("Kolme aluetta 7–8 % yli tarpeen",
                  "Nettokäyttökustannus suhteessa rahoitusmallin laskennalliseen tarpeeseen, 1,00 = Manner-Suomen taso. Piste = 2023–2025 keskiarvo, viiva = vuosien pienin ja suurin. Lähde: Budjettihaukan BigQuery (Valtiokonttorin HHTPP-raportointi) ja VM:n rahoituslaskelmat.",
                  f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Tarvevakioitu kustannusindeksi alueittain">{"".join(g)}</svg>',
                  legend=[("s2", "Yli 3 % keskitason yläpuolella"), ("s1", "Muut alueet")],
                  table=f"AlueIndeksiVaihteluväli{table}")

def bar_chart():
    data = [("2024",-105),("2025",-394),("2026",-468),("2027",-715)]
    W, H, L, R, T, B = 720, 320, 64, 20, 28, 30
    ymin = -800
    bw = (W - L - R) / len(data)
    Y = lambda v: T + (0 - v) / (0 - ymin) * (H - T - B)
    g = []
    for t in [0, -200, -400, -600, -800]:
        g.append(f'<line class="{" axis0"="" if="" t="=0" else="" "grid"}"="" x1="{L}" x2="{W-R}" y1="{Y(t):.1f}" y2="{Y(t):.1f}">'
                 f'<text class="tick" x="{L-8}" y="{Y(t)+4:.1f}" text-anchor="end">{str(t).replace("-","−")}</text>')
    for i, (yr, v) in enumerate(data):
        x = L + i * bw + bw * 0.25; w = bw * 0.5; y0 = Y(0); y1 = Y(v)
        g.append(f'<text class="tick" x="{x+w/2:.1f}" y="{T-10}" text-anchor="middle">{yr}</text>'
                 f'<path class="hotf hit" d="M{x:.1f},{y0:.1f} V{y1-4:.1f} Q{x:.1f},{y1:.1f} {x+4:.1f},{y1:.1f} H{x+w-4:.1f} Q{x+w:.1f},{y1:.1f} {x+w:.1f},{y1-4:.1f} V{y0:.1f} Z" data-tip="{yr}: −{-v} M€ vuodessa">'
                 f'<text class="dlabel" x="{x+w/2:.1f}" y="{y1+16:.1f}" text-anchor="middle">−{-v}</text>')
    table = "".join(f"{y}−{-v}" for y, v in data)
    return figure("Rahoitusta 0,7 mrd € vähemmän 2027",
                  "Hallituksen päätösperäiset vähennykset alueiden rahoitukseen kumulatiivisesti, M€ vuodessa. 2027 sisältää rahoituslain 60 %:n säännön. Ei sisällä STEA-leikkauksia eikä Kelan korvauksia. Oma laskelma talousarvioesityksistä 2024–2027.",
                  f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Rahoitusvähennykset 2024–2027">{"".join(g)}</svg>',
                  legend=None,
                  table=f"VuosiMuutos, M€{table}")

def figure(title, note, svg, legend, table):
    leg = ""
    if legend:
        leg = '<div class="legend">' + "".join(f'<span><i class="{c}f"></i>{n}</span>' for c, n in legend) + "</div>"
    return (f'<figure class="chart"><div class="chart-title">{title}</div>{leg}{svg}'
            f'<figcaption>{note}</figcaption><details><summary>Näytä luvut taulukkona</summary>'
            f'{table}<table></table></details></figure>')


import json as _json
ALUE = _json.loads((SRC / "alue_charts.json").read_text())

def alue_bar_chart():
    data = sorted(ALUE["bars"], key=lambda r: -r["meur"])
    W, L, R, T, rowh = 720, 140, 40, 8, 26
    H = T + rowh * len(data) + 34
    xmax = 100
    X = lambda v: L + v / xmax * (W - L - R)
    g = []
    for t in [0, 20, 40, 60, 80, 100]:
        g.append(f'<line class="grid" x1="{X(t):.1f}" x2="{X(t):.1f}" y1="{T}" y2="{H-30}"><text class="tick" x="{X(t):.1f}" y="{H-12}" text-anchor="middle">{t}</text>')
    for i, r in enumerate(data):
        y = T + rowh * i + 4; h = rowh - 8; w = X(r["meur"]) - L
        cls = "s1f" if i &lt; 4 else "mutedf"
        g.append(f'<text class="tick" x="{L-8}" y="{y+h/2+4:.1f}" text-anchor="end">{r["alue"]}</text>'
                 f'<path class="{cls} hit" d="M{L},{y} H{L+max(w-4,0):.1f} Q{L+w:.1f},{y} {L+w:.1f},{y+4} V{y+h-4} Q{L+w:.1f},{y+h} {L+max(w-4,0):.1f},{y+h} H{L} Z" data-tip="{r[" alue"]}:="" {r["meur"]}="" m€="" vuodessa"="">'
                 f'<text class="dlabel" x="{L+w+6:.1f}" y="{y+h/2+4:.1f}">{r["meur"]}</text>')
    tot = sum(r["meur"] for r in data)
    table = "".join(f'{r["alue"]}{r["meur"]}' for r in data)
    return figure(f"Ylitys noin {round(tot,-1):.0f} M€ kertyy {len(data)} alueelta",
                  "Tarvevakioitu ylitys keskitason yläpuolella, M€ vuodessa (vuoden 2025 kustannustaso, indeksi 2023–2025 keskiarvo). Neljä kalleinta aluetta (korostettu) kattaa 250 M€. Lähde: Budjettihaukan BigQuery (Valtiokonttorin HHTPP-raportointi) ja VM:n rahoituslaskelmat.",
                  f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Tarvevakioitu ylitys alueittain">{"".join(g)}</svg>',
                  legend=None, table=f"AlueYlitys, M€/v{table}")

def alue_dumbbell_chart():
    rows = ALUE["dumb"]
    areas = []
    for r in rows:
        if r["alue"] not in areas: areas.append(r["alue"])
    v = {(r["alue"], r["vuosi"]): r["idx"] for r in rows}
    W, L, R, T, rowh = 720, 140, 30, 10, 22
    H = T + rowh * len(areas) + 34
    xmin, xmax = 0.88, 1.12
    X = lambda x: L + (x - xmin) / (xmax - xmin) * (W - L - R)
    g = []
    for t in [0.90, 0.95, 1.00, 1.05, 1.10]:
        g.append(f'<line class="{" ref"="" if="" t="=1" else="" "grid"}"="" x1="{X(t):.1f}" x2="{X(t):.1f}" y1="{T}" y2="{H-30}"><text class="tick" x="{X(t):.1f}" y="{H-12}" text-anchor="middle">{fmt(t,2)}</text>')
    g.append(f'<text class="tick" x="{X(1)+4:.1f}" y="{T+8}">Keskitaso</text>')
    for i, a in enumerate(areas):
        y = T + rowh * i + rowh / 2
        a0, a1 = v[(a, "2023")], v[(a, "2025")]
        g.append(f'<text class="tick" x="{L-8}" y="{y+4:.1f}" text-anchor="end">{a}</text>'
                 f'<line class="whisk" x1="{X(a0):.1f}" x2="{X(a1):.1f}" y1="{y:.1f}" y2="{y:.1f}">'
                 f'<circle class="yr0f hit" cx="{X(a0):.1f}" cy="{y:.1f}" r="5" data-tip="{a} 2023: {fmt(a0,3)}">'
                 f'<circle class="s1f hit" cx="{X(a1):.1f}" cy="{y:.1f}" r="5" data-tip="{a} 2025: {fmt(a1,3)}">')
    table = "".join(f'{a}{fmt(v[(a,"2023")],3)}{fmt(v[(a,"2025")],3)}' for a in areas)
    return figure("Kolme neljästä kalleimmasta kallistui",
                  "Tarvevakioitu kustannusindeksi 2023 ja 2025, 1,00 = Manner-Suomen taso. Keski-Suomi, Kymenlaakso ja Etelä-Savo erkanivat keskitasosta, Keski-Uusimaa lähestyi sitä.",
                  f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Indeksin muutos 2023–2025">{"".join(g)}</svg>',
                  legend=[("yr0", "2023"), ("s1", "2025")],
                  table=f"Alue20232025{table}")

def alue_heat_chart():
    rows = ALUE["heat"]
    secs = [r["sektori"] for r in rows if r["alue"] == rows[0]["alue"]]
    areas = [r["alue"] for r in rows if r["sektori"] == secs[0]]
    W, L, T, rowh = 720, 150, 28, 24
    cw = (W - L - 10) / len(secs)
    H = T + rowh * len(areas) + 8
    g = []
    for j, s_ in enumerate(secs):
        g.append(f'<text class="tick" x="{L + j*cw + cw/2:.1f}" y="{T-10}" text-anchor="middle">{s_}</text>')
    for i, a in enumerate(areas):
        g.append(f'<text class="tick" x="{L-8}" y="{T + i*rowh + 16}" text-anchor="end">{a}</text>')
    for r in rows:
        i, j = areas.index(r["alue"]), secs.index(r["sektori"])
        op = min(0.7, 0.06 + abs(r["idx"] - 1) * 2)
        cls = "hotf" if r["idx"] &gt;= 1 else "s1f"
        x = L + j*cw + 2; y = T + i*rowh + 1
        g.append(f'<rect class="{cls} hit" x="{x:.1f}" y="{y}" width="{cw-4:.1f}" height="{rowh-2}" rx="3" fill-opacity="{op:.2f}" data-tip="{r[" alue"]},="" {r["sektori"]}:="" {fmt(r["idx"],2)}"="">'
                 f'<text class="cell" x="{x + (cw-4)/2:.1f}" y="{y+15}" text-anchor="middle">{fmt(r["idx"],2)}</text>')
    table = "".join("" + a + "" + "".join(f'{fmt(next(r["idx"] for r in rows if r["alue"]==a and r["sektori"]==s_),2)}' for s_ in secs) + "" for a in areas)
    return figure("Kallein sektori vaihtelee alueittain",
                  "Tarvevakioitu indeksi sektoreittain, 2023–2025 keskiarvo, 1,00 = keskitaso. Mitä voimakkaampi väri, sitä suurempi ero keskitasoon.",
                  f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Sektorikohtainen indeksi alueittain">{"".join(g)}</svg>',
                  legend=[("hot", "Keskitasoa kalliimpi"), ("s1", "Keskitasoa halvempi")],
                  table=f"Alue{''.join(f'{s_}' for s_ in secs)}{table}")

CHARTS = {
    "node/a6e7b5bb-705c": line_chart,
    "node/1deadadd-90eb": index_chart,
    "node/f3379a10-f736": bar_chart,
    "node/03355f26-3d3b": alue_bar_chart,
    "node/a5755818-dc3f": alue_dumbbell_chart,
    "node/a10326e4-e09d": alue_heat_chart,
}

# ---------- sisältö ----------
def slug_ok(s):
    return re.sub(r"[^a-z0-9äöå-]", "", s)

def process(body, fname):
    body = re.sub(r'<figure data-embed="([^" ]+)"="">.*?</figure>',
                  lambda m: CHARTS[m.group(1)]() if m.group(1) in CHARTS else "", body, flags=re.S)
    # taulukot vieritettäviksi
    def _wrap(m):
        t = m.group(0)
        head = re.search(r".*?", t, re.S)
        ncol = len(re.findall(r"<th[>]", head.group(0))) if head else 0
        rows = max(1, len(re.findall(r"", t)))
        density = len(re.sub(r"&lt;[^&gt;]+&gt;", "", t)) / rows
        # leveä asettelu vain, jos sarakkeita on paljon JA soluissa paljon tekstiä
        cls = "tablewrap wide" if ncol &gt;= 5 and density &gt;= 150 else "tablewrap"
        return f'<div class="{cls}">{t}</div>'
    body = re.sub(r".*?<table></table>", _wrap, body, flags=re.S)
    # figure-taulukot eivät tarvitse kääremuutosta, siivotaan tuplakääre detailsin sisältä
    body = re.sub(r'(<details><summary>[^&lt;]*</summary>)<div class="tablewrap">(.*?<table></table>)</div>',
                  r"\1\2", body, flags=re.S)
    # liikennevalot: merkitään solut
    body = body.replace("🔴", '🔴').replace("🟢", '🟢').replace("🟡", '🟡')
    # ristiviittaukset välilehtiin
    body = body.replace("välilehti Suositus", '<a href="https://raw.githubusercontent.com/juntunen-ai/liberaali-sote/main/index.html">välilehti Politiikkasuositus</a>')
    body = re.sub(r"(Alueittainen erittely siitä, mistä ylitys syntyy: )Alue-erittely",
                  r'\1<a href="https://raw.githubusercontent.com/juntunen-ai/liberaali-sote/main/alue-erittely.html">Alue-erittely</a>', body)
    body = body.replace("Hallituksen linja -välilehden", '<a href="https://raw.githubusercontent.com/juntunen-ai/liberaali-sote/main/hallituksen-linja.html">Hallituksen linja</a> -välilehden')
    body = re.sub(r'<span data-atom="mention" [^="">]*&gt;[^&lt;]*</span>', "Harri Juntunen", body)
    body = re.sub(r'<p><time[^>]*&gt;(\d{4})-(\d{2})-(\d{2}) · Harri Juntunen</time[^></p>', lambda m: f'<p class="byline">{int(m.group(3))}.{int(m.group(2))}.{m.group(1)} · Harri Juntunen</p>', body)
    body = re.sub(r'<a data-atom="ref" data-ref="file/76c5cc30-4152">[^&lt;]*</a>', '<a href="https://raw.githubusercontent.com/juntunen-ai/liberaali-sote/main/liberaali-vaihtoehto.html">Liberaali sote-politiikka</a>', body)
    body = body.replace("välilehdellä Politiikkasuositus", '<a href="https://raw.githubusercontent.com/juntunen-ai/liberaali-sote/main/index.html">välilehdellä Politiikkasuositus</a>')
    body = body.replace("välilehdellä Hallituksen linja", '<a href="https://raw.githubusercontent.com/juntunen-ai/liberaali-sote/main/hallituksen-linja.html">välilehdellä Hallituksen linja</a>')
    body = body.replace("välilehdillä Sote-tehtävät laissa ja Laki ja palvelukokonaisuudet", 'välilehdillä <a href="https://raw.githubusercontent.com/juntunen-ai/liberaali-sote/main/sote-tehtavat.html">Sote-tehtävät laissa</a> ja <a href="https://raw.githubusercontent.com/juntunen-ai/liberaali-sote/main/laki-ja-palvelukokonaisuudet.html">Laki ja palvelukokonaisuudet</a>')
    body = body.replace("(ks. Hallituksen linja, luvut 3–5)", '(ks. <a href="https://raw.githubusercontent.com/juntunen-ai/liberaali-sote/main/hallituksen-linja.html#3-vaikutukset-palveluihin">Hallituksen linja, luvut 3–5</a>)')
    # ulkoiset linkit uuteen välilehteen
    body = re.sub(r'<a href="https://raw.githubusercontent.com/juntunen-ai/liberaali-sote/main/(https?://[^" ]+)"',="" r'<a="" target="_blank" rel="noopener" ',="" body)="" return="" body="" def="" toc(body):="" items="re.findall(r'<h2" id="([^" ]+)"="">(.*?)', body)
    if len(items) &lt; 3:
        return ""
    lis = "".join(f'</a><li><a href="https://raw.githubusercontent.com/juntunen-ai/liberaali-sote/main/(https?://[^" ]+)"',="" r'<a="" target="_blank" rel="noopener" ',="" body)="" return="" body="" def="" toc(body):="" items="re.findall(r'<h2" id="([^" ]+)"=""></a><a href="https://raw.githubusercontent.com/juntunen-ai/liberaali-sote/main/build.py#{i}">{re.sub("&lt;[^&gt;]+&gt;","",t)}</a></li>' for i, t in items)
    return f''

CSS = (pathlib.Path(__file__).parent / "style.css").read_text()
JS = (pathlib.Path(__file__).parent / "tip.js").read_text()

for out, src, label in PAGES:
    if src.startswith("app:"):
        build_app(src[4:])
        body = f'<iframe class="app" src="apps/{src[4:]}" title="{html.escape(label)}"></iframe>'
    else:
        body = (SRC / src).read_text()
        body = process(body, src)
    h1 = re.search(r"<h1[^>]*&gt;(.*?)", body)
    ptitle = re.sub("&lt;[^&gt;]+&gt;", "", h1.group(1)) if h1 else label
    cur = ' aria-current="page"'
    nav = "".join(f'<a href="https://raw.githubusercontent.com/juntunen-ai/liberaali-sote/main/%7Bo%7D" {cur="" if="" o="=out" else="" ""}="">{l}</a>' for o, _, l in PAGES)
    page = f"""




<title>{html.escape(ptitle) + " · " + SITE_TITLE if ptitle != SITE_TITLE else SITE_TITLE}</title>

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="">
<link href="https://fonts.googleapis.com/css2?family=Raleway:ital,wght@0,400;0,500;0,600;0,700;1,400&amp;display=swap" rel="stylesheet">




<main class="wrap">
{toc(body)}
<article>{body}</article>
</main>

<div id="tip" role="tooltip" hidden=""></div>



"""
    (OUT / out).write_text(page)
    print("wrote", out, len(page))
(OUT / ".nojekyll").write_text("")
</h1[^></details></th[></rect></circle></circle></line></line></path></line></path></line></circle></line></line></circle></polyline></line></body></html>