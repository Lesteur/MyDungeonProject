from random import random

# Taille du donjon
width, height = 60, 30

# Paramètres
prob_wall = 0.45
iterations = 6

# Initialisation aléatoire
grid = [[1 if random() < prob_wall else 0 for x in range(width)] for y in range(height)]

# Fonction pour compter les voisins "mur"
def count_walls(grid, x, y):
    count = 0
    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if nx < 0 or nx >= width or ny < 0 or ny >= height:
                count += 1  # Bords considérés comme murs
            elif grid[ny][nx] == 1:
                count += 1
    return count

def flood_fill(grid, x, y):
    to_fill = [(x, y)]
    visited = set()
    cells = []
    while to_fill:
        cx, cy = to_fill.pop()
        if (cx, cy) in visited:
            continue
        visited.add((cx, cy))
        if grid[cy][cx] == 0:
            cells.append((cx, cy))
            for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < width and 0 <= ny < height:
                    to_fill.append((nx, ny))
    return cells

def carve_corridor(grid, x1, y1, x2, y2):
    # On trace d'abord horizontalement, puis verticalement
    for x in range(min(x1, x2), max(x1, x2) + 1):
        grid[y1][x] = 0
    for y in range(min(y1, y2), max(y1, y2) + 1):
        grid[y][x2] = 0

# Simulation
for i in range(iterations):
    new_grid = [[0 for x in range(width)] for y in range(height)]
    for y in range(height):
        for x in range(width):
            walls = count_walls(grid, x, y)
            if grid[y][x] == 1:
                new_grid[y][x] = 1 if walls >= 4 else 0
            else:
                new_grid[y][x] = 1 if walls >= 5 else 0
    grid = new_grid

cells = flood_fill(grid, 15, 15)

# Afficher le labyrinthe
for row in grid:
    print(''.join(['#' if cell == 1 else '.' for cell in row]))