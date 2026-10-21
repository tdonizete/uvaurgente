"""Metodologia UVA URGENTE v2.0 — cálculos e validações.

Toda conta que vira número publicado passa por aqui, para que a nota do
Instagram, a do site e a ficha de auditoria sejam sempre a mesma.
"""
from decimal import Decimal, ROUND_HALF_UP

PESOS = {"visual": 0.10, "aroma": 0.25, "paladar": 0.40, "custo_beneficio": 0.25}

# (preço máximo da faixa, nome, índice, expectativa de entrega V+A+P)
FAIXAS_PRECO = [
    (40, "Popular", 1.0, 6.5),
    (80, "Acessível", 1.3, 7.5),
    (150, "Intermediário", 1.7, 8.0),
    (300, "Premium", 2.2, 8.5),
    (600, "Luxo", 2.8, 9.0),
    (float("inf"), "Ultra-premium", 3.5, 9.5),
]

AJUSTES_CB = {
    "disponibilidade_restrita": -0.5,
    "promocao_frequente": 0.3,
    "pequeno_produtor": 0.2,
    "inflacao_de_preco": -0.3,
}

TETO_BLIC = {0: 6.0, 1: 8.0, 2: 8.8, 3: 9.4, 4: 10.0}

# Perguntas das âncoras (seção 7.2): resposta "não" impõe o teto ao lado.
ANCORAS = [
    ("melhor_que_7", "É claramente melhor que um 7,0 (vinho correto de supermercado)?", 6.9),
    ("supera_cartuxa", "Supera o EA Cartuxa (8,3)?", 8.2),
    ("algo_alem_do_cartuxa", "Tem algo que o Cartuxa não tem (terroir, complexidade, final)?", 8.5),
    ("aproxima_9", "Aproxima-se de um 9,0 (3 pilares BLIC, identidade regional)?", 8.8),
    ("aproxima_95", "Tem algo próximo de um 9,5 (guarda, 4 pilares)?", 9.2),
]

SELOS = [  # (limite superior inclusivo, nome, classe css, fundo, texto)
    (6.0, "Sem Urgência", 1, "#363636", "#D0D0C8"),
    (8.0, "Sem Pressa", 2, "#8A5200", "#FFF8D0"),
    (9.0, "Boa Pedida", 3, "#7A4010", "#FFE8C0"),
    (9.5, "Vale a Pena", 4, "#700810", "#FFD8D8"),
    (10.0, "⚡ Urgente · Compre Agora", 5, "#901808", "#FFD8B8"),
]
FRONTEIRAS = [6.0, 8.0, 9.0, 9.5]

FINAL_FAIXAS = [  # segundos mínimos, nota mínima, nota máxima, rótulo
    (12, 9.0, 10.0, "Muito longo"),
    (8, 7.5, 8.9, "Longo"),
    (5, 6.0, 7.4, "Médio"),
    (3, 4.0, 5.9, "Curto"),
    (0, 0.0, 3.9, "Muito curto"),
]


def r1(x):
    """Arredonda para 1 casa, meio para cima (8,25 → 8,3)."""
    return float(Decimal(str(x)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


def clamp(x, lo=0.0, hi=10.0):
    return max(lo, min(hi, x))


def faixa_preco(preco):
    for teto, nome, indice, expectativa in FAIXAS_PRECO:
        if preco <= teto:
            return {"nome": nome, "indice": indice, "expectativa": expectativa}
    raise ValueError(preco)


def nota_aroma(a):
    return r1(a["limpeza"] * 0.30 + a["intensidade"] * 0.30 + a["complexidade"] * 0.40)


def nota_paladar(p):
    attrs = [p["acidez"], p["corpo"], p["tanino_docura"], p["intensidade"], p["final"]]
    ajuste = clamp(p.get("ajuste_equilibrio", 0.0), -0.5, 0.5)
    return r1(clamp(sum(attrs) / 5 + ajuste)), attrs


def nota_cb(entrega, preco_ref, ajustes):
    """C/B = 7,0 + 1,8 × (entrega − expectativa da faixa) + ajustes, limitado a 0–10.

    Entregar exatamente o esperado para a faixa de preço vale 7,0 (correto).
    O fator 1,8 reproduz o exemplo oficial da metodologia: Casal Garcia,
    R$ 55 (Acessível, expectativa 7,5), entrega 8,6 → C/B 9,0.
    """
    f = faixa_preco(preco_ref)
    soma_aj = sum(AJUSTES_CB[k] for k in ajustes)
    soma_aj = clamp(soma_aj, -0.5, 0.5)
    bruto = 7.0 + 1.8 * (entrega - f["expectativa"]) + soma_aj
    return r1(clamp(bruto)), f, soma_aj


def blic(aroma, paladar_attrs, paladar_nota):
    acidez, corpo, tan, intens_g, final = paladar_attrs
    desvio = max(paladar_attrs) - min(paladar_attrs)
    pilares = {
        "B": desvio < 2.0 and paladar_nota >= 7.5,
        "L": aroma.get("_final_segundos", 0) >= 8,
        "I": (aroma["intensidade"] + intens_g) / 2 >= 7.5,
        "C": len(aroma["familias"]) >= 3 and aroma["complexidade"] >= 7.5,
    }
    return pilares


def arredondar_conservador(x):
    """Regra 8.2: 8,05 publica 8,0. Valores que só passam a fronteira pelo
    arredondamento ficam na faixa de baixo."""
    r = r1(x)
    for b in FRONTEIRAS:
        if x < b + 0.1 - 1e-9 and r1(b + 0.1) == r:
            return b
    return r


def selo(nota):
    for lim, nome, n, bg, ink in SELOS:
        if nota <= lim + 1e-9:
            return {"nome": nome, "n": n, "bg": bg, "ink": ink}
    return {"nome": SELOS[-1][1], "n": 5, "bg": SELOS[-1][3], "ink": SELOS[-1][4]}


def avaliar(d):
    """Recebe o dicionário da avaliação e devolve todos os números + alertas."""
    alertas = []
    v = d["visual"]["nota"]
    a = dict(d["aroma"])
    p = d["paladar"]
    a["_final_segundos"] = p["final_segundos"]

    # Coerências da metodologia
    nf = len(a["familias"])
    if nf <= 1 and a["complexidade"] > 7.0:
        alertas.append("Complexidade > 7,0 com 1 família aromática (máx. 7,0).")
    if 2 <= nf <= 3 and not 7.1 <= a["complexidade"] <= 8.5:
        alertas.append("Com 2–3 famílias a complexidade deve ficar entre 7,1 e 8,5.")
    if nf >= 4 and a["complexidade"] < 8.6:
        alertas.append("Com 4+ famílias a complexidade deve ficar entre 8,6 e 10.")
    if a.get("defeito_irreversivel") and a["limpeza"] > 4.0:
        alertas.append("Defeito irreversível exige Limpeza ≤ 4,0.")
    for seg, lo, hi, rot in FINAL_FAIXAS:
        if p["final_segundos"] >= seg:
            if not lo <= p["final"] <= hi:
                alertas.append(f"Final de {p['final_segundos']} s ({rot}) pede nota {lo}–{hi}; recebeu {p['final']}.")
            break

    aroma = nota_aroma(a)
    paladar, attrs = nota_paladar(p)
    entrega = r1((v + aroma + paladar) / 3)
    preco = d["preco"]
    cb, faixa, aj = nota_cb(entrega, preco["referencia"], preco.get("ajustes", []))
    if len(preco.get("fontes", [])) < 2:
        alertas.append("Preço pesquisado em menos de 2 fontes (exigência 11.1).")

    criterios = {"visual": r1(v), "aroma": aroma, "paladar": paladar, "custo_beneficio": cb}
    matematica = sum(criterios[k] * PESOS[k] for k in PESOS)

    pilares = blic(a, attrs, paladar)
    n_pil = sum(pilares.values())
    teto_blic = TETO_BLIC[n_pil]
    apos_blic = min(matematica, teto_blic)

    tetos_ancora = []
    respostas = d.get("ancoras", {})
    for chave, pergunta, teto in ANCORAS:
        resp = respostas.get(chave)
        if resp is None:
            alertas.append(f"Âncora sem resposta: {pergunta}")
            continue
        tetos_ancora.append((pergunta, resp, teto))
        if not resp:
            break  # a cascata para na primeira resposta "não"
    teto_anc = min([t for _, r, t in tetos_ancora if not r] or [10.0])
    final = arredondar_conservador(min(apos_blic, teto_anc))
    s = selo(final)

    return {
        "criterios": criterios,
        "entrega_vap": entrega,
        "faixa_preco": faixa,
        "ajuste_cb": aj,
        "nota_matematica": round(matematica, 3),
        "pilares": pilares,
        "n_pilares": n_pil,
        "teto_blic": teto_blic,
        "ancoras": tetos_ancora,
        "teto_ancoras": teto_anc,
        "nota": final,
        "selo": s,
        "paladar_attrs": attrs,
        "alertas": alertas,
    }


def virgula(x):
    return f"{x:.1f}".replace(".", ",")


if __name__ == "__main__":
    # Autoteste com o exemplo oficial (Casal Garcia, seção 5.2)
    cb, f, _ = nota_cb(8.6, 55, [])
    assert f["nome"] == "Acessível" and cb == 9.0, cb
    assert arredondar_conservador(8.05) == 8.0
    assert arredondar_conservador(8.04) == 8.0
    assert arredondar_conservador(8.15) == 8.2
    assert arredondar_conservador(9.06) == 9.0
    assert arredondar_conservador(9.49) == 9.5
    assert selo(8.0)["nome"] == "Sem Pressa" and selo(8.1)["nome"] == "Boa Pedida"
    assert selo(9.5)["nome"] == "Vale a Pena" and selo(9.6)["n"] == 5
    print("metodologia: autoteste ok")
