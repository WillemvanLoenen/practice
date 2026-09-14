from board import Cell, CellState

# TODO: 
# take into account number of remaining mines for resolving last mines if possible
# prompt when game can't be solved with certainty
# add docstrings
# add function annotation
# check for wrong flags (possibly by keeping track of all mines in grid)
# queue class
# optional: only communicate newly revealed cells instead of the whole grid


class Cluster:
    def __init__(self, x: int, y: int, mine_count: int):
        self.x = x
        self.y = y
        self._mine_count = mine_count
        self.cells = {}
    
    def check(self):
        if not self.cells:
            return None, None

        self._clean()
        return self._resolve_safe(), self._resolve_mine()

    def combine(self, other):
        if self.cells.isdisjoint(other.cells):
            return None, None

        if other.cells.issubset(self.cells):
            self.cells -= other.cells
            self._mine_count -= other._mine_count
            return self._resolve_safe(), self._resolve_mine()

        elif self.cells.issubset(other.cells):
            other.cells -= self.cells
            other._mine_count -= self._mine_count
            return other._resolve_safe(), other._resolve_mine()

        elif self._mine_count == other._mine_count - len(other.cells - self.cells):
            safe = self.cells - other.cells
            mine = other.cells - self.cells
            self.cells &= other.cells
            other.cells.clear()
            other._mine_count = 0
            for cell in mine:
                cell.is_mine = True
            return safe, mine

        elif other._mine_count == self._mine_count - len(self.cells - other.cells):
            safe = other.cells - self.cells
            mine = self.cells - other.cells
            other.cells &= self.cells
            self.cells.clear()
            self._mine_count = 0
            for cell in mine:
                cell.is_mine = True
            return safe, mine
        
        return None, None

    def _clean(self):
        self.cells = set(filter(
            lambda cell: cell.state != CellState.REVEALED,
            self.cells
        ))
        for cell in list(self.cells):
            if cell.is_mine:
                self._mine_count -= 1
                self.cells.remove(cell)

    def _resolve_safe(self):
        if self._mine_count == 0:
            safe = self.cells.copy()
            self.cells.clear()
            return safe

    def _resolve_mine(self):
        if 0 < self._mine_count == len(self.cells):
            mine = self.cells.copy()
            for cell in mine:
                cell.is_mine = True
            self.cells.clear()
            return mine

    
class Solver():
    def __init__(self, width, height, num_mines, grid=None, flag=True):
        self.width = width
        self.height = height
        self.num_mines = num_mines
       
        self.flag = flag
        self.reveal_queue = []
        self.flag_queue = []

        self.clusters = [[None for x in range(width)] for y in range(height)]
        self.grid = [[Cell(x, y) for x in range(width)] for y in range(height)]
        self._update_grid(grid)
        self._check_flags()
        self._gen_check_clusters = self._check_clusters()

        game_started = False
        for row in self.grid:
            for cell in row:
                if cell.state == CellState.REVEALED:
                    game_started = True
        if game_started:
            next(self._gen_check_clusters)
        else:
            self.reveal_queue.append(self.grid[height//2][width//2])

    def __iter__(self):
        while True:

            while self.flag and self.flag_queue:
                if self.flag_queue[0].state == CellState.FLAGGED:
                    del self.flag_queue[0]
                else:
                    grid = yield self.flag_queue.pop(0), True
                    self._update_grid(grid)

            while self.reveal_queue:
                if self.reveal_queue[0].state == CellState.HIDDEN:
                    grid = yield self.reveal_queue.pop(0), False
                    self._update_grid(grid)
                elif self.reveal_queue[0].state == CellState.FLAGGED:
                    yield self.reveal_queue[0], True
                elif self.reveal_queue[0].state == CellState.REVEALED:
                    del self.reveal_queue[0]

            try:
                next(self._gen_check_clusters)
            except StopIteration:
                self._check_remaining_mines()
                break

    # TODO every .combine() to include .check() for cleaner code?
    # change implementation after setting up queue class
    def _check_clusters(self):
        exhausted = False
        while not exhausted:
            exhausted = True
            for row in self.clusters:
                for cluster in row:

                    if cluster:
                        safe, mine = cluster.check()
                        if safe:
                            exhausted = False
                            yield self.reveal_queue.extend(safe)
                        if mine and self.flag:
                            exhausted = False
                            yield self.flag_queue.extend(mine)

                        for neighbour in self._neighbour_clusters(cluster):

                            safe, mine = neighbour.check()
                            if safe:
                                exhausted = False
                                yield self.reveal_queue.extend(safe)
                            if mine and self.flag:
                                exhausted = False
                                yield self.flag_queue.extend(mine)

                            safe, mine = cluster.check()
                            if safe:
                                exhausted = False
                                yield self.reveal_queue.extend(safe)
                            if mine and self.flag:
                                exhausted = False
                                yield self.flag_queue.extend(mine)

                            safe, mine = cluster.combine(neighbour)
                            if safe:
                                exhausted = False
                                yield self.reveal_queue.extend(safe)
                            if mine and self.flag:
                                exhausted = False
                                yield self.flag_queue.extend(mine)

    def _init_cluster(self, x: int, y: int, adjacent_count: int):
        self.clusters[y][x] = Cluster(x, y, adjacent_count)
        self.clusters[y][x].cells = {
            self.grid[ny][nx] for nx, ny in self._neighbour_cells(x, y)
            if self.grid[ny][nx].state != CellState.REVEALED
        }

    def _neighbour_cells(self, x: int, y: int):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if self._in_bounds(nx, ny):
                    yield nx, ny
                    
    def _neighbour_clusters(self, cluster):
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = cluster.x + dx, cluster.y + dy
                if self._in_bounds(nx, ny) and self.clusters[ny][nx]:
                    yield self.clusters[ny][nx]

    def _in_bounds(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def _update_grid(self, grid):
        for y, row in enumerate(grid):
            for x, cell in enumerate(row):

                if cell.state == CellState.FLAGGED:
                    self.grid[y][x].state = CellState.FLAGGED
                elif (cell.state == CellState.REVEALED
                      and self.grid[y][x].state != CellState.REVEALED):
                    self.grid[y][x].state = CellState.REVEALED
                    self.grid[y][x].adjacent_count = cell.adjacent_count
                    self._init_cluster(x, y, cell.adjacent_count)

    def _check_flags(self):
        pass

    def _check_remaining_mines(self):
        pass
