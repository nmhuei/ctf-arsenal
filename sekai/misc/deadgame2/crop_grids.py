def crop_grid(filename, player_label):
    with open(filename, 'r') as f:
        content = f.read()
        
    parts = content.split("==================================================")
    part = None
    for p in parts:
        if player_label in p:
            part = p
            break
            
    if not part:
        print(f"Label {player_label} not found")
        return
        
    lines = part.strip().split('\n')
    grid_lines = []
    start = False
    for line in lines:
        if "ASCII Grid" in line:
            start = True
            continue
        if start:
            grid_lines.append(line)
            
    # Remove empty outer rows and columns
    # Find min/max row/col with '#'
    non_empty_rows = []
    for r_idx, row in enumerate(grid_lines):
        if '#' in row:
            non_empty_rows.append(r_idx)
            
    if not non_empty_rows:
        print("No '#' found in grid")
        return
        
    min_row, max_row = min(non_empty_rows), max(non_empty_rows)
    
    non_empty_cols = []
    for c_idx in range(len(grid_lines[0])):
        col_has_hash = False
        for r_idx in range(min_row, max_row + 1):
            if c_idx < len(grid_lines[r_idx]) and grid_lines[r_idx][c_idx] == '#':
                col_has_hash = True
                break
        if col_has_hash:
            non_empty_cols.append(c_idx)
            
    min_col, max_col = min(non_empty_cols), max(non_empty_cols)
    
    print(f"\nCropped grid for {player_label}:")
    for r_idx in range(min_row, max_row + 1):
        row = grid_lines[r_idx]
        cropped_row = row[min_col:max_col+1]
        # pad if shorter
        cropped_row = cropped_row.ljust(max_col - min_col + 1)
        print(cropped_row)

crop_grid('scripts/spawn_grid.txt', 'Player 1')
crop_grid('scripts/spawn_grid.txt', 'Player 2')
