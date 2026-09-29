#!/usr/bin/env python3
"""Rakentaa GitHub Pages -sivuston Claude Docs -viennin HTML-tiedostoista."""
import re, html, os, pathlib

SRC = pathlib.Path(__file__).parent / "src"
OUT = pathlib.Path(__file__).parent / "docs"
OUT.mkdir(exist_ok=True)

PAGES = [
    ("index.html", "Politiikkasuositus.html", "Politiikkasuositus"),
    ("hallituksen-linja.html", "Hallituksen linja.html", "Hallituksen linja"),
    ("liberaali-vaihtoehto.html", "Liberaali vaihtoehto.html", "Liberaali vaihtoehto"),
    ("alue-erittely.html", "Alue-erittely.html", "Alue-erittely"),
    ("sanasto.html", "Sanasto.html", "Sanasto"),
]
SITE_TITLE = "Miljardi hukasta, ei hoidosta"

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
        g.append(f'<line class="grid" x1="{L}" x2="{W-R}" y1="{Y(t):.1f}" y2="{Y(t):.1f}"/>'
                 f'<text class="tick" x="{L-8}" y="{Y(t)+4:.1f}" text-anchor="end">{t}</text>')
    for i, yr in enumerate(years):
        if i % 2 == 0:
            g.append(f'<text class="tick" x="{X(i):.1f}" y="{H-B+18}" text-anchor="middle">{yr}</text>')
    for k, (name, vals) in enumerate(rows.items()):
        pts = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(vals))
        g.append(f'<polyline class="s{k+1}" fill="none" stroke-width="2" points="{pts}"/>')
        g.append(f'<text class="dlabel" x="{X(len(vals)-1)+8:.1f}" y="{Y(vals[-1])+4:.1f}">{name} {fmt(vals[-1])}</text>')
        for i, v in enumerate(vals):
            g.append(f'<circle class="hit s{k+1}f" cx="{X(i):.1f}" cy="{Y(v):.1f}" r="4" '
                     f'data-tip="{name}, {years[i]}: {fmt(v,2)} mrd €"/>')
    table = "".join(f"<tr><td>{y}</td>" + "".join(f"<td>{fmt(rows[n][i],2)}</td>" for n in rows) + "</tr>"
                    for i, y in enumerate(years))
    return figure("Menot 2035: 27,3 – 26,2 – 25,2 mrd €",
                  "Sote-nettokäyttökustannukset, Manner-Suomi, mrd € vuoden 2025 hinnoin. Perusura = palvelutarpeen kasvu 0,89 % vuodessa (VM:n rahoituslaskelma 2027).",
                  f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Menoura 2025–2035 kolmessa skenaariossa">{"".join(g)}</svg>',
                  legend=[("s1", "Perusura"), ("s2", "Skenaario 1"), ("s3", "Skenaario 2")],
                  table=f"<thead><tr><th>Vuosi</th>{''.join(f'<th>{n}</th>' for n in rows)}</tr></thead><tbody>{table}</tbody>")

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
        g.append(f'<line class="{"ref" if t==1 else "grid"}" x1="{X(t):.1f}" x2="{X(t):.1f}" y1="{T}" y2="{H-30}"/>'
                 f'<text class="tick" x="{X(t):.1f}" y="{H-12}" text-anchor="middle">{fmt(t,2)}</text>')
    g.append(f'<text class="tick" x="{X(1)+4:.1f}" y="{T+8}">Keskitaso</text>')
    for i, (a, v, lo, hi) in enumerate(data):
        y = T + rowh * i + rowh / 2
        cls = "s2f" if v >= 1.03 else "s1f"
        g.append(f'<text class="tick" x="{L-8}" y="{y+4:.1f}" text-anchor="end">{a}</text>'
                 f'<line class="whisk" x1="{X(lo):.1f}" x2="{X(hi):.1f}" y1="{y:.1f}" y2="{y:.1f}"/>'
                 f'<circle class="{cls} hit" cx="{X(v):.1f}" cy="{y:.1f}" r="5" '
                 f'data-tip="{a}: {fmt(v,3)} (vaihteluväli {fmt(lo,3)}–{fmt(hi,3)})"/>')
    table = "".join(f"<tr><td>{a}</td><td>{fmt(v,3)}</td><td>{fmt(lo,3)}–{fmt(hi,3)}</td></tr>" for a, v, lo, hi in data)
    return figure("Kolme aluetta 7–8 % yli tarpeen",
                  "Nettokäyttökustannus suhteessa rahoitusmallin laskennalliseen tarpeeseen, 1,00 = Manner-Suomen taso. Piste = 2023–2025 keskiarvo, viiva = vuosien pienin ja suurin. Lähde: Budjettihaukan BigQuery (Valtiokonttorin HHTPP-raportointi) ja VM:n rahoituslaskelmat.",
                  f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Tarvevakioitu kustannusindeksi alueittain">{"".join(g)}</svg>',
                  legend=[("s2", "Yli 3 % keskitason yläpuolella"), ("s1", "Muut alueet")],
                  table=f"<thead><tr><th>Alue</th><th>Indeksi</th><th>Vaihteluväli</th></tr></thead><tbody>{table}</tbody>")

def bar_chart():
    data = [("2024",-105),("2025",-394),("2026",-468),("2027",-715)]
    W, H, L, R, T, B = 720, 320, 64, 20, 28, 30
    ymin = -800
    bw = (W - L - R) / len(data)
    Y = lambda v: T + (0 - v) / (0 - ymin) * (H - T - B)
    g = []
    for t in [0, -200, -400, -600, -800]:
        g.append(f'<line class="{"axis0" if t==0 else "grid"}" x1="{L}" x2="{W-R}" y1="{Y(t):.1f}" y2="{Y(t):.1f}"/>'
                 f'<text class="tick" x="{L-8}" y="{Y(t)+4:.1f}" text-anchor="end">{str(t).replace("-","−")}</text>')
    for i, (yr, v) in enumerate(data):
        x = L + i * bw + bw * 0.25; w = bw * 0.5; y0 = Y(0); y1 = Y(v)
        g.append(f'<text class="tick" x="{x+w/2:.1f}" y="{T-10}" text-anchor="middle">{yr}</text>'
                 f'<path class="hotf hit" d="M{x:.1f},{y0:.1f} V{y1-4:.1f} Q{x:.1f},{y1:.1f} {x+4:.1f},{y1:.1f} H{x+w-4:.1f} Q{x+w:.1f},{y1:.1f} {x+w:.1f},{y1-4:.1f} V{y0:.1f} Z" data-tip="{yr}: −{-v} M€ vuodessa"/>'
                 f'<text class="dlabel" x="{x+w/2:.1f}" y="{y1+16:.1f}" text-anchor="middle">−{-v}</text>')
    table = "".join(f"<tr><td>{y}</td><td>−{-v}</td></tr>" for y, v in data)
    return figure("Rahoitusta 0,7 mrd € vähemmän 2027",
                  "Hallituksen päätösperäiset vähennykset alueiden rahoitukseen kumulatiivisesti, M€ vuodessa. 2027 sisältää rahoituslain 60 %:n säännön. Ei sisällä STEA-leikkauksia eikä Kelan korvauksia. Oma laskelma talousarvioesityksistä 2024–2027.",
                  f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Rahoitusvähennykset 2024–2027">{"".join(g)}</svg>',
                  legend=None,
                  table=f"<thead><tr><th>Vuosi</th><th>Muutos, M€</th></tr></thead><tbody>{table}</tbody>")

def figure(title, note, svg, legend, table):
    leg = ""
    if legend:
        leg = '<div class="legend">' + "".join(f'<span><i class="{c}f"></i>{n}</span>' for c, n in legend) + "</div>"
    return (f'<figure class="chart"><div class="chart-title">{title}</div>{leg}{svg}'
            f'<figcaption>{note}</figcaption><details><summary>Näytä luvut taulukkona</summary>'
            f'<table>{table}</table></details></figure>')


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
        g.append(f'<line class="grid" x1="{X(t):.1f}" x2="{X(t):.1f}" y1="{T}" y2="{H-30}"/><text class="tick" x="{X(t):.1f}" y="{H-12}" text-anchor="middle">{t}</text>')
    for i, r in enumerate(data):
        y = T + rowh * i + 4; h = rowh - 8; w = X(r["meur"]) - L
        cls = "s1f" if i < 4 else "mutedf"
        g.append(f'<text class="tick" x="{L-8}" y="{y+h/2+4:.1f}" text-anchor="end">{r["alue"]}</text>'
                 f'<path class="{cls} hit" d="M{L},{y} H{L+max(w-4,0):.1f} Q{L+w:.1f},{y} {L+w:.1f},{y+4} V{y+h-4} Q{L+w:.1f},{y+h} {L+max(w-4,0):.1f},{y+h} H{L} Z" data-tip="{r["alue"]}: {r["meur"]} M€ vuodessa"/>'
                 f'<text class="dlabel" x="{L+w+6:.1f}" y="{y+h/2+4:.1f}">{r["meur"]}</text>')
    tot = sum(r["meur"] for r in data)
    table = "".join(f'<tr><td>{r["alue"]}</td><td>{r["meur"]}</td></tr>' for r in data)
    return figure(f"Ylitys noin {round(tot,-1):.0f} M€ kertyy {len(data)} alueelta",
                  "Tarvevakioitu ylitys keskitason yläpuolella, M€ vuodessa (vuoden 2025 kustannustaso, indeksi 2023–2025 keskiarvo). Neljä kalleinta aluetta (korostettu) kattaa 250 M€. Lähde: Budjettihaukan BigQuery (Valtiokonttorin HHTPP-raportointi) ja VM:n rahoituslaskelmat.",
                  f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Tarvevakioitu ylitys alueittain">{"".join(g)}</svg>',
                  legend=None, table=f"<thead><tr><th>Alue</th><th>Ylitys, M€/v</th></tr></thead><tbody>{table}</tbody>")

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
        g.append(f'<line class="{"ref" if t==1 else "grid"}" x1="{X(t):.1f}" x2="{X(t):.1f}" y1="{T}" y2="{H-30}"/><text class="tick" x="{X(t):.1f}" y="{H-12}" text-anchor="middle">{fmt(t,2)}</text>')
    g.append(f'<text class="tick" x="{X(1)+4:.1f}" y="{T+8}">Keskitaso</text>')
    for i, a in enumerate(areas):
        y = T + rowh * i + rowh / 2
        a0, a1 = v[(a, "2023")], v[(a, "2025")]
        g.append(f'<text class="tick" x="{L-8}" y="{y+4:.1f}" text-anchor="end">{a}</text>'
                 f'<line class="whisk" x1="{X(a0):.1f}" x2="{X(a1):.1f}" y1="{y:.1f}" y2="{y:.1f}"/>'
                 f'<circle class="yr0f hit" cx="{X(a0):.1f}" cy="{y:.1f}" r="5" data-tip="{a} 2023: {fmt(a0,3)}"/>'
                 f'<circle class="s1f hit" cx="{X(a1):.1f}" cy="{y:.1f}" r="5" data-tip="{a} 2025: {fmt(a1,3)}"/>')
    table = "".join(f'<tr><td>{a}</td><td>{fmt(v[(a,"2023")],3)}</td><td>{fmt(v[(a,"2025")],3)}</td></tr>' for a in areas)
    return figure("Kolme neljästä kalleimmasta kallistui",
                  "Tarvevakioitu kustannusindeksi 2023 ja 2025, 1,00 = Manner-Suomen taso. Keski-Suomi, Kymenlaakso ja Etelä-Savo erkanivat keskitasosta, Keski-Uusimaa lähestyi sitä.",
                  f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Indeksin muutos 2023–2025">{"".join(g)}</svg>',
                  legend=[("yr0", "2023"), ("s1", "2025")],
                  table=f"<thead><tr><th>Alue</th><th>2023</th><th>2025</th></tr></thead><tbody>{table}</tbody>")

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
        cls = "hotf" if r["idx"] >= 1 else "s1f"
        x = L + j*cw + 2; y = T + i*rowh + 1
        g.append(f'<rect class="{cls} hit" x="{x:.1f}" y="{y}" width="{cw-4:.1f}" height="{rowh-2}" rx="3" fill-opacity="{op:.2f}" data-tip="{r["alue"]}, {r["sektori"]}: {fmt(r["idx"],2)}"/>'
                 f'<text class="cell" x="{x + (cw-4)/2:.1f}" y="{y+15}" text-anchor="middle">{fmt(r["idx"],2)}</text>')
    table = "".join("<tr><td>" + a + "</td>" + "".join(f'<td>{fmt(next(r["idx"] for r in rows if r["alue"]==a and r["sektori"]==s_),2)}</td>' for s_ in secs) + "</tr>" for a in areas)
    return figure("Kallein sektori vaihtelee alueittain",
                  "Tarvevakioitu indeksi sektoreittain, 2023–2025 keskiarvo, 1,00 = keskitaso. Mitä voimakkaampi väri, sitä suurempi ero keskitasoon.",
                  f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Sektorikohtainen indeksi alueittain">{"".join(g)}</svg>',
                  legend=[("hot", "Keskitasoa kalliimpi"), ("s1", "Keskitasoa halvempi")],
                  table=f"<thead><tr><th>Alue</th>{''.join(f'<th>{s_}</th>' for s_ in secs)}</tr></thead><tbody>{table}</tbody>")

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
    body = re.sub(r'<figure data-embed="([^"]+)">.*?</figure>',
                  lambda m: CHARTS[m.group(1)]() if m.group(1) in CHARTS else "", body, flags=re.S)
    # taulukot vieritettäviksi
    def _wrap(m):
        t = m.group(0)
        head = re.search(r"<thead>.*?</thead>", t, re.S)
        ncol = head.group(0).count("<th") if head else 0
        cls = "tablewrap wide" if ncol >= 5 else "tablewrap"
        return f'<div class="{cls}">{t}</div>'
    body = re.sub(r"<table>.*?</table>", _wrap, body, flags=re.S)
    # figure-taulukot eivät tarvitse kääremuutosta, siivotaan tuplakääre detailsin sisältä
    body = re.sub(r'(<details><summary>[^<]*</summary>)<div class="tablewrap">(<table>.*?</table>)</div>',
                  r"\1\2", body, flags=re.S)
    # liikennevalot: merkitään solut
    body = body.replace("<td>🔴", '<td class="tl tl-red">🔴').replace("<td>🟢", '<td class="tl tl-green">🟢').replace("<td>🟡", '<td class="tl tl-yellow">🟡')
    # ristiviittaukset välilehtiin
    body = body.replace("välilehti Suositus", '<a href="index.html">välilehti Politiikkasuositus</a>')
    body = re.sub(r"(Alueittainen erittely siitä, mistä ylitys syntyy: )Alue-erittely",
                  r'\1<a href="alue-erittely.html">Alue-erittely</a>', body)
    body = body.replace("Hallituksen linja -välilehden", '<a href="hallituksen-linja.html">Hallituksen linja</a> -välilehden')
    body = re.sub(r'<span data-atom="mention"[^>]*>[^<]*</span>', "Harri Juntunen", body)
    body = re.sub(r'<p><time[^>]*>(\d{4})-(\d{2})-(\d{2})</time> · Harri Juntunen</p>', lambda m: f'<p class="byline">{int(m.group(3))}.{int(m.group(2))}.{m.group(1)} · Harri Juntunen</p>', body)
    body = re.sub(r'<a data-atom="ref" data-ref="file/76c5cc30-4152">', '<a href="liberaali-vaihtoehto.html">', body)
    body = body.replace("välilehdellä Politiikkasuositus", '<a href="index.html">välilehdellä Politiikkasuositus</a>')
    body = body.replace("välilehdellä Hallituksen linja", '<a href="hallituksen-linja.html">välilehdellä Hallituksen linja</a>')
    body = body.replace("(ks. Hallituksen linja, luvut 3–5)", '(ks. <a href="hallituksen-linja.html#3-vaikutukset-palveluihin">Hallituksen linja, luvut 3–5</a>)')
    # ulkoiset linkit uuteen välilehteen
    body = re.sub(r'<a href="(https?://[^"]+)"', r'<a href="\1" target="_blank" rel="noopener"', body)
    return body

def toc(body):
    items = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body)
    if len(items) < 3:
        return ""
    lis = "".join(f'<li><a href="#{i}">{re.sub("<[^>]+>","",t)}</a></li>' for i, t in items)
    return f'<nav class="toc" aria-label="Sisällys"><div class="toc-h">Sisällys</div><ol>{lis}</ol></nav>'

CSS = (pathlib.Path(__file__).parent / "style.css").read_text()
JS = (pathlib.Path(__file__).parent / "tip.js").read_text()

for out, src, label in PAGES:
    body = (SRC / src).read_text()
    body = process(body, src)
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", body)
    ptitle = re.sub("<[^>]+>", "", h1.group(1)) if h1 else label
    cur = ' aria-current="page"'
    nav = "".join(f'<a href="{o}"{cur if o==out else ""}>{l}</a>' for o, _, l in PAGES)
    page = f"""<!doctype html>
<html lang="fi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(ptitle)} · {SITE_TITLE}</title>
<meta name="description" content="Liberaalipuolueen sote-politiikkasuositus: sote-menojen hillintä palveluja heikentämättä.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Raleway:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<header class="site">
  <div class="wrap">
    <a class="brand" href="index.html">{SITE_TITLE}<span>Liberaalipuolueen sote-linja</span></a>
    <nav class="tabs" aria-label="Osiot">{nav}</nav>
  </div>
</header>
<main class="wrap">
{toc(body)}
<article>{body}</article>
</main>
<footer class="site"><div class="wrap">
<p class="credit"><a href="https://github.com/juntunen-ai/budjettihaukka" target="_blank" rel="noopener">BUDJETTIHAUKKA</a> | HARRI JUNTUNEN | LIBERAALIPUOLUE</p>
<p>Luvut ovat arvioita; lähteet on lueteltu kunkin sivun lopussa.</p>
</div></footer>
<div id="tip" role="tooltip" hidden></div>
<script>{JS}</script>
</body>
</html>
"""
    (OUT / out).write_text(page)
    print("wrote", out, len(page))
(OUT / ".nojekyll").write_text("")
