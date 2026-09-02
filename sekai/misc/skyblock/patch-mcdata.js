const fs = require('fs');
const path = require('path');

const ver = '26.1.2', base = '1.21.11';
const mcDir = path.dirname(require.resolve('minecraft-data'));

// 1. Create protocol data directory
const pkDir = path.join(mcDir, 'minecraft-data', 'data', 'pc');
const vDir = path.join(pkDir, ver);
if (!fs.existsSync(vDir)) {
  fs.mkdirSync(vDir, { recursive: true });
  for (const f of fs.readdirSync(path.join(pkDir, base))) {
    if (f.endsWith('.json')) fs.cpSync(path.join(pkDir, base, f), path.join(vDir, f));
  }
  const lp = path.join(pkDir, 'latest', 'proto.yml');
  if (fs.existsSync(lp)) {
    let p = fs.readFileSync(lp, 'utf8');
    fs.writeFileSync(path.join(vDir, 'proto.yml'), p.replace(/!version: [\d.]+/, '!version: ' + ver));
  }
}

// 2. dataPaths.json
const dpPath = path.join(mcDir, 'minecraft-data', 'data', 'dataPaths.json');
let dp = JSON.parse(fs.readFileSync(dpPath, 'utf8'));
if (!dp.pc[ver]) {
  dp.pc[ver] = { ...dp.pc[base], protocol: 'pc/' + ver, proto: 'pc/' + ver };
  fs.writeFileSync(dpPath, JSON.stringify(dp, null, 2) + '\n');
}

// 3. protocolVersions.json
const pvPath = path.join(pkDir, 'common', 'protocolVersions.json');
let pv = JSON.parse(fs.readFileSync(pvPath, 'utf8'));
if (!pv.find(e => e.minecraftVersion === ver)) {
  pv.unshift({ minecraftVersion: ver, version: 775, dataVersion: 4790, usesNetty: true, majorVersion: '26.1', releaseType: 'release' });
  fs.writeFileSync(pvPath, JSON.stringify(pv, null, 2) + '\n');
}

// 4. versions.json
const vJson = path.join(pkDir, 'common', 'versions.json');
let v = JSON.parse(fs.readFileSync(vJson, 'utf8'));
if (!v.includes(ver)) { v.unshift(ver); fs.writeFileSync(vJson, JSON.stringify(v, null, 2) + '\n'); }

// 5. data.js — INSERT BEFORE pc CLOSE, AFTER 1.21.11
const dataJsPath = path.join(mcDir, 'data.js');
let content = fs.readFileSync(dataJsPath, 'utf8');

if (!content.includes("'" + ver + "'")) {
  // Find the closing of pc: "  },\n  'bedrock':"
  const closeSeq = "  },\n  'bedrock':";
  const closeIdx = content.lastIndexOf(closeSeq);
  if (closeIdx === -1) throw new Error('Cannot find close sequence');

  // Go backwards from closeIdx to find the 4-space closing "    }" of 1.21.11
  // Find the last "    }\n" that ends before closeIdx
  const beforeClose = content.substring(0, closeIdx);
  const lastBlockClose = beforeClose.lastIndexOf("\n    }\n");
  if (lastBlockClose === -1) throw new Error('Cannot find last block close');

  // The "    }" at lastBlockClose+1 is the close of 1.21.11
  // Replace it with "    },\n" + 26.1.2 block + "\n    }"

  // Extract the 1.21.11 block
  const mStart = "    '" + base + "': {";
  const mEnd = "proto: __dirname + '/minecraft-data/data/pc/latest/proto.yml'\n    }";
  const blockStart = content.indexOf(mStart);
  const blockEnd = content.indexOf(mEnd, blockStart);
  if (blockStart === -1 || blockEnd === -1) throw new Error('Cannot find 1.21.11 block');

  const block1211 = content.substring(blockStart, blockEnd + mEnd.length);
  const block2612 = block1211.replace(/1\.21\.11/g, ver);

  // Find the exact "    }\n" before pc close to replace
  const insertAt = lastBlockClose + 1; // points to "    }"
  const originalClose = content.substring(insertAt, insertAt + 5); // "    }"
  if (originalClose !== "    }") {
    throw new Error('Expected "    }" at position ' + insertAt + ', got: ' + JSON.stringify(originalClose));
  }

  // Build new content
  const newEntry = "    },\n" + block2612 + "\n    }";
  content = content.substring(0, insertAt) + newEntry + content.substring(insertAt + 5);

  fs.writeFileSync(dataJsPath, content);
  console.log('Patched data.js');
}

// Clear cache
for (const k of Object.keys(require.cache)) delete require.cache[k];

// Verify
const mcData = require('minecraft-data');
const test = mcData(ver);
if (!test) throw new Error('Failed: mcData("' + ver + '") = null');
console.log('OK: ' + ver + ' protocol=' + test.version.version);

const data = require('minecraft-data/data.js');
console.log('data.pc["' + ver + '"]:', !!data.pc[ver]);
