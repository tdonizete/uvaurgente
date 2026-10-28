"""Atualiza o preço médio dos produtos de "Além do Vinho" e regenera as páginas.

Uso (na raiz do repositório):
    python3 _automacao/atualizar_precos_alem.py precos.json [AAAA-MM-DD]

precos.json: {"<slug>": [["Amazon", 49.63], ["Mercado Livre", 39.99], ...], ...}
Regras: só lojas brasileiras; a Amazon entra com o preço da página do produto (link do Tiago).
Um produto ausente do arquivo, ou com lista vazia, mantém o preço anterior.
Grava o histórico em _automacao/alem/_historico-precos.csv e imprime as variações.
"""
import csv, json, os, subprocess, sys
from datetime import date

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
PASTA = os.path.join(AQUI, "alem")
HIST = os.path.join(PASTA, "_historico-precos.csv")
ALERTA = 0.30  # variação acima de 30% é sinalizada para conferência


def br(v):
    return f"R$ {v:.2f}".replace(".", ",")


def main(arq, dia):
    novos = json.load(open(arq, encoding="utf-8"))
    linhas, avisos = [], []
    novo_hist = not os.path.exists(HIST)
    with open(HIST, "a", newline="", encoding="utf-8") as h:
        w = csv.writer(h, delimiter=";")
        if novo_hist:
            w.writerow(["data", "slug", "loja", "preco"])
        for s, fontes in sorted(novos.items()):
            p = os.path.join(PASTA, f"{s}.json")
            if not os.path.exists(p) or not fontes:
                continue
            d = json.load(open(p, encoding="utf-8"))
            ant = d.get("preco_medio")
            media = round(sum(v for _, v in fontes) / len(fontes), 2)
            d["preco_medio"], d["preco_data"] = media, dia
            d["preco_fontes"] = [f"{n}: {br(v)}" for n, v in fontes]
            json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            for n, v in fontes:
                w.writerow([dia, s, n, f"{v:.2f}"])
            r = subprocess.run(["python3", os.path.join(AQUI, "gerar_extra.py"), p], capture_output=True, text=True, cwd=RAIZ)
            if r.returncode:
                avisos.append(f"ERRO ao gerar {s}: {r.stderr[-200:]}")
            var = (media - ant) / ant if ant else 0
            linhas.append(f"{s}: {br(ant) if ant else '—'} -> {br(media)} ({var:+.0%}, {len(fontes)} lojas)")
            if ant and abs(var) > ALERTA:
                avisos.append(f"Conferir {s}: variação de {var:+.0%}")
            if len(fontes) > 1 and max(v for _, v in fontes) > 1.6 * min(v for _, v in fontes):
                avisos.append(f"Conferir {s}: diferença grande entre lojas ({', '.join(f'{n} {br(v)}' for n, v in fontes)})")
    print("\n".join(linhas))
    if avisos:
        print("\nATENÇÃO\n" + "\n".join(avisos))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else date.today().isoformat())
