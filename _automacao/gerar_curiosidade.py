"""Gera o carrossel de curiosidade (5 slides 1080×1350) e a legenda.

Uso: python3 _automacao/gerar_curiosidade.py _automacao/curiosidades/<arquivo>.json
Saída: _automacao/saida/curiosidades/<slug>/slide-1..5.png/.jpg e legenda.txt
"""
import json, os, sys
import jinja2, yaml
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
from metodologia import selo, virgula  # noqa: E402


def vinho(slug, mostrar):
    t = open(os.path.join(RAIZ, "_vereditos", slug + ".md"), encoding="utf-8").read()
    fm = yaml.safe_load(t.split("---")[1])
    s = selo(float(fm["nota"]))
    partes = [fm.get("produtor")]
    if mostrar == "safra":
        partes.append(f"Safra {fm['safra']}" if fm.get("safra") else "Sem safra no rótulo")
    elif mostrar == "servir" and fm.get("servir"):
        partes.append(f"Servir a {fm['servir']}")
    elif fm.get("safra"):
        partes.append(str(fm["safra"]))
    img = os.path.join(RAIZ, "assets", "img", "vereditos", slug + ".png")
    return {"title": fm["title"], "linha": " · ".join(p for p in partes if p), "nota": virgula(float(fm["nota"])),
            "selo": s["nome"], "bg": s["bg"], "fg": s["ink"], "img": ("file://" + img) if os.path.exists(img) else None}


def main(caminho):
    d = json.load(open(caminho, encoding="utf-8"))
    out = os.path.join(AQUI, "saida", "curiosidades", f"{d['n']:02d}-{d['slug']}")
    os.makedirs(out, exist_ok=True)
    ctx = dict(d, fontes="file://" + os.path.join(AQUI, "fontes"),
               vinhos=[vinho(s, d.get("mostrar")) for s in d.get("vinhos", [])])
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(AQUI, "modelos")), autoescape=True)
    hp = os.path.join(out, "carrossel.html")
    open(hp, "w", encoding="utf-8").write(env.get_template("curiosidade.html").render(**ctx))
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1350})
        pg.goto("file://" + hp); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
        est = pg.evaluate("""() => [...document.querySelectorAll('.slide')].flatMap(s => { const r = s.getBoundingClientRect();
            const rod = s.querySelector('.rod').getBoundingClientRect();
            return [...s.querySelectorAll('h1,h2,p,.tab,.stat,.vin')].filter(e => !e.closest('.rod') && !e.closest('[style*="margin-top:auto"]') && e.getBoundingClientRect().bottom > rod.top - 4)
              .map(e => s.id + ': ' + (e.textContent || '').trim().slice(0, 40)).concat(rod.bottom > r.bottom + 1 ? [s.id + ': rodapé fora do slide'] : []); })""")
        for i in range(1, 6):
            p = os.path.join(out, f"slide-{i}.png"); pg.locator(f"#s{i}").screenshot(path=p)
            Image.open(p).convert("RGB").save(p[:-4] + ".jpg", quality=92)
        b.close()
    leg = d["legenda"].strip() + "\n\n" + " ".join(d.get("hashtags", []))
    if d.get("fontes_ref"):
        leg += "\n\nFontes: " + "; ".join(d["fontes_ref"])
    open(os.path.join(out, "legenda.txt"), "w", encoding="utf-8").write(leg + "\n")
    print(f"#{d['n']:02d} {d['capa']} → {out}")
    for e in est:
        print("TEXTO ESTOURANDO:", e)
    return 1 if est else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
