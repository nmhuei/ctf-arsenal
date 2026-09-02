import mpyq
import os

replay_path = 'misc_deadgame2/DeadGame2.SC2Replay'
archive = mpyq.MPQArchive(replay_path)
output_dir = 'extracted_replay'

os.makedirs(output_dir, exist_ok=True)

for filename in archive.files:
    name_str = filename.decode('utf-8')
    try:
        data = archive.read_file(filename)
        if data is None:
            print(f"Warning: {name_str} returned None")
            continue
        with open(os.path.join(output_dir, name_str), 'wb') as f:
            f.write(data)
        print(f"Extracted {name_str} successfully.")
    except Exception as e:
        print(f"Failed to extract {name_str}: {e}")

print("Extraction complete.")
