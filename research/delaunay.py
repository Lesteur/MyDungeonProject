#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
delaunay_dungeon.py
Exemple : points -> triangulation de Delaunay -> MST -> carve rooms & corridors sur une grille.
"""

import numpy as np
from scipy.spatial import Delaunay
import networkx as nx
import matplotlib.pyplot as plt
import random
from math import floor, ceil

# Paramètres
WIDTH, HEIGHT = 120, 80       # taille de la grille en tiles
N_POINTS = 30                 # nombre de centres de salles
ROOM_RADIUS_MIN = 3
ROOM_RADIUS_MAX = 7
SEED = np.random.randint(0, 100)
random.seed(SEED)
np.random.seed(SEED)

# 1) Générer des points (centres de salles) avec rejet si trop proche (simple poisson-disk style)
def generate_points(n, w, h, min_dist=6, attempts=2000):
    pts = []
    tries = 0
    while len(pts) < n and tries < attempts:
        x = random.uniform(5, w-6)
        y = random.uniform(5, h-6)
        ok = True
        for (px,py) in pts:
            if (px-x)**2 + (py-y)**2 < min_dist**2:
                ok = False
                break
        if ok:
            pts.append((x,y))
        tries += 1
    return np.array(pts)

points = generate_points(N_POINTS, WIDTH, HEIGHT, min_dist=6)

# 2) Triangulation de Delaunay
tri = Delaunay(points)
edges = set()
for simplex in tri.simplices:
    # simplex contient indices des 3 sommets du triangle
    for i in range(3):
        a = simplex[i]
        b = simplex[(i+1)%3]
        edge = tuple(sorted((int(a), int(b))))
        edges.add(edge)
edges = list(edges)

# 3) Construire graphe et MST
G = nx.Graph()
for i, p in enumerate(points):
    G.add_node(i, pos=tuple(p))

for (a,b) in edges:
    pa = points[a]
    pb = points[b]
    dist = np.linalg.norm(pa-pb)
    G.add_edge(a,b,weight=dist)

mst = nx.minimum_spanning_tree(G, weight='weight')

# Ajouter quelques arêtes supplémentaires (pour cycles)
G_extra = nx.Graph(mst)
extra_edges = []
for (a,b) in G.edges():
    if not mst.has_edge(a,b) and random.random() < 0.15:  # 15% chance d'ajout
        G_extra.add_edge(a,b, weight=G[a][b]['weight'])
        extra_edges.append((a,b))

# 4) Grille tilemap initialement pleine (1=wall, 0=floor)
grid = [[1 for _ in range(WIDTH)] for __ in range(HEIGHT)]

# Helper : carve circular room
def carve_circle(grid, cx, cy, r):
    for ix in range(int(cx-r)-1, int(cx+r)+2):
        for iy in range(int(cy-r)-1, int(cy+r)+2):
            if 0 <= ix < WIDTH and 0 <= iy < HEIGHT:
                if (ix-cx)**2 + (iy-cy)**2 <= r*r:
                    grid[iy][ix] = 0

# Carver salles
room_radii = []
for i,(x,y) in enumerate(points):
    r = random.randint(ROOM_RADIUS_MIN, ROOM_RADIUS_MAX)
    room_radii.append(r)
    carve_circle(grid, x, y, r)

# Bresenham line pour couloirs orthogonaux simple
def bresenham_line(x0,y0,x1,y1):
    x0, y0, x1, y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
    points = []
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        points.append((x0,y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy
    return points

# Carver couloirs selon les arêtes du graphe G_extra (MST+quelques extras)
for a,b in G_extra.edges():
    ax, ay = points[a]
    bx, by = points[b]
    # Ligne droite (Bresenham). On peut embellir avec corridors épais.
    line = bresenham_line(ax, ay, bx, by)
    for (lx,ly) in line:
        # largeur de corridor
        for dx in (-1,0,1):
            for dy in (-1,0,1):
                x = lx + dx
                y = ly + dy
                if 0 <= x < WIDTH and 0 <= y < HEIGHT:
                    grid[y][x] = 0

# 5) Visualisation simple
fig, ax = plt.subplots(figsize=(10,7))
ax.imshow(grid, cmap='gray_r', origin='lower')

# afficher centres et arêtes
"""
pts = np.array(points)
ax.scatter(pts[:,0], pts[:,1], c='red', s=20)

for (a,b) in G_extra.edges():
    pa = points[a]; pb = points[b]
    ax.plot([pa[0], pb[0]], [pa[1], pb[1]], c='yellow', linewidth=0.6, alpha=0.6)
"""

ax.set_title("Donjon via Delaunay -> MST + corridors")
plt.show()