import sc2reader

class MockReplay:
    build = 96999
    base_build = 96999

def view_right_p2():
    with open('extracted_replay/replay.tracker.events', 'rb') as f:
        data = f.read()
    events = sc2reader.readers.TrackerEventsReader()(data, MockReplay())
    
    # Filter Player 2 units
    coords = set((ev.x, ev.y) for ev in events if ev.__class__.__name__ == 'UnitBornEvent' and ev.control_pid == 2)
    
    # We want to look at X in [150, 204], Y in [52, 95]
    min_x, max_x = 150, 204
    min_y, max_y = 52, 95
    
    grid = [[' ' for _ in range(max_x - min_x + 1)] for _ in range(max_y - min_y + 1)]
    for x, y in coords:
        if min_x <= x <= max_x and min_y <= y <= max_y:
            grid[y - min_y][x - min_x] = '#'
            
    print("Player 2 Spawn Grid (Right Part X=[150, 204]):")
    for row in reversed(grid):
        print("".join(row))

view_right_p2()
