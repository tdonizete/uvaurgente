"""Gera as peças de "Notícias" e "Além do Vinho": página do site + arte do Story.

Uso (na raiz do repositório):
    python3 _automacao/gerar_extra.py _automacao/noticias/<slug>.json
    python3 _automacao/gerar_extra.py _automacao/alem/<slug>.json

Saídas:
    Notícia: _noticias/<slug>.md, assets/img/noticias/<slug>.png (1200×630),
             _automacao/saida/noticias/<slug>/story.png (1080×1920), linkedin.png (1200×1500),
             linkedin.txt (texto do post) e link.txt
    Produto: _alem/<slug>.md, assets/img/alem/<slug>.png (foto, se houver),
             _automacao/saida/alem/<slug>/story.png e link.txt
"""
import json
import os
import shutil
import sys
from datetime import date

import jinja2
import yaml

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
SITE = "https://uvaurgente.com.br"
CATEGORIAS_NOTICIA = ["Mercado", "Brasil", "Mundo", "Safra e clima", "Preço e impostos", "Eventos", "Ciência e saúde", "Rótulos e lançamentos"]
CATEGORIAS_PRODUTO = ["Livros", "Taças", "Saca-rolhas e abridores", "Decanters e aeradores", "Conservação", "Kits e presentes"]
LIMITES = {"titulo": 100, "resumo": 420, "porque_importa": 320, "linha_story": 140, "frase": 120}


def checar(d, tipo):
    al = []
    cats = CATEGORIAS_NOTICIA if tipo == "noticia" else CATEGORIAS_PRODUTO
    if d.get("categoria") not in cats:
        al.append(f"Categoria '{d.get('categoria')}' fora da lista: {', '.join(cats)}")
    for k, lim in LIMITES.items():
        if d.get(k) and len(d[k]) > lim:
            al.append(f"{k} com {len(d[k])} caracteres (máx. {lim})")
    if tipo == "noticia" and not (d.get("fonte") or {}).get("url"):
        al.append("Notícia sem link da fonte.")
    if tipo == "produto" and not d.get("lojas"):
        al.append("Produto sem link de loja.")
    return al


def escrever_md(pasta, slug, fm, corpo):
    fm = {k: v for k, v in fm.items() if v not in (None, "", [], {})}
    txt = "---\n" + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000) + "---\n"
    if corpo:
        txt += "\n" + corpo.strip() + "\n"
    with open(os.path.join(RAIZ, pasta, f"{slug}.md"), "w", encoding="utf-8") as f:
        f.write(txt)


def render(ctx, saida, og_destino=None):
    from playwright.sync_api import sync_playwright
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(AQUI, "modelos")), autoescape=True)
    html = env.get_template("extras.html").render(fontes="file://" + os.path.join(AQUI, "fontes"), **ctx)
    hp = os.path.join(saida, "peca.html")
    with open(hp, "w", encoding="utf-8") as f:
        f.write(html)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": 1200, "height": 1920})
        pg.goto("file://" + hp)
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(300)
        estouro = pg.evaluate("""() => [...document.querySelectorAll('.peca')].flatMap(s => { const r = s.getBoundingClientRect();
            return [...s.querySelectorAll('*')].filter(e => { const b = e.getBoundingClientRect(); return b.width && (b.bottom > r.bottom + 1 || b.right > r.right + 1); })
            .map(e => s.id + ': ' + (e.textContent || '').trim().slice(0, 40)); })""")
        pg.locator("#story").screenshot(path=os.path.join(saida, "story.png"))
        if og_destino:
            pg.locator("#og").screenshot(path=og_destino)
        if pg.locator("#linkedin").count():
            pg.locator("#linkedin").screenshot(path=os.path.join(saida, "linkedin.png"))
        b.close()
    return estouro


def main(caminho):
    d = json.load(open(caminho, encoding="utf-8"))
    tipo = "noticia" if "fonte" in d else "produto"
    slug = d["slug"]
    dia = date.fromisoformat(d.get("data", date.today().isoformat()))
    alertas = checar(d, tipo)
    saida = os.path.join(AQUI, "saida", "noticias" if tipo == "noticia" else "alem", slug)
    os.makedirs(saida, exist_ok=True)

    if tipo == "noticia":
        url = f"/noticias/{slug}/"
        og = os.path.join(RAIZ, "assets", "img", "noticias", f"{slug}.png")
        fonte = dict(d["fonte"])
        if fonte.get("data"):
            fonte["data"] = date.fromisoformat(fonte["data"])
        escrever_md("_noticias", slug, {
            "title": d["titulo"], "date": dia, "categoria": d["categoria"], "resumo": d["resumo"],
            "porque_importa": d.get("porque_importa"), "fonte": fonte, "outras_fontes": d.get("outras_fontes"),
            "vereditos": d.get("vereditos"), "image": f"/assets/img/noticias/{slug}.png",
            "description": d["resumo"][:155],
        }, "\n\n".join(d.get("texto", [])))
        estouro = render({"tipo": "noticia", "titulo": d["titulo"], "categoria": d["categoria"],
                          "linha": d.get("linha_story"), "fonte": d["fonte"]["nome"],
                          "numeros": d.get("numeros", [])[:3]}, saida, og)
        li = d.get("linkedin") or {}
        if li.get("texto"):
            tags = " ".join(li.get("hashtags", ["#vinho", "#mercadodevinho", "#uvaurgente"]))
            with open(os.path.join(saida, "linkedin.txt"), "w", encoding="utf-8") as f:
                f.write("POST (cole com a imagem linkedin.png)\n\n" + li["texto"].strip() + "\n\n" + tags + "\n\n"
                        + "PRIMEIRO COMENTÁRIO (publique logo depois do post)\n\n"
                        + "Notícia completa, com a fonte original: " + SITE + url + "\n")
            if len(li["texto"]) > 2800:
                alertas.append(f"Texto do LinkedIn com {len(li['texto'])} caracteres (máx. recomendado 2800)")
    else:
        url = f"/alem-do-vinho/{slug}/"
        img = None
        if d.get("imagem_origem"):
            img = os.path.join(RAIZ, "assets", "img", "alem", f"{slug}.png")
            if os.path.abspath(d["imagem_origem"]) != os.path.abspath(img):
                shutil.copy(d["imagem_origem"], img)
        escrever_md("_alem", slug, {
            "title": d["titulo"], "date": dia, "categoria": d["categoria"], "marca": d.get("marca"),
            "frase": d.get("frase"), "aprovado": bool(d.get("aprovado")) or None, "destaques": d.get("destaques"),
            "imagem": f"/assets/img/alem/{slug}.png" if img else None, "image": f"/assets/img/alem/{slug}.png" if img else None,
            "lojas": [{"nome": l["nome"], "url": l["url"]} for l in d["lojas"]], "vereditos": d.get("vereditos"),
            "description": d.get("frase"),
        }, "\n\n".join(d.get("texto", [])))
        estouro = render({"tipo": "produto", "titulo": d["titulo"], "categoria": d["categoria"], "frase": d.get("frase"),
                          "aprovado": d.get("aprovado"), "imagem": ("file://" + img) if img else None}, saida)

    with open(os.path.join(saida, "link.txt"), "w", encoding="utf-8") as f:
        f.write(SITE + url + "\n")
    print(("Notícia" if tipo == "noticia" else "Produto") + f": {d['titulo']}")
    print("Link para o sticker:", SITE + url)
    for a in alertas:
        print("ALERTA:", a)
    for e in estouro:
        print("TEXTO ESTOURANDO A ARTE:", e)
    print("Saída:", saida)
    return 1 if (alertas or estouro) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
