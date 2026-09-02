import sc2reader

class MockReplay:
    build = 96999
    base_build = 96999

def view_left_p2():
    with open('extracted_replay/replay.tracker.events', 'rb') as f:
        data = f.read()
    events = sc2reader.readers.TrackerEventsReader()(data, MockReplay())
    
    # Filter Player 2 units
    coords = set((ev.x, ev.y) for ev in events if ev.__class__.__name__ == 'UnitBornEvent' and ev.control_pid == 2)
    
    # X in [60, 150], Y in [50, 100]
    min_x, max_x = 60, 150
    min_y, max_y = 50, 100
    
    grid = [[' ' for _ in range(max_x - min_x + 1)] for _ in range(max_y - min_y + 1)]
    for x, y in coords:
        if min_x <= x <= max_x and min_y <= y <= max_y:
            grid[y - min_y][x - min_x] = '#'
            
    print("Player 2 Spawn Grid (Left Part X=[60, 150]):")
    for row in reversed(grid):
        print("".join(row))

view_left_p2()
