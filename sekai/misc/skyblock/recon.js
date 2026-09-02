const mineflayer = require('mineflayer');

const HOST = 'skyblock.chals.sekai.team';
const PORT = 25565;
const USERNAME = `bot${Math.random().toString(36).slice(2, 7)}`;

const bot = mineflayer.createBot({
  host: HOST,
  port: PORT,
  username: USERNAME,
  version: "1.21.11",
  auth: 'offline',
  chatLengthLimit: 256,
});

const chatLog = [];
let commandsSent = 0;
let commandsComplete = 0;

bot.on('login', () => {
  console.log(`[+] Logged in as ${bot.username}`);
});

bot.on('spawn', () => {
  console.log('[+] Bot spawned in world, starting recon...\n');
  startRecon();
});

bot.on('message', (jsonMsg) => {
  const msg = jsonMsg.toString();
  console.log(`[CHAT] ${msg}`);
  chatLog.push(msg);
});

bot.on('kicked', (reason, extra) => {
  console.log(`[!] KICKED: ${reason} ${extra ? JSON.stringify(extra) : ''}`);
});

bot.on('end', (reason) => {
  console.log(`[!] Disconnected: ${reason}`);
});

bot.on('error', (err) => {
  console.log(`[!] Error: ${err.message}`);
});

function sendCmd(cmd, delay = 500) {
  setTimeout(() => {
    try {
      console.log(`[CMD] ${cmd}`);
      bot.chat(cmd);
      commandsSent++;
    } catch (e) {
      console.log(`[ERR] Failed to send ${cmd}: ${e.message}`);
    }
  }, delay);
}

function startRecon() {
  // Phase 1: Basic commands
  const P1 = 2000;
  sendCmd('/help', P1);

  // Phase 2: Economy commands
  const P2 = P1 + 3000;
  sendCmd('/balance', P2);
  sendCmd('/money', P2 + 500);
  sendCmd('/pay help', P2 + 1000);

  // Phase 3: Tradebook help
  const P3 = P2 + 4000;
  sendCmd('/tradebook help', P3);

  // Phase 4: List all tradebook items
  const P4 = P3 + 4000;
  sendCmd('/tradebook list', P4);

  // Phase 5: Check items (batch 1 - basics)
  const P5 = P4 + 5000;
  const items1 = ['dirt', 'cobblestone', 'stone', 'oak_log', 'iron_ingot', 'gold_ingot',
    'diamond', 'emerald', 'netherite_ingot', 'netherite_scrap', 'ancient_debris'];
  items1.forEach((item, i) => sendCmd(`/tradebook info ${item}`, P5 + i * 800));

  // Phase 6: Items batch 2 - farming/mob drops
  const P6 = P5 + items1.length * 800 + 2000;
  const items2 = ['wheat', 'carrot', 'potato', 'bread', 'cooked_beef', 'apple',
    'golden_apple', 'ender_pearl', 'blaze_rod', 'bone', 'string', 'feather',
    'gunpowder', 'leather', 'rotten_flesh', 'spider_eye', 'slime_ball'];
  items2.forEach((item, i) => sendCmd(`/tradebook info ${item}`, P6 + i * 800));

  // Phase 7: Items batch 3 - valuables
  const P7 = P6 + items2.length * 800 + 2000;
  const items3 = ['obsidian', 'shulker_shell', 'phantom_membrane', 'totem_of_undying',
    'elytra', 'trident', 'heart_of_the_sea', 'nautilus_shell', 'prismarine_shard',
    'prismarine_crystals', 'sponge', 'chorus_fruit', 'ghast_tear', 'magma_cream',
    'blaze_powder', 'nether_wart', 'ender_eye'];
  items3.forEach((item, i) => sendCmd(`/tradebook info ${item}`, P7 + i * 800));

  // Phase 8: Blocks batch
  const P8 = P7 + items3.length * 800 + 2000;
  const items4 = ['gravel', 'sand', 'granite', 'diorite', 'andesite', 'deepslate',
    'tuff', 'calcite', 'ice', 'packed_ice', 'blue_ice', 'glass', 'glowstone',
    'sea_lantern', 'sugar_cane', 'cactus', 'bamboo', 'kelp', 'egg', 'milk_bucket',
    'honey_block', 'honey_bottle', 'tropical_fish', 'pufferfish'];
  items4.forEach((item, i) => sendCmd(`/tradebook info ${item}`, P8 + i * 800));

  // Phase 9: Check game-specific items
  const P9 = P8 + items4.length * 800 + 2000;
  const items5 = ['redstone', 'coal', 'copper_ingot', 'lapis_lazuli', 'amethyst_shard',
    'quartz', 'netherite_block', 'diamond_block', 'emerald_block', 'iron_block',
    'gold_block', 'copper_block', 'redstone_block', 'coal_block'];
  items5.forEach((item, i) => sendCmd(`/tradebook info ${item}`, P9 + i * 800));

  // Phase 10: Special items, leaderboard, goal check
  const P10 = P9 + items5.length * 800 + 2000;
  sendCmd('/leaderboard', P10);
  sendCmd('/baltop', P10 + 1000);
  sendCmd('/island', P10 + 2000);
  sendCmd('/warp', P10 + 3000);
  sendCmd('/shop', P10 + 4000);

  // Phase 11: Try flag/key/crate type items
  const P11 = P10 + 6000;
  const items6 = ['flag', 'admin_shop', 'mythic', 'legendary', 'rare_voucher',
    'key', 'crate', 'star', 'token', 'voucher', 'compass', 'scroll', 'crystal',
    'experience_bottle', 'potion', 'book', 'paper', 'map'];
  items6.forEach((item, i) => sendCmd(`/tradebook info ${item}`, P11 + i * 800));

  // Phase 12: Check more potential items
  const P12 = P11 + items6.length * 800 + 2000;
  const items7 = ['command_block', 'structure_block', 'barrier', 'bedrock',
    'dragon_egg', 'dragon_head', 'player_head', 'beacon', 'conduit',
    'spawner', 'sculk_sensor', 'sculk_shrieker', 'reinforced_deepslate',
    'debug_stick', 'knowledge_book'];
  items7.forEach((item, i) => sendCmd(`/tradebook info ${item}`, P12 + i * 800));

  // Phase 13: More common items
  const P13 = P12 + items7.length * 800 + 2000;
  const items8 = ['arrow', 'bow', 'crossbow', 'trident', 'fishing_rod',
    'flint_and_steel', 'shears', 'shield', 'elytra', 'firework_rocket',
    'saddle', 'name_tag', 'lead', 'painting', 'item_frame', 'flower_pot',
    'armor_stand', 'end_crystal', 'respawn_anchor', 'lodestone'];
  items8.forEach((item, i) => sendCmd(`/tradebook info ${item}`, P13 + i * 800));

  // Phase 14: Wool colors, wood types, etc
  const P14 = P13 + items8.length * 800 + 2000;
  const items9 = ['white_wool', 'orange_wool', 'magenta_wool', 'light_blue_wool',
    'yellow_wool', 'lime_wool', 'pink_wool', 'gray_wool', 'light_gray_wool',
    'cyan_wool', 'purple_wool', 'blue_wool', 'brown_wool', 'green_wool',
    'red_wool', 'black_wool', 'cobweb', 'vine', 'lily_pad', 'moss_block'];
  items9.forEach((item, i) => sendCmd(`/tradebook info ${item}`, P14 + i * 800));

  // Phase 15: Summarize
  const P15 = P14 + items9.length * 800 + 5000;
  setTimeout(() => {
    console.log('\n=========== RECON COMPLETE ===========');
    console.log(`Chat log (${chatLog.length} messages):\n`);
    chatLog.forEach(line => console.log(line));
    console.log('\n=========== END LOG ===========');
    bot.end();
    process.exit(0);
  }, P15);
}
