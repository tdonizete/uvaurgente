# Automação de vereditos — UVA URGENTE

Esta pasta não aparece no site (o Jekyll ignora pastas que começam com `_`).
Ela guarda o gerador que transforma uma avaliação em página do site,
carrossel do Instagram, legenda e ficha de auditoria.

| Arquivo | Função |
| --- | --- |
| `metodologia.py` | Cálculos da Metodologia v2.0: aroma, paladar, custo-benefício, BLIC, âncoras, arredondamento conservador, selo. `python3 metodologia.py` roda o autoteste. |
| `gerar.py` | Lê `avaliacoes/<slug>.json` e gera `_vereditos/<slug>.md`, `saida/<slug>/slide-1..6.png`, `legenda.txt` e `ficha.md`. |
| `modelos/carrossel.html` | Os 6 slides (1080×1350) na identidade da marca. |
| `fontes/` | Archivo Black e Inter (licença OFL), embutidas para o render. |
| `avaliacoes/` | Uma ficha JSON por vinho: é o registro permanente de cada nota e das fontes. |

Uso, na raiz do repositório:

```
python3 _automacao/gerar.py _automacao/avaliacoes/<slug>.json
```

Saída com código 1 = há alerta de metodologia ou texto estourando um slide; corrija antes de publicar.

Regra de custo-benefício (aprovada em 21/10/2026; substitui a fórmula com Índice de Preço da seção 5.1, que dava 10 para todo vinho):
`C/B = 7,0 + 1,8 × (média V+A+P − expectativa da faixa) + ajustes`, limitado a 0–10.
Reproduz o exemplo oficial (Casal Garcia, R$ 55, entrega 8,6 → 9,0).

Pilar B (Balance) do BLIC: ativo quando nenhum atributo do paladar fica 2,0 ou mais acima dos demais (seção 6.3), com paladar mínimo de 6,0. A regra genérica de "subatributo ≥ 7,5" (seção 6.2) vale para L, I e C.
