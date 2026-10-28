"""Pontua as fichas da base (top 100 Amazon) sem publicar nada.

Uso, na raiz do repositório:
    python3 _automacao/pontuar_base.py

Lê _automacao/base/vinhos/*.json, calcula a nota com metodologia.avaliar
e grava _automacao/base/resultado.md (tabela) e o status de cada item em
_automacao/base/top100-amazon.json. Não gera páginas, slides nem legendas.

Para publicar um vinho da base (quando o Tiago mandar foto, link e ok):
1. copie a ficha para _automacao/avaliacoes/<slug>.json;
2. preencha "textos", "lojas", "hashtags", "safra" e "imagem_origem";
3. rode python3 _automacao/gerar.py _automacao/avaliacoes/<slug>.json.
"""
import glob
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import metodologia as m  # noqa: E402

BASE = os.path.join(AQUI, "base")


def virgula(x):
    return f"{x:.1f}".replace(".", ",")


def preco_br(x):
    return f"{x:.2f}".replace(".", ",")


def main():
    linhas, por_rank = [], {}
    for f in sorted(glob.glob(os.path.join(BASE, "vinhos", "*.json"))):
        d = json.load(open(f))
        r = m.avaliar(d)
        c = r["criterios"]
        alertas = [a for a in r["alertas"] if "menos de 2 fontes" not in a]
        pend = list(d.get("pendencias", []))
        if len(d["preco"]["fontes"]) < 2 and not any("1 só fonte" in p for p in pend):
            pend.append("Preço em 1 só fonte")
        pil = "".join(k for k, v in r["pilares"].items() if v) or "—"
        rk = d["rank_amazon"] if d.get("rank_amazon") else 1000 + d["pos_lista300"] if d.get("pos_lista300") else 3000
        linhas.append((rk, d, r, c, pil, alertas, pend))
        por_rank[d.get("rank_amazon")] = (d["slug"], r["nota"], r["selo"]["nome"])

    linhas.sort(key=lambda x: x[0])
    out = ["# Base top 100 Amazon — notas (não publicadas)", "",
           "Gerado por `_automacao/pontuar_base.py`. Nenhum destes vinhos está no site.", "Coluna #: número = posição no top 100 Amazon; L + número = posição na lista popular 300; W = divulgado no grupo de WhatsApp Sommelier de Promo (27-28/10/2026).", "",
           "| # | Vinho | País | Tipo | Preço ref. | V | A | P | C/B | BLIC | Nota | Selo | Confiança | Pendências |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for rank, d, r, c, pil, alertas, pend in linhas:
        v = d["vinho"]
        out.append(
            f"| {rank if rank < 1000 else 'W' if rank >= 3000 else 'L' + str(rank - 1000)} | {v['title'] if v['title'].startswith(v['produtor'].split()[0]) else v['produtor'] + ' ' + v['title']} | {v['pais']} | {v['tipo']} | "
            f"R$ {preco_br(d['preco']['referencia'])} | "
            f"{virgula(c['visual'])} | {virgula(c['aroma'])} | {virgula(c['paladar'])} | {virgula(c['custo_beneficio'])} | "
            f"{pil} | **{virgula(r['nota'])}** | {r['selo']['nome']} | {d.get('confianca', '')} | "
            f"{'; '.join(pend + alertas) or '—'} |")
    top = json.load(open(os.path.join(BASE, "top100-amazon.json")))
    sem = [it for it in top["itens"] if it["status"] == "sem_ficha"]
    if sem:
        out += ["", "## Sem ficha (fora da pontuação)", "", "| # | Vinho | Motivo |", "| --- | --- | --- |"]
        out += [f"| {it['rank']} | {it['nome'][:70]} | {it.get('motivo', '')} |" for it in sem]
    open(os.path.join(BASE, "resultado.md"), "w").write("\n".join(out) + "\n")

    for it in top["itens"]:
        if it["rank"] in por_rank and it["status"] == "a_avaliar" or it.get("status") == "avaliado_base":
            if it["rank"] in por_rank:
                slug, nota, selo = por_rank[it["rank"]]
                it.update(status="avaliado_base", slug=slug, nota=nota, selo=selo)
    json.dump(top, open(os.path.join(BASE, "top100-amazon.json"), "w"), ensure_ascii=False, indent=2)

    for rank, d, r, c, pil, alertas, pend in linhas:
        flag = " ⚠ " + "; ".join(alertas) if alertas else ""
        print(f"{(rank if rank < 1000 else 'W' if rank >= 3000 else 'L' + str(rank - 1000))!s:>4} {d['slug'][:44]:44} {virgula(r['nota'])} {r['selo']['nome']:<12} BLIC {pil}{flag}")


if __name__ == "__main__":
    main()
