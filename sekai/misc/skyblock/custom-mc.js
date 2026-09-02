const minecraftData = require('minecraft-data');
const path = require('path');
const fs = require('fs');

// Patch minecraft-data to support 26.1.2 at runtime
function patchMinecraftData() {
  const mcDataRoot = path.dirname(require.resolve('minecraft-data'));
  const pkDir = path.join(mcDataRoot, 'minecraft-data', 'data', 'pc');

  // 1. Create 26.1.2 data directory if not exists
  const v2612Dir = path.join(pkDir, '26.1.2');
  if (!fs.existsSync(v2612Dir)) {
    const srcDir = path.join(pkDir, '1.21.11');
    fs.mkdirSync(v2612Dir, { recursive: true });
    for (const f of fs.readdirSync(srcDir)) {
      fs.cpSync(path.join(srcDir, f), path.join(v2612Dir, f));
    }
    // Copy proto.yml and fix version
    const latestProto = path.join(pkDir, 'latest', 'proto.yml');
    fs.cpSync(latestProto, path.join(v2612Dir, 'proto.yml'));
    let proto = fs.readFileSync(path.join(v2612Dir, 'proto.yml'), 'utf8');
    fs.writeFileSync(path.join(v2612Dir, 'proto.yml'), proto.replace('!version: 1.21.11', '!version: 26.1.2'));
  }

  // 2. Add to dataPaths if missing
  const dpPath = path.join(mcDataRoot, 'minecraft-data', 'data', 'dataPaths.json');
  const dp = JSON.parse(fs.readFileSync(dpPath, 'utf8'));
  if (!dp.pc['26.1.2']) {
    dp.pc['26.1.2'] = { ...dp.pc['1.21.11'], protocol: 'pc/26.1.2', proto: 'pc/26.1.2' };
    fs.writeFileSync(dpPath, JSON.stringify(dp, null, 2) + '\n');
  }

  // 3. Patch the index.js to make toMajor find 26.1.2
  const idxPath = path.join(mcDataRoot, 'index.js');
  // We don't need to modify the file - we'll use our own custom loading

  // 4. Directly modify the in-memory data object that minecraft-data uses
  // Since minecraft-data uses data.js which is built at require() time,
  // we need to add 26.1.2 to the data object
  const data = require('minecraft-data/data.js');
  if (!data.pc['26.1.2']) {
    data.pc['26.1.2'] = {};
    const src = data.pc['1.21.11'];
    for (const key of Object.keys(src)) {
      const desc = Object.getOwnPropertyDescriptor(src, key);
      if (desc && (desc.get || typeof src[key] !== 'string')) {
        // It's a getter or non-string value
        Object.defineProperty(data.pc['26.1.2'], key.replace(/1\.21\.11/g, '26.1.2'), {
          get: typeof desc?.get === 'function'
            ? function() {
                const val = desc.get.call(data.pc['1.21.11']);
                if (typeof val === 'string') return val.replace(/1\.21\.11/g, '26.1.2');
                return val;
              }
            : desc,
          enumerable: true,
        });
      } else {
        data.pc['26.1.2'][key] = src[key];
      }
    }
    data.pc['26.1.2'].proto = data.pc['1.21.11'].proto.replace('1.21.11', '26.1.2');
  }

  // 5. Verify
  const ver = minecraftData('26.1.2');
  if (!ver) {
    // Force cache clear and retry
    const idx2 = require.resolve('minecraft-data/index.js');
    delete require.cache[idx2];
    const result = minecraftData('26.1.2');
    if (!result) {
      console.error('WARN: minecraft-data still cannot resolve 26.1.2');
    }
  }
  return minecraftData('26.1.2');
}

// Patch it immediately
const patched = patchMinecraftData();
if (patched) {
  console.log('Patched minecraft-data for 26.1.2');
}

// Now create a custom minecraft-protocol wrapper
function createBot(options) {
  const mc = require('minecraft-protocol');

  // Configure with version override
  const opts = {
    host: options.host || 'localhost',
    port: options.port || 25565,
    username: options.username || 'bot',
    auth: 'offline',
    version: '1.21.11',  // Use 1.21.11 protocol data
    protocolVersion: 775, // But send protocol 775 (Paper 26.1.2)
  };

  // Create client directly, bypassing autoVersion
  const client = mc.createClient(opts);

  return client;
}

module.exports = {
  createBot,
  patchMinecraftData,
  minecraftData: require('minecraft-data'),
};
