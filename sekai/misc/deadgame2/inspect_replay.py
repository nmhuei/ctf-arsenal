import mpyq

replay_path = 'misc_deadgame2/DeadGame2.SC2Replay'
archive = mpyq.MPQArchive(replay_path)

print("Files in archive:")
for filename in archive.files:
    print(filename)
