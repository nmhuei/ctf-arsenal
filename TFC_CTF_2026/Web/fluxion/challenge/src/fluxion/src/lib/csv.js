'use strict';




function cell(v) {
  const s = v == null ? '' : String(v);
  if (/[",\n\r]/.test(s)) return '"' + s.replace(/"/g, '""') + '"';
  return s;
}


function toCsv(rows, columns) {
  const cols = Array.isArray(columns) && columns.length
    ? columns
    : (rows[0] ? Object.keys(rows[0]) : []);
  const head = cols.map(cell).join(',');
  const body = rows.map((r) => cols.map((c) => cell(r[c])).join(',')).join('\n');
  return body ? head + '\n' + body : head;
}

module.exports = { toCsv, cell };
