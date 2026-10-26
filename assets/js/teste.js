// Wine Matcher do UVA URGENTE: quiz de 8 perguntas e recomendação entre os vereditos do site.
(function () {
  var raiz = document.querySelector('[data-matcher]');
  var dados = document.getElementById('catalogo');
  if (!raiz || !dados) return;
  var vinhos = [];
  try { vinhos = JSON.parse(dados.textContent); } catch (e) { vinhos = []; }
  var $ = function (s) { return raiz.querySelector(s); };
  $('[data-total]').textContent = vinhos.length;

  var P = [
    { id: 'docura', q: 'Como você toma café?', d: 'Ajuda a entender o quanto você curte doçura.', o: [
      ['seco', 'Puro, sem açúcar'], ['meio', 'Com um pouquinho de açúcar'], ['doce', 'Bem docinho']] },
    { id: 'acidez', q: 'Limonada, para você, é…', d: 'Acidez é o que deixa o vinho fresco e com vontade de mais um gole.', o: [
      ['alta', 'Bem azedinha, adoro'], ['media', 'Equilibrada'], ['baixa', 'Docinha, sem azedo']] },
    { id: 'tanino', q: 'Chá preto forte ou chocolate 70%?', d: 'Aquela sensação de boca seca é o tanino, que aparece nos tintos.', o: [
      ['gosta', 'Adoro, quanto mais intenso melhor'], ['neutro', 'Gosto, mas sem exagero'], ['nao', 'Prefiro coisas suaves']] },
    { id: 'corpo', q: 'Se o vinho fosse leite, seria…', d: 'Corpo é o peso do vinho na boca.', o: [
      ['leve', 'Desnatado: leve'], ['medio', 'Semidesnatado: no meio'], ['encorpado', 'Integral: cheio e marcante']] },
    { id: 'aroma', q: 'Qual cheiro te ganha?', d: 'Escolha o que mais combina com você.', o: [
      ['fresco', 'Frutas frescas e flores'], ['maduro', 'Fruta madura e especiarias'], ['madeira', 'Baunilha, tostado e madeira'], ['terra', 'Ervas, terra e cogumelos']] },
    { id: 'bolha', q: 'E as borbulhas?', d: 'Espumante não é só para festa.', o: [
      ['sim', 'Amo espumante'], ['talvez', 'Às vezes'], ['nao', 'Prefiro sem bolha']] },
    { id: 'comida', q: 'Com o que você vai abrir a garrafa?', d: 'O prato muda bastante a escolha.', o: [
      ['carne', 'Churrasco e carne vermelha'], ['massa', 'Massa, pizza ou lasanha'], ['peixe', 'Peixe, frutos do mar ou salada'], ['petisco', 'Petiscos e comemoração'], ['sozinho', 'Sem comida, só relaxar']] },
    { id: 'preco', q: 'Quanto quer gastar na garrafa?', d: 'Mostramos primeiro o que cabe no bolso.', o: [
      ['50', 'Até R$ 50'], ['100', 'Até R$ 100'], ['200', 'Até R$ 200'], ['9999', 'Tanto faz, quero o melhor']] }
  ];
  var R = {}, i = 0;

  function tela(nome) {
    raiz.querySelectorAll('[data-tela]').forEach(function (t) { t.hidden = t.dataset.tela !== nome; });
    window.scrollTo({ top: raiz.offsetTop - 16, behavior: 'smooth' });
  }

  function mostrar() {
    var p = P[i];
    $('[data-contador]').textContent = 'Pergunta ' + (i + 1) + ' de ' + P.length;
    $('[data-barra]').style.width = ((i + 1) / P.length * 100) + '%';
    $('[data-pergunta]').textContent = p.q;
    $('[data-dica]').textContent = p.d;
    var box = $('[data-opcoes]'); box.innerHTML = '';
    box.setAttribute('aria-label', p.q);
    p.o.forEach(function (op) {
      var b = document.createElement('button');
      b.type = 'button'; b.className = 'm-opcao'; b.textContent = op[1];
      if (R[p.id] === op[0]) b.classList.add('ativa');
      b.addEventListener('click', function () { R[p.id] = op[0]; if (i < P.length - 1) { i++; mostrar(); } else { resultado(); } });
      box.appendChild(b);
    });
    $('[data-voltar]').style.visibility = i === 0 ? 'hidden' : 'visible';
    $('[data-pergunta]').focus({ preventScroll: true });
  }

  // ── Motor de match ──
  var tem = function (v, tag) { return (v.e || []).indexOf(tag) >= 0; };
  function corpoDe(v) { return tem(v, 'encorpado') ? 'encorpado' : tem(v, 'leve') ? 'leve' : 'medio'; }
  function afinidadeTipo(tipo) {
    var s = 0;
    if (tipo === 'tinto') { s += { gosta: 1.2, neutro: .4, nao: -1 }[R.tanino]; s += { encorpado: 1, medio: .4, leve: -.4 }[R.corpo];
      s += { carne: 1.2, massa: .8, peixe: -1, petisco: -.2, sozinho: .3 }[R.comida]; s += { sim: -.4, talvez: 0, nao: .3 }[R.bolha]; }
    if (tipo === 'branco') { s += { alta: 1, media: .4, baixa: -.3 }[R.acidez]; s += { leve: .8, medio: .4, encorpado: -.6 }[R.corpo];
      s += { carne: -1, massa: .2, peixe: 1.2, petisco: .5, sozinho: .5 }[R.comida]; s += { gosta: -.6, neutro: 0, nao: .6 }[R.tanino]; }
    if (tipo === 'rose') { s += { alta: .6, media: .5, baixa: 0 }[R.acidez]; s += { leve: .8, medio: .4, encorpado: -.6 }[R.corpo];
      s += { carne: -.6, massa: .4, peixe: .8, petisco: .9, sozinho: .6 }[R.comida]; s += { gosta: -.5, neutro: .1, nao: .6 }[R.tanino]; }
    if (tipo === 'espumante') { s += { sim: 2.2, talvez: .4, nao: -2.5 }[R.bolha]; s += { alta: .6, media: .3, baixa: 0 }[R.acidez];
      s += { carne: -.8, massa: 0, peixe: .7, petisco: 1.2, sozinho: .3 }[R.comida]; }
    return Math.max(0, Math.min(1, (s + 2) / 5));
  }
  function avaliar(v) {
    var c = corpoDe(v), ordem = ['leve', 'medio', 'encorpado'];
    var dist = Math.abs(ordem.indexOf(c) - ordem.indexOf(R.corpo));
    var pts = {
      tipo: afinidadeTipo(v.tipo) * 32,
      corpo: [1, .45, 0][dist] * 18,
      acidez: (R.acidez === 'alta' ? (tem(v, 'fresco') ? 1 : .35) : R.acidez === 'baixa' ? (tem(v, 'fresco') ? .35 : 1) : .75) * 10,
      docura: (R.docura === 'seco' ? (tem(v, 'adocicado') ? .1 : 1) : R.docura === 'meio' ? (tem(v, 'adocicado') ? 1 : .6) : (tem(v, 'adocicado') ? 1 : .25)) * 8,
      aroma: ({ fresco: (tem(v, 'floral') ? 1 : (tem(v, 'frutado') && !tem(v, 'amadeirado') ? .75 : .3)), maduro: (tem(v, 'especiado') ? 1 : .35),
               madeira: (tem(v, 'amadeirado') || tem(v, 'tostado') ? 1 : .25), terra: (tem(v, 'terroso') ? 1 : .3) })[R.aroma] * 14,
      tanino: v.tipo === 'tinto' && v.tn ? ((R.tanino === 'gosta' ? (v.tn >= 7.5 ? 1 : .5) : R.tanino === 'nao' ? (v.tn < 7 ? 1 : .3) : .8) * 6) : 4,
      nota: Math.max(0, Math.min(1, (v.n - 6.5) / 2.5)) * 12
    };
    var total = 0; for (var k in pts) total += pts[k];
    var orc = +R.preco, cabe = !v.pmin || v.pmin <= orc;
    if (!cabe) total *= .55;
    return { v: v, total: total, pts: pts, cabe: cabe, corpo: c };
  }
  var NOMES_TIPO = { tinto: 'Tinto', branco: 'Branco', rose: 'Rosé', espumante: 'Espumante' };
  var COMIDA = { carne: 'churrasco e carne vermelha', massa: 'massa e pizza', peixe: 'peixe e frutos do mar', petisco: 'petiscos e comemoração', sozinho: 'tomar sem compromisso' };
  function motivos(r) {
    var m = [], v = r.v;
    if (r.pts.tipo >= 22) m.push(NOMES_TIPO[v.tipo] + ' combina com ' + COMIDA[R.comida]);
    if (r.pts.corpo >= 18) m.push('Corpo ' + { leve: 'leve', medio: 'médio', encorpado: 'encorpado' }[r.corpo] + ', como você pediu');
    if (r.pts.aroma >= 13) m.push({ fresco: 'Aromas de fruta fresca e flores', maduro: 'Fruta madura e especiarias no nariz', madeira: 'Toque de madeira e tostado', terra: 'Notas terrosas e de ervas' }[R.aroma]);
    if (R.acidez === 'alta' && tem(v, 'fresco')) m.push('Acidez viva, bem fresco');
    if (r.cabe && +R.preco < 9999) m.push('Cabe no seu orçamento');
    if (v.n >= 8.1) m.push('Uma das melhores notas da casa');
    return m.slice(0, 3);
  }
  function selo(n) {
    if (n >= 9.6) return [5, '⚡ Urgente · Compre Agora']; if (n >= 9.1) return [4, 'Vale a Pena'];
    if (n >= 8.1) return [3, 'Boa Pedida']; if (n >= 6.1) return [2, 'Sem Pressa']; return [1, 'Sem Urgência'];
  }
  var virgula = function (x) { return (+x).toFixed(1).replace('.', ','); };
  var esc = function (s) { return String(s || '').replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  function perfil() {
    var corpo = { leve: 'leve', medio: 'de corpo médio', encorpado: 'encorpado' }[R.corpo];
    var aroma = { fresco: 'frutado e floral', maduro: 'de fruta madura e especiarias', madeira: 'com toque de madeira', terra: 'terroso e de ervas' }[R.aroma];
    var bolha = R.bolha === 'sim' ? ' e borbulhas' : '';
    return { t: 'Seu vinho é ' + corpo + ', ' + aroma + '.', d: 'Você gosta de vinho ' + corpo + ', ' + aroma + bolha + ', para ' + COMIDA[R.comida] + '. Estes são os vinhos avaliados que mais combinam com você.' };
  }

  function resultado() {
    var lista = vinhos.map(avaliar).sort(function (a, b) { return b.total - a.total; }).slice(0, 3);
    var pf = perfil();
    $('[data-perfil]').textContent = pf.t;
    $('[data-perfil-texto]').textContent = pf.d;
    var maior = lista.length ? lista[0].total : 1;
    $('[data-resultados]').innerHTML = lista.map(function (r, k) {
      var v = r.v, s = selo(v.n), pct = Math.round(Math.min(98, 62 + 36 * r.total / Math.max(maior, 1)));
      var preco = v.pmin ? ('R$ ' + v.pmin + (v.pmax && v.pmax !== v.pmin ? '–' + v.pmax : '')) : '';
      var loja = (v.l || [])[0];
      return '<article class="m-card">' +
        '<div class="m-garrafa">' + (v.img ? '<img src="' + esc(v.img) + '" alt="Garrafa de ' + esc(v.t) + '" loading="lazy">' : '') + '</div>' +
        '<div class="m-corpo">' +
          '<p class="kicker">' + (k === 0 ? 'Seu match' : 'Também combina') + ' · ' + pct + '%</p>' +
          '<h3 class="card-nome"><a href="' + esc(v.u) + '">' + esc(v.t) + '</a>.</h3>' +
          '<p class="card-produtor">' + esc([v.pr, v.sf].filter(Boolean).join(' · ')) + '</p>' +
          '<div class="pills"><span class="selo selo-' + s[0] + '">' + s[1] + '</span>' + (v.pv ? '<span class="selo selo-provado card-provado">Provado</span>' : '') + '</div>' +
          '<ul class="m-motivos">' + motivos(r).map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul>' +
          '<div class="m-rodape"><span class="m-nota">' + virgula(v.n) + '<small>/10</small></span><span class="preco">' + preco + '</span></div>' +
          '<div class="m-botoes"><a class="btn btn-linha btn-sm" href="' + esc(v.u) + '">Ver veredito</a>' +
          (loja ? '<a class="btn btn-cobalt btn-sm" href="' + esc(loja.url) + '" rel="sponsored noopener" target="_blank">Comprar na ' + esc(loja.nome) + '</a>' : '') + '</div>' +
        '</div></article>';
    }).join('');
    try { localStorage.setItem('uu-teste', JSON.stringify({ r: R, em: Date.now() })); } catch (e) {}
    if (typeof gtag === 'function') gtag('event', 'teste_concluido', { perfil_corpo: R.corpo, perfil_aroma: R.aroma, primeiro_vinho: lista[0] && lista[0].v.t });
    tela('resultado');
    $('[data-perfil]').focus({ preventScroll: true });
  }

  $('[data-comecar]').addEventListener('click', function () { R = {}; i = 0; tela('quiz'); mostrar(); });
  $('[data-voltar]').addEventListener('click', function () { if (i > 0) { i--; mostrar(); } });
  $('[data-refazer]').addEventListener('click', function () { R = {}; i = 0; tela('quiz'); mostrar(); });
  $('[data-compartilhar]').addEventListener('click', function () {
    var txt = $('[data-perfil]').textContent + ' Descubra o seu vinho no teste do UVA URGENTE:';
    var url = location.origin + location.pathname;
    if (navigator.share) { navigator.share({ title: 'Qual é o seu vinho?', text: txt, url: url }).catch(function () {}); }
    else if (navigator.clipboard) { navigator.clipboard.writeText(txt + ' ' + url).then(function () { $('[data-compartilhar]').textContent = 'Link copiado!'; }); }
  });
})();
