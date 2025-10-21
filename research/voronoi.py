"""
voronoi_dungeon.py
Exemple : points -> diagramme de Voronoï -> clip to bbox -> utiliser arêtes Voronoï pour corridors
"""

import numpy as np
from scipy.spatial import Voronoi
import matplotlib.pyplot as plt
import math
import random
from shapely.geometry import LineString, box, Polygon, Point
from shapely.ops import unary_union

# Dépendance optionnelle : shapely pour le clipping pratique
# pip install shapely

WIDTH, HEIGHT = 120, 80
N_POINTS = 25
SEED = 123
random.seed(SEED)
np.random.seed(SEED)

# Générer points
points = np.column_stack((
    np.random.uniform(5, WIDTH-6, size=N_POINTS),
    np.random.uniform(5, HEIGHT-6, size=N_POINTS)
))

# Construire Voronoi
vor = Voronoi(points)

# Bounding box pour clipper les régions infinies
bbox = box(0, 0, WIDTH-1, HEIGHT-1)

# Récupérer arêtes finies du diagramme Voronoi et clipper
lines = []
for (v1, v2) in vor.ridge_vertices:
    if v1 >= 0 and v2 >= 0:
        p1 = vor.vertices[v1]
        p2 = vor.vertices[v2]
        line = LineString([tuple(p1), tuple(p2)])
        clipped = line.intersection(bbox)
        if not clipped.is_empty:
            # clipping peut renvoyer LineString ou MultiLineString
            if clipped.geom_type == 'LineString':
                lines.append(clipped)
            else:
                for g in clipped:
                    if g.length > 0:
                        lines.append(g)

# Visualisation des arêtes Voronoi (clippées)
fig, ax = plt.subplots(figsize=(10,7))
for ln in lines:
    xs, ys = ln.xy
    ax.plot(xs, ys, color='gray', linewidth=1)
ax.scatter(points[:,0], points[:,1], c='red')
ax.set_xlim(0, WIDTH); ax.set_ylim(0, HEIGHT)
ax.set_title("Arêtes Voronoï (clippées) — utilisables comme corridors médians")
plt.gca().set_aspect('equal', adjustable='box')
plt.show()

# Exemple d'utilisation pratique :
#  - pour chaque arête Voronoi, si elle sépare deux sites, on peut considérer creuser un couloir le long de cette arête
#  - ou bien construire un graphe dual (les régions = nœuds) et relier régions adjacentes selon les ridges

# Construire graphe dual : nœuds = indices des points, arêtes = ridges (clippées)
import networkx as nx
G = nx.Graph()
for i in range(len(points)):
    G.add_node(i, pos=tuple(points[i]))

# vor.ridge_points contient paires d'indices de sites séparés par la ridge_vertices correspondante
for (p1, p2), (v1, v2) in zip(vor.ridge_points, vor.ridge_vertices):
    # Si la ridge a une représentation finie (v1>=0 and v2>=0) ou partiellement finie après clipping,
    # on peut ajouter une arête p1-p2 pondérée par la distance entre sites
    dist = np.linalg.norm(points[p1] - points[p2])
    G.add_edge(p1, p2, weight=dist)

# On peut alors prendre un MST sur ce graphe (ou laisser la topologie originale)
mst = nx.minimum_spanning_tree(G)

# Visualiser MST over points
fig, ax = plt.subplots(figsize=(10,7))
ax.scatter(points[:,0], points[:,1], c='red')
for (a,b) in mst.edges():
    pa = points[a]; pb = points[b]
    ax.plot([pa[0], pb[0]], [pa[1], pb[1]], c='blue', linewidth=1.2)
# aussi montrer quelques arêtes Voronoi
for ln in lines:
    xs, ys = ln.xy
    ax.plot(xs, ys, color='gray', linewidth=0.8, alpha=0.6)

ax.set_xlim(0, WIDTH); ax.set_ylim(0, HEIGHT)
ax.set_title("Voronoï + MST (connexion minimale des sites)")
plt.gca().set_aspect('equal', adjustable='box')
plt.show()