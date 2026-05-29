from collections import deque
from typing import List, Optional, Tuple, Dict


Cell = Tuple[int, int]  # (x, y)


class GridRoutingEngine:
    def __init__(self, grid: List[List[int]]):
        """
        grid[y][x] = 0 libero, 1 bloccato
        """
        self.grid = grid
        self.height = len(grid)
        self.width = len(grid[0]) if self.height > 0 else 0

        # cache: (start, goal) -> distance | None
        self._dist_cache: Dict[Tuple[Cell, Cell], Optional[int]] = {}

    def _in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def _is_free(self, x: int, y: int) -> bool:
        if not self._in_bounds(x, y):
            return False
        return self.grid[y][x] == 0

    def _neighbors_4(self, x: int, y: int):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if self._is_free(nx, ny):
                yield nx, ny

    def shortest_path_distance(self, start: Cell, goal: Cell) -> Optional[int]:
        key = (start, goal)
        if key in self._dist_cache:
            return self._dist_cache[key]

        sx, sy = start
        gx, gy = goal

        # start/goal su celle bloccate => no route
        if not self._is_free(sx, sy) or not self._is_free(gx, gy):
            self._dist_cache[key] = None
            return None

        if start == goal:
            self._dist_cache[key] = 0
            return 0

        # BFS: costo uniforme 1 per passo
        q = deque()
        q.append(start)
        dist: Dict[Cell, int] = {start: 0}

        while q:
            cx, cy = q.popleft()
            cd = dist[(cx, cy)]

            for nx, ny in self._neighbors_4(cx, cy):
                ncell = (nx, ny)
                if ncell in dist:
                    continue
                dist[ncell] = cd + 1
                if ncell == goal:
                    self._dist_cache[key] = dist[ncell]
                    return dist[ncell]
                q.append(ncell)

        self._dist_cache[key] = None
        return None
