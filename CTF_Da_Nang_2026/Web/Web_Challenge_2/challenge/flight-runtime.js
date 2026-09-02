/**
 * Flight v1.3 client runtime  (NebulaCommerce)
 * --------------------------------------------
 * Decodes the streamed row format produced by /api/flight.
 *
 * Wire format (line-delimited):
 *   <rowId>:<tag><payload>\n
 *
 *   tag = 'I'   import marker  — payload is a JSON string
 *   tag = 'M'   model           — payload is a JSON object (the React tree)
 *   tag = 'T'   text fragment   — payload is a JSON string
 *   tag = 'E'   error           — payload is { message }
 *
 * The runtime understands one object directive in the public stream:
 *
 *   { "$ref": "<rowId>" }   — inline another row's payload at this position.
 *
 * Server actions
 * --------------
 * Mutations (e.g. add-to-cart) are encoded as a Flight POST: a single
 * model row describing the action, optionally referencing other rows
 * via $ref. The server replies with the new model fragment.
 */
(function () {
  'use strict';

  function decode(text) {
    const rows = [];
    for (const line of text.split('\n')) {
      if (!line) continue;
      const i = line.indexOf(':');
      if (i < 0) continue;
      const id = line.slice(0, i);
      const rest = line.slice(i + 1);
      const tag = rest[0];
      let payload = rest.slice(1);
      try { payload = JSON.parse(payload); } catch (_) { /* keep raw */ }
      rows.push({ id, tag, payload });
    }
    return rows;
  }

  function reify(node, byId) {
    if (node === null || typeof node !== 'object') return node;
    if (Array.isArray(node)) return node.map(n => reify(n, byId));
    if (typeof node['$ref'] === 'string') {
      const r = byId.get(node['$ref']);
      return r ? reify(r.payload, byId) : null;
    }
    const out = {};
    for (const k of Object.keys(node)) out[k] = reify(node[k], byId);
    return out;
  }

  function render(model, mount) {
    if (!model || model.type !== 'PageRoot') return;
    const grid = mount.querySelector('#grid');
    if (!grid) return;
    grid.innerHTML = '';
    const catalog = (model.props.children || []).find(c => c.type === 'Catalog');
    const items = (catalog && catalog.props.items) || [];
    for (const it of items) {
      const card = document.createElement('div');
      card.className = 'card';
      const pid    = document.createElement('div'); pid.className = 'pid';   pid.textContent = it.id;
      const pname  = document.createElement('div'); pname.className = 'pname'; pname.textContent = it.name;
      const meta   = document.createElement('div'); meta.className = 'meta';
      const price  = document.createElement('span'); price.textContent = '$' + it.price;
      const stock  = document.createElement('span'); stock.className = 'stock'; stock.textContent = it.stock + ' in stock';
      meta.appendChild(price); meta.appendChild(stock);
      const btn    = document.createElement('button');
      btn.className = 'add'; btn.type = 'button';
      btn.dataset.pid = it.id; btn.textContent = 'Add to cart';
      card.appendChild(pid); card.appendChild(pname); card.appendChild(meta); card.appendChild(btn);
      grid.appendChild(card);
    }
  }

  function encodeAction(action, payload) {
    const model = { action: action, payload: payload };
    return '0:I"app/_next/static/chunks/flight-runtime.js"\n'
         + '1:M' + JSON.stringify(model) + '\n';
  }

  window.Flight = { decode, reify, render, encodeAction };
})();
