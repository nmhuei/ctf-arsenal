import mpyq
import hashlib
from extract_hidden_blocks import read_block_directly

expected_md5s = {
    'replay.attributes.events': 'bacc44377694ee72c64ec08f0a51d329',
    'replay.details': 'bb21a9b5967674fa48aa6e44d5edb421',
    'replay.details.backup': '66fc18c56eba4eb5b00f2bcc965a1651',
    'replay.game.events': 'd397f350118bda336a776291e1e47c36',
    'replay.gamemetadata.json': 'fc893deda1ed84c2fa7a6859cfffe704',
    'replay.initData': '00000000e34e625e52025f40e433ff5f',
    'replay.initData.backup': 'e036884d1a82d0213d6030eba837dc70',
    'replay.load.info': '786bae1da3220520fb2ae9b81aa30ceb',
    'replay.message.events': 'ff7e123470eb08ffbc7c08784a259bf2',
    'replay.resumable.events': 'c7ca1f290311d650bef5cb17e4df09c9',
    'replay.server.battlelobby': '5e8e7dd0a48e10fc92748d6cbad41423',
    'replay.smartcam.events': 'e44791665a39e72f6aa79cee8813b9a9',
    'replay.sync.events': '9c3533d9eac7f22db87549e0469aa816',
    'replay.sync.history': '39a9176f625189afb2673ca0fb208605',
    'replay.tracker.events': 'b04ed163000000000000000000000000'
}

replay_path = 'misc_deadgame2/DeadGame2.SC2Replay'
archive = mpyq.MPQArchive(replay_path)

block_md5s = {}
for idx, block in enumerate(archive.block_table):
    data = read_block_directly(archive, block)
    if data:
        md5 = hashlib.md5(data).hexdigest()
        block_md5s[idx] = md5
    else:
        block_md5s[idx] = hashlib.md5(b'').hexdigest()

print("Block index mapping by MD5:")
for idx, b_md5 in block_md5s.items():
    matched_file = "None/Unknown"
    # check for exact match
    for fname, f_md5 in expected_md5s.items():
        if b_md5 == f_md5:
            matched_file = fname
            break
    # check for partial match (like tracker events MD5 with trailing zeroes)
    if matched_file == "None/Unknown":
        for fname, f_md5 in expected_md5s.items():
            if f_md5.endswith('00000000') and b_md5.startswith(f_md5.rstrip('0')):
                matched_file = f"{fname} (partial match)"
                break
    print(f"  Block {idx:2d}: size={archive.block_table[idx].size:<6} md5={b_md5} -> {matched_file}")
