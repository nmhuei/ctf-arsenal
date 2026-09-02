/**
 * Simple Minecraft protocol client for Paper 1.21.11/Skyblock
 * Uses minecraft-protocol directly (not mineflayer)
 */
const mc = require('minecraft-protocol');
const HOST = 'skyblock.chals.sekai.team';
const PORT = 25565;
const USERNAME = `B${Math.floor(Math.random() * 10000)}`;

const client = mc.createClient({
  host: HOST,
  port: PORT,
  username: USERNAME,
  auth: 'offline',
  version: false,  // auto-detect
});

client.on('session', () => {
  console.log(`[+] Connected as ${client.username}`);
});

client.on('keep_alive', () => {
  console.log('[KA] keep_alive');
});

client.on('login', (packet) => {
  console.log(`[+] Login received: ${JSON.stringify(packet).slice(0, 200)}`);
});

client.on('position', (packet) => {
  console.log(`[+] Position: ${JSON.stringify(packet)}`);
  client.write('teleport_confirm', { teleportId: packet.teleportId });
});

client.on('chat', (packet) => {
  console.log(`[CHAT] ${packet.message}`);
});

client.on('system_chat', (packet) => {
  console.log(`[SYS] ${JSON.stringify(packet).slice(0, 300)}`);
});

client.on('title', (packet) => {
  console.log(`[TITLE] ${JSON.stringify(packet).slice(0, 200)}`);
});

client.on('set_title_subtitle', (packet) => {
  console.log(`[SUB] ${JSON.stringify(packet)}`);
});

client.on('action_bar', (packet) => {
  console.log(`[BAR] ${JSON.stringify(packet)}`);
});

client.on('kick_disconnect', (packet) => {
  console.log(`[KICK] ${JSON.stringify(packet)}`);
});

client.on('error', (err) => {
  console.log(`[ERR] ${err.message}`);
});

client.on('end', (reason) => {
  console.log(`[END] ${reason}`);
});

// Log all packets (verbose)
client.on('packet', (data, { name, state }) => {
  if (!['keep_alive', 'unload_chunk', 'block_change', 'tick', 'sync_entity_position',
        'entity_metadata', 'entity_velocity', 'entity_equipment', 'rel_entity_move',
        'entity_move_look', 'entity_look', 'entity_head_rotation', 'sound_effect',
        'entity_sound_effect', 'world_particles', 'update_light', 'map_chunk',
        'chunk_batch_finished', 'chunk_batch_start', 'set_ticking_state',
        'step_tick', 'debug_sample', 'spawn_entity', 'animation',
        'set_passengers', 'attach_entity', 'entity_effect', 'remove_entity_effect',
        'entity_destroy', 'entity_status', 'update_view_position', 'update_view_distance',
        'world_border_center', 'world_border_size', 'simulation_distance',
        'server_data', 'recipe_book_settings', 'abilities', 'held_item_slot',
        'scoreboard_objective', 'scoreboard_score', 'teams', 'playerlist_header',
        'player_info', 'update_time', 'game_state_change', 'experience',
        'update_health', 'set_ticking_state', 'reset_score', 'entity_teleport',
        'collect', 'set_player_inventory', 'set_slot', 'window_items',
        'craft_progress_bar', 'close_window', 'declare_recipes', 'tags',
        'select_advancement_tab', 'advancements', 'face_player',
        'boss_bar', 'player_rotation', 'tracked_waypoint'].includes(name)) {
    console.log(`[PKT ${state}/${name}]`);
  }
});

// Send commands after delay
setTimeout(() => {
  console.log('[CMD] /tradebook list');
  client.write('chat_command', { command: 'tradebook list' });
}, 5000);

setTimeout(() => {
  console.log('[CMD] /coins');
  client.write('chat_command', { command: 'coins' });
}, 12000);

setTimeout(() => {
  console.log('[CMD] /tradebook help');
  client.write('chat_command', { command: 'tradebook help' });
}, 20000);

// Stay connected for 45s
setTimeout(() => {
  console.log('[DONE] Ending connection');
  client.end();
  process.exit(0);
}, 45000);
