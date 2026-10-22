"""Gera tudo de uma avaliação: página do site, carrossel do Instagram, legenda e ficha.

Uso (na raiz do repositório):
    python3 _automacao/gerar.py _automacao/avaliacoes/<slug>.json

Saídas:
    _vereditos/<slug>.md                       página do vinho no site
    assets/img/vereditos/<slug>.png            foto da garrafa (se informada)
    _automacao/saida/<slug>/slide-1..6.png     carrossel 1080×1350
    _automacao/saida/<slug>/legenda.txt        legenda + hashtags
    _automacao/saida/<slug>/ficha.md           ficha de auditoria da nota
"""
import json
import os
import shutil
import sys
from datetime import date

import jinja2
import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from metodologia import avaliar, faixa_preco, virgula  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)

FONTE_TXT = {
    False: "calculada a partir de ficha técnica, críticas publicadas e preço de mercado",
    True: "calculada a partir de ficha técnica, críticas publicadas e preço de mercado, e validada na prova do @uvaurgente",
}

NIVEL_PCT = {"fraco": 40, "moderado": 62, "pronunciado": 78, "intenso": 92}
NOMES_PALADAR = ["Acidez", "Corpo", "Tanino", "Intensidade", "Final"]


def preco_txt(p):
    lo, hi = p["min"], p["max"]
    return f"R$ {lo}" if lo == hi else f"R$ {lo}–{hi}"


def front_matter(d, r, ctx):
    v = d["vinho"]
    t = d["textos"]
    fm = {
        "title": v["title"],
        "date": date.fromisoformat(d.get("data", date.today().isoformat())),
        "tipo": v["tipo"],
        "pais": v["pais"],
        "regiao": v["regiao"],
        "safra": v.get("safra"),
        "uvas": v["uvas"],
        "nota": r["nota"],
        "preco_min": d["preco"]["min"],
        "preco_max": d["preco"]["max"],
        "frase": d["textos"]["frase"],
        "degustacao": d["textos"]["degustacao"],
        "harmonizacao": [{"prato": h["prato"], "porque": h["porque"], "tag": h["tag"]} for h in t["harmonizacao"]],
        "provado": bool(d.get("provado")),
        "produtor": v.get("produtor"),
        "kicker_identidade": t.get("kicker_identidade"),
        "historico": t.get("historico"),
        "canal": d.get("canal"),
        "aromas": [{"nome": a["nome"], "pct": a["pct"]} for a in ctx["aromas"]],
        "paladar": [{"nome": x["nome"], "nota": x["valor"], "sub": x["sub"]} for x in ctx["paladar"]],
        "blic": r["n_pilares"],
        "servir": v.get("servir"),
        "teor": v.get("teor"),
        "imagem": f"/assets/img/vereditos/{d['slug']}.png" if d.get("imagem_origem") else None,
        "preco_checado": date.fromisoformat(d.get("data", date.today().isoformat())),
        "lojas": [{"nome": l["nome"], "url": l["url"], "preco": l.get("preco")} for l in d.get("lojas", [])],
        "criterios": r["criterios"],
    }
    fm = {k: val for k, val in fm.items() if val not in (None, "")}
    if not fm.get("provado"):
        fm.pop("provado", None)
    if "lojas" not in fm or not fm["lojas"]:
        fm["lojas"] = []
    corpo = yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000)
    texto = d["textos"].get("texto_site", "").strip()
    return f"---\n{corpo}---\n" + (f"\n{texto}\n" if texto else "")


def legenda(d, r):
    v, t = d["vinho"], d["textos"]
    hs = " ".join(d.get("hashtags", [])) or "#vinho #vinhos #uvaurgente #vinhosemmimimi #dicadevinho"
    pratos = ", ".join(h["prato"].lower() for h in t["harmonizacao"][:3])
    linhas = [
        f"{v['title']}: {virgula(r['nota'])}/10 · {r['selo']['nome']}.",
        "",
        t["frase"],
        "",
        t["degustacao"],
        "",
        f"🍽 Vai bem com {pratos}.",
        f"🌡 Servir a {v.get('servir', '')}.",
        f"💰 {preco_txt(d['preco'])}. Link de compra na bio.",
        "",
        ("✅ PROVADO. " if d.get("provado") else "") + f"Nota pela Metodologia UVA URGENTE v2.0, {FONTE_TXT[bool(d.get('provado'))]}. Método completo no site.",
        "",
        "E você, já experimentou? Comenta COMPRO ou PASSO.",
        "",
        hs,
    ]
    return "\n".join(linhas)


def ficha(d, r):
    v = d["vinho"]
    pil = ", ".join(f"{k} {'✓' if ok else '✗'}" for k, ok in r["pilares"].items())
    linhas = [
        f"# Ficha de avaliação — {v['title']}",
        "",
        f"- Nota publicada: **{virgula(r['nota'])}** ({r['selo']['nome']}){' · PROVADO' if d.get('provado') else ''}",
        f"- Nota matemática: {r['nota_matematica']:.2f}",
        f"- Critérios: Visual {virgula(r['criterios']['visual'])} · Aroma {virgula(r['criterios']['aroma'])} · Paladar {virgula(r['criterios']['paladar'])} · C/B {virgula(r['criterios']['custo_beneficio'])}",
        f"- Entrega V+A+P: {virgula(r['entrega_vap'])} · Faixa de preço: {r['faixa_preco']['nome']} (expectativa {virgula(r['faixa_preco']['expectativa'])}) · ajustes C/B {r['ajuste_cb']:+.1f}",
        f"- BLIC: {pil} → {r['n_pilares']} pilares, teto {virgula(r['teto_blic'])}",
        f"- Âncoras: " + "; ".join(f"{q} {'sim' if a else 'NÃO'}" for q, a, _ in r["ancoras"]) + f" → teto {virgula(r['teto_ancoras'])}",
        "",
        "## Fontes consultadas",
        *[f"- {u}" for u in d.get("fontes", [])],
        "",
        "## Preço",
        *[f"- {u}" for u in d["preco"].get("fontes", [])],
        "",
        "## Alertas",
        *([f"- {a}" for a in r["alertas"]] or ["- nenhum"]),
    ]
    return "\n".join(linhas)


def contexto_slides(d, r, pasta_saida):
    v, t, p = d["vinho"], d["textos"], d["paladar"]
    tipo = v["tipo"].lower()
    nomes_pal = list(NOMES_PALADAR)
    if tipo not in ("tinto",):
        nomes_pal[2] = "Doçura"
    pal = []
    for nome, nota, sub in zip(nomes_pal, r["paladar_attrs"], p["descritores"]):
        pal.append({"nome": nome, "nota": virgula(nota), "valor": nota, "pct": round(nota * 10), "sub": sub})
    aromas = [{"nome": a["nome"], "pct": a.get("pct") or NIVEL_PCT[a["nivel"]]} for a in d["aroma"]["top5"]]
    crit = [
        {"nome": "Visual", "peso": "10%", "nota": virgula(r["criterios"]["visual"]), "pct": r["criterios"]["visual"] * 10},
        {"nome": "Aroma", "peso": "25%", "nota": virgula(r["criterios"]["aroma"]), "pct": r["criterios"]["aroma"] * 10},
        {"nome": "Paladar", "peso": "40%", "nota": virgula(r["criterios"]["paladar"]), "pct": r["criterios"]["paladar"] * 10},
        {"nome": "Custo-benefício", "peso": "25%", "nota": virgula(r["criterios"]["custo_beneficio"]), "pct": r["criterios"]["custo_beneficio"] * 10},
    ]
    from metodologia import SELOS
    faixas = [{"bg": bg, "ativa": n == r["selo"]["n"]} for _, _, n, bg, _ in SELOS]
    pt = preco_txt(d["preco"])
    safra = str(v["safra"]) if v.get("safra") else "Não informada"
    teor = f"{v['teor']}".replace(".", ",") + "%" if v.get("teor") else "—"
    ficha_tec = [
        ("Uvas", v["uvas"]),
        ("Origem", f"{v['regiao']}, {v['pais']}"),
        ("Safra", safra),
        ("Teor", f"{teor} vol."),
        ("Preço", pt),
        ("Produtor", v["produtor"]),
    ]
    acidez_nivel = p["descritores"][0].split(" — ")[0]
    specs = [
        ("Servir", v.get("servir", "—")),
        ("Preço", pt),
        ("Teor", teor),
        ("Acidez", acidez_nivel),
        ("Onde achar", d.get("canal", "Supermercado")),
        ("Safra", safra if v.get("safra") else "—"),
    ]
    img = None
    if d.get("imagem_origem"):
        img = "file://" + os.path.abspath(d["imagem_origem"])
    lojas = d.get("lojas", [])
    return {
        "fontes": "file://" + os.path.join(AQUI, "fontes"),
        "v": v, "t": t, "s": {"selo": r["selo"], "n_pilares": r["n_pilares"]},
        "nota": virgula(r["nota"]), "preco_txt": pt, "imagem": img,
        "ficha": ficha_tec, "aromas": aromas, "paladar": pal, "criterios": crit,
        "faixas": faixas, "marcador": round(r["nota"] * 10, 1), "specs": specs,
        "loja_principal": lojas[0]["nome"] if lojas else "",
        "provado": bool(d.get("provado")),
        "fonte_txt": FONTE_TXT[bool(d.get("provado"))],
    }


def render_slides(html_path, pasta):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350})
        pg.goto("file://" + html_path)
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(400)
        problemas = pg.evaluate("""() => [...document.querySelectorAll('.slide')].flatMap(s => {
            const r = s.getBoundingClientRect(); const out = [];
            s.querySelectorAll('*').forEach(e => { const b = e.getBoundingClientRect();
              if (b.width && (b.right > r.right + 1 || b.bottom > r.bottom + 1)) out.push(s.id + ': ' + (e.textContent||'').trim().slice(0,40)); });
            return out; })""")
        for i in range(1, 7):
            pg.locator(f"#s{i}").screenshot(path=os.path.join(pasta, f"slide-{i}.png"))
        b.close()
    return problemas


def main(caminho):
    with open(caminho, encoding="utf-8") as f:
        d = json.load(f)
    r = avaliar({"visual": d["visual"], "aroma": d["aroma"], "paladar": d["paladar"],
                 "preco": d["preco"], "ancoras": d.get("ancoras", {})})
    slug = d["slug"]
    saida = os.path.join(AQUI, "saida", slug)
    os.makedirs(saida, exist_ok=True)

    ctx = contexto_slides(d, r, saida)

    # Site
    with open(os.path.join(RAIZ, "_vereditos", f"{slug}.md"), "w", encoding="utf-8") as f:
        f.write(front_matter(d, r, ctx))
    if d.get("imagem_origem"):
        destino = os.path.join(RAIZ, "assets", "img", "vereditos", f"{slug}.png")
        if os.path.abspath(d["imagem_origem"]) != os.path.abspath(destino):
            shutil.copy(d["imagem_origem"], destino)

    # Instagram
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(AQUI, "modelos")), autoescape=True)
    html = env.get_template("carrossel.html").render(**ctx)
    html_path = os.path.join(saida, "carrossel.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    problemas = render_slides(html_path, saida)
    with open(os.path.join(saida, "legenda.txt"), "w", encoding="utf-8") as f:
        f.write(legenda(d, r))
    with open(os.path.join(saida, "ficha.md"), "w", encoding="utf-8") as f:
        f.write(ficha(d, r))

    print(f"Nota {virgula(r['nota'])} · {r['selo']['nome']} · BLIC {r['n_pilares']}/4")
    print("Critérios:", {k: virgula(x) for k, x in r["criterios"].items()})
    for a in r["alertas"]:
        print("ALERTA:", a)
    for p in problemas:
        print("TEXTO ESTOURANDO O SLIDE:", p)
    print("Saída:", saida)
    return 1 if (r["alertas"] or problemas) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
