#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=========================================================
BSP Dungeon Generator (Binary Space Partitioning)
=========================================================
Génère un donjon procédural avec :
- Découpage binaire récursif de la carte
- Placement de salles rectangulaires
- Connexion par couloirs perpendiculaires (orthogonaux)
- Sortie ASCII

Auteur : ChatGPT (GPT-5)
Version : 1.0
=========================================================
"""

import random
import numpy as np
from dataclasses import dataclass
from typing import Optional, List, Tuple

# ========================================================
# Paramètres principaux
# ========================================================
WIDTH, HEIGHT = 120, 80       # taille de la grille (en tiles)
N_POINTS = 30                 # non utilisé ici, mais pourrait servir à limiter le nombre de salles
ROOM_RADIUS_MIN = 3           # dimensions minimales des salles
ROOM_RADIUS_MAX = 7           # dimensions maximales des salles
SEED = 56                     # graine aléatoire fixe
SEED = random.randint(0, 100)
random.seed(SEED)
np.random.seed(SEED)

# ========================================================
# Structures de données
# ========================================================

@dataclass
class BSPNode:
    """Représente un noeud dans l'arbre BSP."""
    x: int
    y: int
    w: int
    h: int
    left: Optional['BSPNode'] = None
    right: Optional['BSPNode'] = None
    room: Optional[Tuple[int, int, int, int]] = None  # (x, y, w, h)

    def is_leaf(self) -> bool:
        return self.left is None and self.right is None


# ========================================================
# Fonctions principales de génération
# ========================================================

def split_node(node: BSPNode, min_size: int) -> bool:
    """
    Tente de scinder un noeud en deux sous-régions.
    Retourne True si la scission a eu lieu.
    """
    if not node.is_leaf():
        return False

    # Choisir orientation selon proportions
    split_horizontally = random.random() > 0.5
    if node.w / node.h >= 1.25:
        split_horizontally = False
    elif node.h / node.w >= 1.25:
        split_horizontally = True

    if split_horizontally:
        max_split = node.h - min_size * 2
        if max_split <= 0:
            return False
        split = random.randint(min_size, node.h - min_size)
        node.left = BSPNode(node.x, node.y, node.w, split)
        node.right = BSPNode(node.x, node.y + split, node.w, node.h - split)
    else:
        max_split = node.w - min_size * 2
        if max_split <= 0:
            return False
        split = random.randint(min_size, node.w - min_size)
        node.left = BSPNode(node.x, node.y, split, node.h)
        node.right = BSPNode(node.x + split, node.y, node.w - split, node.h)

    return True


def split_recursive(node: BSPNode, min_size: int, depth: int):
    """
    Divise récursivement un noeud BSP jusqu'à une certaine profondeur.
    """
    if depth <= 0:
        return
    if split_node(node, min_size):
        split_recursive(node.left, min_size, depth - 1)
        split_recursive(node.right, min_size, depth - 1)


def create_rooms(node: BSPNode):
    """
    Place des salles dans chaque feuille (rectangle terminal).
    """
    if node.is_leaf():
        rw = random.randint(ROOM_RADIUS_MIN * 2, min(node.w - 2, ROOM_RADIUS_MAX * 2))
        rh = random.randint(ROOM_RADIUS_MIN * 2, min(node.h - 2, ROOM_RADIUS_MAX * 2))
        rx = random.randint(node.x + 1, node.x + node.w - rw - 1)
        ry = random.randint(node.y + 1, node.y + node.h - rh - 1)
        node.room = (rx, ry, rw, rh)
    else:
        if node.left:
            create_rooms(node.left)
        if node.right:
            create_rooms(node.right)


def get_rooms(node: BSPNode) -> List[Tuple[int, int, int, int]]:
    """Récupère toutes les salles de l'arbre BSP."""
    if node.is_leaf():
        return [node.room] if node.room else []
    rooms = []
    if node.left:
        rooms.extend(get_rooms(node.left))
    if node.right:
        rooms.extend(get_rooms(node.right))
    return rooms


# ========================================================
# Connexion des salles
# ========================================================

def room_center(room: Tuple[int, int, int, int]) -> Tuple[int, int]:
    x, y, w, h = room
    return (x + w // 2, y + h // 2)


def connect_rooms(node: BSPNode, grid: List[List[int]]):
    """
    Connecte récursivement les sous-régions de l'arbre BSP.
    Chaque noeud interne relie le centre d'une salle à gauche et à droite.
    """
    if node.left and node.right:
        connect_rooms(node.left, grid)
        connect_rooms(node.right, grid)

        c1 = find_room_center(node.left)
        c2 = find_room_center(node.right)
        if c1 and c2:
            carve_corridor(grid, c1, c2)


def find_room_center(node: BSPNode) -> Optional[Tuple[int, int]]:
    """Retourne le centre d'une salle dans le sous-arbre."""
    if node.is_leaf() and node.room:
        return room_center(node.room)
    left = find_room_center(node.left) if node.left else None
    right = find_room_center(node.right) if node.right else None
    return left or right


def carve_corridor(grid: List[List[int]], c1: Tuple[int, int], c2: Tuple[int, int]):
    """
    Creuse un couloir perpendiculaire (orthogonal) entre deux points.
    """
    x1, y1 = c1
    x2, y2 = c2

    if random.random() < 0.5:
        # d'abord horizontal, puis vertical
        carve_line(grid, x1, x2, y1, horizontal=True)
        carve_line(grid, y1, y2, x2, horizontal=False)
    else:
        # d'abord vertical, puis horizontal
        carve_line(grid, y1, y2, x1, horizontal=False)
        carve_line(grid, x1, x2, y2, horizontal=True)


def carve_line(grid: List[List[int]], a: int, b: int, fixed: int, horizontal=True):
    """
    Creuse une ligne droite horizontale ou verticale.
    """
    for v in range(min(a, b), max(a, b) + 1):
        if horizontal:
            grid[fixed][v] = 1
        else:
            grid[v][fixed] = 1


# ========================================================
# Construction de la carte
# ========================================================

def carve_rooms(grid: List[List[int]], rooms: List[Tuple[int, int, int, int]]):
    """Creuse les salles dans la grille."""
    for (x, y, w, h) in rooms:
        for j in range(y, y + h):
            for i in range(x, x + w):
                grid[j][i] = 1


def print_ascii(grid: List[List[int]]):
    """Affichage ASCII de la carte."""
    for row in grid:
        print("".join("." if c == 1 else "#" for c in row))


# ========================================================
# Génération complète
# ========================================================

def generate_bsp_dungeon(width=WIDTH, height=HEIGHT, depth=6, min_leaf=15):
    """Fonction principale de génération du donjon BSP."""
    grid = [[0 for _ in range(width)] for _ in range(height)]
    root = BSPNode(0, 0, width, height)

    split_recursive(root, min_leaf, depth)
    create_rooms(root)
    rooms = get_rooms(root)

    carve_rooms(grid, rooms)
    connect_rooms(root, grid)

    return grid, rooms


# ========================================================
# Exemple d’exécution
# ========================================================

if __name__ == "__main__":
    grid, rooms = generate_bsp_dungeon()

    print(f"Salles générées : {len(rooms)}")
    print("Centres :", [room_center(r) for r in rooms])
    print("\nCarte générée :\n")
    print_ascii(grid)