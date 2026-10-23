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

## Notícias, Além do Vinho e Playlists

- **Notícia:** salve `_automacao/noticias/<slug>.json` e rode `python3 _automacao/gerar_extra.py _automacao/noticias/<slug>.json`.
  Gera `_noticias/<slug>.md`, a imagem de compartilhamento `assets/img/noticias/<slug>.png` (1200×630),
  o Story `_automacao/saida/noticias/<slug>/story.png` (1080×1920) e `link.txt` (endereço para o sticker de link).
  Campos: slug, data, categoria, titulo (até 100), linha_story (até 140), resumo (até 420), texto (lista de parágrafos, opcional),
  porque_importa (até 320), fonte {nome, url, data, titulo}, outras_fontes [{nome, url}], vereditos [slugs].
  Texto sempre próprio: nunca copiar a matéria nem usar foto da fonte.
- **Produto (Além do Vinho):** salve `_automacao/alem/<slug>.json` e rode o mesmo script.
  Campos: slug, data, titulo, marca, categoria, frase (até 120), destaques [3 itens], usamos (true se o Tiago usa),
  imagem_origem (só foto enviada pelo Tiago), lojas [{nome, url}] (links do Tiago), vereditos [slugs], texto (opcional).
  Nunca mostrar preço fixo da loja: o botão diz "Ver preço na Amazon / no Mercado Livre".
- **Playlist:** acrescente um bloco em `_data/playlists.yml` (modelo no topo do arquivo). Os vinhos aparecem sozinhos
  pelas tags `tipos` (qualquer uma) e `estilos` (todas), usando as tags que o `gerar.py` grava em cada veredito (`estilos:`).
- Os itens de menu Notícias, Além do Vinho e Playlists só aparecem quando houver ao menos um item publicado.
