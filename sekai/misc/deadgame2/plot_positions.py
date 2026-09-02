import sc2reader
import matplotlib.pyplot as plt

class MockReplay:
    build = 96999
    base_build = 96999

def plot_positions(path):
    with open(path, 'rb') as f:
        data = f.read()
        
    from sc2reader.readers import TrackerEventsReader
    reader = TrackerEventsReader()
    replay = MockReplay()
    events = reader(data, replay)
    
    # Extract coordinates
    p1_x, p1_y = [], []
    p2_x, p2_y = [], []
    neutral_x, neutral_y = [], []
    
    for ev in events:
        if ev.__class__.__name__ == 'UnitBornEvent':
            if ev.control_pid == 1:
                p1_x.append(ev.x)
                p1_y.append(ev.y)
            elif ev.control_pid == 2:
                p2_x.append(ev.x)
                p2_y.append(ev.y)
            else:
                neutral_x.append(ev.x)
                neutral_y.append(ev.y)
                
    # Plot Player 1
    plt.figure(figsize=(10, 10))
    plt.scatter(p1_x, p1_y, c='red', s=10)
    plt.title('Player 1 Unit Born Positions')
    plt.grid(True)
    plt.savefig('scripts/player1_spawn.png')
    plt.close()
    
    # Plot Player 2
    plt.figure(figsize=(10, 10))
    plt.scatter(p2_x, p2_y, c='blue', s=10)
    plt.title('Player 2 Unit Born Positions')
    plt.grid(True)
    plt.savefig('scripts/player2_spawn.png')
    plt.close()
    
    print("Plots saved successfully.")

plot_positions('extracted_replay/replay.tracker.events')
