// Filtros e ordenação da página /vereditos/ (sem bibliotecas).
(function () {
  var form = document.querySelector('[data-filtros]');
  var lista = document.querySelector('[data-lista]');
  if (!form || !lista) return;
  var contagem = document.querySelector('[data-contagem]');
  var vazio = document.querySelector('[data-vazio]');
  var cards = Array.prototype.slice.call(lista.querySelectorAll('.card'));

  function aplicar() {
    var tipo = form.tipo.value;
    var faixa = form.faixa.value;
    var ordem = form.ordem.value;

    cards.sort(function (a, b) {
      if (ordem === 'nota') return parseFloat(b.dataset.nota) - parseFloat(a.dataset.nota);
      if (ordem === 'preco') return parseFloat(a.dataset.preco || 9999) - parseFloat(b.dataset.preco || 9999);
      return parseInt(b.dataset.data, 10) - parseInt(a.dataset.data, 10);
    });

    var visiveis = 0;
    cards.forEach(function (c) {
      var ok = (!tipo || c.dataset.tipo === tipo) && (!faixa || c.dataset.faixa === faixa);
      c.hidden = !ok;
      if (ok) visiveis++;
      lista.appendChild(c);
    });

    if (contagem) contagem.textContent = visiveis === 1 ? '1 vinho' : visiveis + ' vinhos';
    if (vazio) vazio.hidden = visiveis !== 0;

    var params = new URLSearchParams();
    if (tipo) params.set('tipo', tipo);
    if (faixa) params.set('faixa', faixa);
    if (ordem !== 'data') params.set('ordem', ordem);
    var qs = params.toString();
    history.replaceState(null, '', qs ? '?' + qs : location.pathname);
  }

  // Lê filtros da URL (ex.: /vereditos/?faixa=ate-50 nos links do Instagram)
  var inicial = new URLSearchParams(location.search);
  ['tipo', 'faixa', 'ordem'].forEach(function (k) {
    if (inicial.get(k) && form[k]) form[k].value = inicial.get(k);
  });

  form.addEventListener('change', aplicar);
  aplicar();
})();
