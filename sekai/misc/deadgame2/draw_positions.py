import sc2reader

class MockReplay:
    build = 96999
    base_build = 96999

def draw_positions(path):
    with open(path, 'rb') as f:
        data = f.read()
        
    from sc2reader.readers import TrackerEventsReader
    reader = TrackerEventsReader()
    replay = MockReplay()
    events = reader(data, replay)
    
    with open('scripts/spawn_grid.txt', 'w') as out_f:
        for pid in (1, 2):
            x_coords = []
            y_coords = []
            for ev in events:
                if ev.__class__.__name__ == 'UnitBornEvent' and ev.control_pid == pid:
                    x_coords.append(ev.x)
                    y_coords.append(ev.y)
            if not x_coords:
                continue
            min_x, max_x = min(x_coords), max(x_coords)
            min_y, max_y = min(y_coords), max(y_coords)
            out_f.write(f"Player {pid}: X range [{min_x}, {max_x}], Y range [{min_y}, {max_y}], Unique points: {len(set(zip(x_coords, y_coords)))}\n")
            
            coords = set(zip(x_coords, y_coords))
            grid = [[' ' for _ in range(max_x - min_x + 1)] for _ in range(max_y - min_y + 1)]
            for x, y in coords:
                grid[y - min_y][x - min_x] = '#'
            out_f.write(f"ASCII Grid for Player {pid}:\n")
            for row in reversed(grid):
                out_f.write("".join(row) + "\n")
            out_f.write("\n" + "="*50 + "\n\n")

draw_positions('extracted_replay/replay.tracker.events')
