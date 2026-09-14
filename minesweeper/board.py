#!/usr/bin/env python3

"""
A mineswiper game playable from the CLI,
and accessible by GUI applications.

To create a game:
    Board(width, height, num_mines)

To play the game:
    Board.reveal(x, y)
    Board.toggle_flag(x, y)

Additional setting:
    Board.auto_resolve_flags = False
"""

import random
from dataclasses import dataclass
from enum import Enum, auto


class CellState(Enum):
    HIDDEN = auto()
    REVEALED = auto()
    FLAGGED = auto()


class GameState(Enum):
    PLAYING = auto()
    WON = auto()
    LOST = auto()


@dataclass
class Cell:
    x: int
    y: int
    is_mine: bool = False
    state: CellState = CellState.HIDDEN
    adjacent_count: int = 0
    adjacent_flag: int = 0

    def __eq__(self, other) -> bool:
        if not isinstance(other, Cell):
            return False
        return self.x == other.x and self.y == other.y

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __repr__(self) -> str:
        if self.state == CellState.HIDDEN:
            return "#"
        if self.state == CellState.FLAGGED:
            return "F"
        return "*" if self.is_mine else str(self.adjacent_count)


class Board:
    def __init__(self, width: int, height: int, num_mines: int):
        self.width = width
        self.height = height
        self.num_mines = num_mines
        self.state = GameState.PLAYING
        self._mines_placed = False
        self.auto_resolve_flags = False

        self.grid = [[Cell(x, y) for x in range(width)] for y in range(height)]

    def _in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def _neighbours(self, x: int, y: int):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if self._in_bounds(nx, ny):
                    yield nx, ny

    def _place_mines(self, safe_x: int, safe_y: int):
        """Place mines randomly, avoiding the first-clicked cell and its neighbours."""
        forbidden = {(safe_x, safe_y)} | set(self._neighbours(safe_x, safe_y))
        all_positions = [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if (x, y) not in forbidden
        ]
        mine_positions = random.sample(all_positions, self.num_mines)

        for x, y in mine_positions:
            self.grid[y][x].is_mine = True

        self._compute_adjacent_counts()
        self._mines_placed = True

    def _compute_adjacent_counts(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x].is_mine:
                    continue
                count = sum(
                    1 for nx, ny in self._neighbours(x, y)
                    if self.grid[ny][nx].is_mine
                )
                self.grid[y][x].adjacent_count = count

    def _compute_adjacent_flags(self, x: int, y: int):
        count = sum(
            1 for nx, ny in self._neighbours(x, y) 
            if self.grid[ny][nx].state == CellState.FLAGGED
        )
        self.grid[y][x].adjacent_flag = count

    def reveal(self, x: int, y: int):
        if self.state != GameState.PLAYING:
            return

        cell = self.grid[y][x]
        if cell.state == CellState.FLAGGED:
            return

        if cell.state == CellState.REVEALED:
            if cell.adjacent_count - cell.adjacent_flag == 0:
                for nx, ny in self._neighbours(x, y):
                    self._flood_reveal(nx, ny)

        if cell.state == CellState.HIDDEN:
            if not self._mines_placed:
                self._place_mines(x, y)

            if cell.is_mine:
                cell.state = CellState.REVEALED
                self.state = GameState.LOST
                return

            self._flood_reveal(x, y)

        self._check_win()

    def _resolve_flag(self, x: int, y: int):
        cell = self.grid[y][x]
        if cell.state != CellState.REVEALED:
            return

        if cell.adjacent_count - cell.adjacent_flag == 0:
            for nx, ny in self._neighbours(x, y):
                self._flood_reveal(nx, ny)

    def _flood_reveal(self, x: int, y: int):
        """Reveal (x, y), and if it has no adjacent mines, recursively reveal neighbours."""
        cell = self.grid[y][x]
        if cell.state != CellState.HIDDEN:
            return

        cell.state = CellState.REVEALED
        if cell.is_mine:
            self.state = GameState.LOST
            return
            
        if cell.adjacent_count - self.auto_resolve_flags * cell.adjacent_flag == 0:
            for nx, ny in self._neighbours(x, y):
                self._flood_reveal(nx, ny)

    def toggle_flag(self, x: int, y: int):
        if self.state != GameState.PLAYING:
            return

        cell = self.grid[y][x]
        if cell.state == CellState.REVEALED:
            return
        elif cell.state == CellState.HIDDEN:
            cell.state = CellState.FLAGGED
        elif cell.state == CellState.FLAGGED:
            cell.state = CellState.HIDDEN
     
        for nx, ny in self._neighbours(x, y):
            self._compute_adjacent_flags(nx, ny)
            if self.auto_resolve_flags:
                self._resolve_flag(nx, ny)
                self._check_win()

    def _check_win(self):
        for row in self.grid:
            for cell in row:
                if not cell.is_mine and cell.state != CellState.REVEALED:
                    return
        self.state = GameState.WON

    def __repr__(self) -> str:
        lines = []
        lines.append("    " + " ".join((str(i) for i in range(self.width))))
        lines.append("\n   " + "-" * 2 * self.width)
        for idx, row in enumerate(self.grid):
            lines.append(f"\n{idx} | " + " ".join(repr(cell) for cell in row))
        return "".join(lines)


def main():
    width = int(input("width: "))
    height = int(input("height: "))
    mines = int(input("mines: "))
    game = Board(width, height, mines)
    print(game)
    while True:
        answer = input("do you want to flag? y/n ")
        if answer == "y":
            print("flag:") 
            x = int(input("x: "))
            y = int(input("y: "))
            game.toggle_flag(x, y)
            print(game)
            continue
        print("reveal:")
        x = int(input("x: "))
        y = int(input("y: "))
        game.reveal(x, y)
        print(game)
        if game.state == GameState.LOST:
            print("you lost!")
            break
        if game.state == GameState.WON:
            print("you won!")
            break


if __name__ == "__main__":
    main()
