/* main.js — boots NebulaCommerce, wires the cart server-action */
(function () {
  'use strict';

  function loadCatalog() {
    return fetch('/api/flight', { headers: { Accept: 'text/x-component' } })
      .then(r => r.text())
      .then(text => {
        const rows = window.Flight.decode(text);
        const byId = new Map(rows.map(r => [r.id, r]));
        const main = rows.find(r => r.tag === 'M');
        if (!main) return;
        const model = window.Flight.reify(main.payload, byId);
        window.Flight.render(model, document.getElementById('__next'));
      });
  }

  function bumpCart(n) {
    const el = document.getElementById('cart-count');
    if (!el) return;
    const cur = parseInt(el.textContent, 10) || 0;
    el.textContent = String(cur + n);
  }

  function flash(msg, ok) {
    const el = document.getElementById('flash');
    if (!el) return;
    el.textContent = msg;
    el.className = 'flash ' + (ok ? 'ok' : 'err');
    setTimeout(() => { el.textContent = ''; el.className = 'flash'; }, 2400);
  }

  function addToCart(pid) {
    const body = window.Flight.encodeAction('addToCart', { sku: pid, qty: 1 });
    return fetch('/api/flight', {
      method: 'POST',
      headers: { 'Content-Type': 'text/x-component' },
      body: body,
    })
      .then(r => r.json())
      .then(j => {
        if (j && j.ok) {
          bumpCart(1);
          flash('Added ' + pid + ' to cart', true);
        } else {
          flash('Cart action failed: ' + (j && j.error || 'unknown'), false);
        }
      })
      .catch(err => flash('network error: ' + err, false));
  }

  document.addEventListener('click', function (ev) {
    const t = ev.target;
    if (t && t.classList && t.classList.contains('add') && t.dataset.pid) {
      addToCart(t.dataset.pid);
    }
  });

  loadCatalog().catch(err => console.warn('flight load failed', err));
})();
