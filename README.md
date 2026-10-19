# UVA URGENTE — site

Site do UVA URGENTE, publicado pelo GitHub Pages com Jekyll. Este arquivo não aparece no site; é o manual rápido de manutenção.

## O que fica em cada pasta

| Pasta ou arquivo | O que é | Você mexe? |
| --- | --- | --- |
| `_config.yml` | Nome, endereço, Instagram, integrações | Sim, só os valores |
| `_vereditos/` | Um arquivo `.md` por vinho avaliado | Sim, toda semana |
| `_posts/` | Um arquivo `.md` por artigo (guia) | Sim |
| `modelos/` | Modelos para copiar (veredito e artigo); não vão para o site | Só para copiar |
| `assets/img/vereditos/` | Fotos das garrafas (PNG com fundo transparente) | Sim |
| `assets/img/og-padrao.png` | Imagem que aparece quando o link do site é compartilhado | Opcional |
| `teste/index.html` | Página do Wine Matcher (hoje provisória) | Quando o app for publicado |
| `metodologia.md`, `sobre.md`, `parcerias.md`, `privacidade.md` | Páginas institucionais | Preencha os campos entre colchetes |
| `_layouts/`, `_includes/`, `assets/css/`, `assets/js/` | Visual e estrutura | Não, a menos que queira mudar o design |

## Publicar um veredito

1. Abra `modelos/veredito.md` e copie todo o conteúdo.
2. Na pasta `_vereditos/`, crie um arquivo novo com o nome do vinho em minúsculas e hífens, terminando em `.md` (exemplo: `miolo-seival-merlot-2022.md`).
3. Cole o conteúdo, preencha os campos e salve (commit).
4. Se tiver foto, envie o PNG para `assets/img/vereditos/` e coloque o caminho no campo `imagem`.
5. Em 1 a 3 minutos o vinho aparece em `/vereditos/`, na home e em `/onde-comprar/`.

Regras que evitam erro:
- `nota` usa **ponto**: `9.1`, nunca `9,1`.
- `preco_min` e `preco_max` são só números: `59`, sem "R$".
- O `preco` de cada loja vai entre aspas e com vírgula: `"64,90"`.
- Não apague as duas linhas `---` do começo do arquivo.

## Publicar um artigo

1. Copie `modelos/artigo.md`.
2. Na pasta `_posts/`, crie o arquivo com o nome no formato `ANO-MES-DIA-titulo.md` (exemplo: `2026-11-10-vinho-para-churrasco.md`). Sem a data no início do nome, o artigo não aparece.
3. Preencha e salve.

## Se o site não atualizar

Abra a aba **Actions** do repositório. Um X vermelho mostra o erro; quase sempre é uma vírgula no lugar de ponto na nota, aspas faltando ou as linhas `---` apagadas. Corrija o arquivo e salve de novo.

## Ver o site no seu computador (opcional)

Com Ruby instalado: `bundle install` e depois `bundle exec jekyll serve`. O site abre em `http://localhost:4000`.
