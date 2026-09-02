import sc2reader
import traceback

replay_path = 'misc_deadgame2/DeadGame2.SC2Replay'
try:
    replay = sc2reader.load_replay(replay_path, load_level=0)
except Exception as e:
    traceback.print_exc()
