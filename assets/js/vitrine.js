// Filtro por categoria da página /alem-do-vinho/ (sem bibliotecas).
(function () {
  var chips = document.querySelector('[data-chips]');
  var lista = document.querySelector('[data-vitrine]');
  if (!chips || !lista) return;
  var botoes = Array.prototype.slice.call(chips.querySelectorAll('[data-cat]'));
  function aplicar(cat) {
    botoes.forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.cat === cat)); });
    lista.querySelectorAll('.card-produto').forEach(function (c) { c.hidden = !!cat && c.dataset.categoria !== cat; });
    history.replaceState(null, '', cat ? '?categoria=' + cat : location.pathname);
  }
  chips.addEventListener('click', function (e) { var b = e.target.closest('[data-cat]'); if (b) aplicar(b.dataset.cat); });
  var inicial = new URLSearchParams(location.search).get('categoria') || '';
  aplicar(inicial);
})();
