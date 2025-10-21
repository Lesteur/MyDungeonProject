#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=========================================================
Dungeon Generator
=========================================================
Generates a procedural dungeon using various algorithms.

Author : Adam Ibn
Version : 1.0
=========================================================
"""

import random
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Optional, List, Tuple

# ========================================================
# Principal Parameters
# ========================================================
WIDTH, HEIGHT = 120, 80       # Size of the grid (in tiles)
N_POINTS = 30                 # Not used here, but could be used to limit the number of rooms
ROOM_RADIUS_MIN = 3           # Minimum room dimensions
ROOM_RADIUS_MAX = 7           # Maximum room dimensions
SEED = 56                     # Fixed random seed
SEED = random.randint(0, 100)
random.seed(SEED)
np.random.seed(SEED)

@dataclass
class Room:
    x: int
    y: int
    w: int
    h: int

    def center(self) -> Tuple[int, int]:
        return (self.x + self.w // 2, self.y + self.h // 2)


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


grid = [[0 for _ in range(WIDTH)] for __ in range(HEIGHT)]

grid[0][0] = 1

fig, ax = plt.subplots(figsize=(10,7))
ax.imshow(grid, cmap='gray_r', origin='lower')
ax.set_title("Dungeon")
plt.show()