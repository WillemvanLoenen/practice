#!/usr/bin/env python3

import cmd
from enum import Enum, auto

RED = "\033[91m"
GREEN = "\033[92m"
RED_BACKGROUND = "\033[41m"
GREEN_BACKGROUND = "\033[42m"
RESET = "\033[0m"


class CellState(Enum):
    EMPTY = auto()
    WALL = auto()
    FOOD = auto()
    OUTSIDE = auto()
    PLAYER = auto()
    PLAYER_OUTSIDE = auto()


class VisionState(Enum):
    REVEALED = auto()
    HIDDEN = auto()
    FOG = auto()
    LEFT_FOG = auto()
    RIGHT_FOG = auto()


class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        if self.vision == VisionState.HIDDEN:
            return "  "
        if self.vision == VisionState.FOG:
            return "☁️☁️"
        if self.vision == VisionState.LEFT_FOG:
            return "☁️ "
        if self.vision == VisionState.RIGHT_FOG:
            return " ☁️"
        if self.vision == VisionState.REVEALED:
            if self.state == CellState.EMPTY:
                return "  "
            if self.state == CellState.WALL:
                return "🪨️"
            if self.state == CellState.FOOD:
                return "🍎️"
            if self.state == CellState.PLAYER:
                return "🙂️"
            if self.state == CellState.OUTSIDE:
                return f"{GREEN_BACKGROUND}  {RESET}"
            if self.state == CellState.PLAYER_OUTSIDE:
                return f"{GREEN_BACKGROUND}🙂️{RESET}"


class Maze:
    def __init__(self, width=11, height=11):
        self.width = width
        self.height = height
        self.x = width//2 + 8
        self.y = height//2 + 8

        self.max_energy = 20
        self.energy = 10
        self.food = 5

        self.max_fog = 4
        self.max_vision = 3
        self.padding = 2* self.max_fog

        self.prompt = "Did you find the exit yet?"

        self.grid = self._init_maze()
        self._hardcoded_maze()

    # TODO: random maze
    def _init_maze(self):
        """Initialize a random maze."""
        grid = [
            [Cell(x, y)
            for x in range(self.width + 2 * self.padding)]
            for y in range(self.height + 2 * self.padding)
        ]
        return grid

    def _hardcoded_maze(self):
        w = CellState.WALL
        e = CellState.EMPTY
        f = CellState.FOOD
        o = CellState.OUTSIDE
        grid = [
            [o, w, w, e, w, o, w, w, w, o, o],
            [w, f, w, e, e, w, e, e, f, w, o],
            [w, e, e, w, f, e, e, w, w, f, w],
            [w, e, e, e, w, w, e, e, e, e, w],
            [w, e, w, e, w, w, w, w, e, f, w],
            [w, e, w, f, e, e, e, e, e, e, w],
            [w, e, f, w, f, w, e, w, w, w, o],
            [e, w, e, w, e, w, e, w, e, e, w],
            [w, f, e, e, e, w, f, e, e, e, w],
            [o, w, w, e, w, f, w, w, w, f, w],
            [w, o, o, w, f, e, w, o, o, w, w],
        ]

        for row in grid:
            for _ in range(self.padding):
                row.insert(0, o)
            row.extend([o for _ in range(self.padding)])
        for _ in range(self.padding):
            grid.insert(0, [o for _ in range(self.width + 2 * (self.padding))])
        grid.extend([[o for _ in range(self.width + 2 * (self.padding))]
                        for _ in range(self.padding)])

        for row, hard_row in zip(self.grid, grid):
            for cell, hard_cell, in zip(row, hard_row):
                cell.state = hard_cell

        self.grid[self.y][self.x].state = CellState.PLAYER 

    def move(self, x, y):
        if self.grid[self.y+y][self.x+x].state == CellState.WALL:
            print("You can't go there!")
            return False

        self.grid[self.y][self.x].state = CellState.EMPTY
        self.x += x
        self.y += y
        cell = self.grid[self.y][self.x]
        self.energy -= 1

        if cell.state == CellState.OUTSIDE:
            cell.state = CellState.PLAYER_OUTSIDE
            self.prompt = "You've escaped!"
            print(self)
            return True
        elif cell.state == CellState.FOOD:
            maze._eat()
        elif cell.state == CellState.EMPTY:
            if self.energy < 5:
                self.prompt = "You're getting hungry! You need to find some refreshments!"
            else:
                self.prompt = "Did you find the exit yet?"

        cell.state = CellState.PLAYER

        if self.energy <= 0:
            self.prompt = "You're exhausted! You failed to find your way out!"
            print(self)
            return True

        print(self)
        return False

    def _eat(self):
        self.energy = min(self.energy + self.food, self.max_energy)
        self.prompt = "You find an apple! That replenishes some energy!"

    def _set_vision(self):
        for row in self.grid:
            for cell in row:
                distance = (self.x - cell.x)**2 + (self.y - cell.y)**2
                if distance <= self.max_fog**2:
                    cell.vision = VisionState.FOG
                elif distance <= (self.max_fog+.2)**2:
                    if cell.x < self.x:
                        cell.vision = VisionState.RIGHT_FOG
                    if cell.x > self.x:
                        cell.vision = VisionState.LEFT_FOG
                else:
                    cell.vision = VisionState.HIDDEN
                if distance <= self.max_vision**2:
                    cell.vision = VisionState.REVEALED

    def __repr__(self):
        print("\033[H\033[J", end="")
        self._set_vision()
        visual_grid = []
        for row in self.grid[self.y-self.padding+1:self.y+self.padding]:
            visual_grid.append(row[self.x-self.padding+1:self.x+self.padding])
        grid = "\n".join("".join(repr(cell) for cell in row) for row in visual_grid) + "\n"
        health_status = (
            "\n     " + 
            self.energy * f"{GREEN}◼{RESET}" + 
            (self.max_energy - self.energy) * f"{RED}◼{RESET}"
        )
        return "\n" + health_status + "\n    " + grid + self.prompt


class Actions(cmd.Cmd):
    aliases = {
        "n": "do_north",
        "s": "do_south",
        "e": "do_east",
        "w": "do_west",
    }

    @classmethod
    def do_vim(cls, args):
        """Set vim bindings"""
        cls.aliases = {
            "k": "do_north",
            "j": "do_south",
            "l": "do_east",
            "h": "do_west",
        }
        print(f"Aliases are now set to {cls.aliases}.")

    def default(self, line):
        cmd, arg, _ = self.parseline(line)
        if cmd in self.aliases:
            handler = getattr(self, self.aliases[cmd])
            return handler(arg)
        else:
            print(f"Unknown command: {line!r}. Type 'help' for a list of commands.")

    def do_north(self, args):
        """Go north"""
        if maze.move(0, -1):
            return True

    def do_south(self, args):
        """Go south"""
        if maze.move(0, 1):
            return True

    def do_east(self, args):
        """Go east"""
        if maze.move(1, 0):
            return True

    def do_west(self, args):
        """Go west"""
        if maze.move(-1, 0):
            return True


if __name__ == "__main__":
    maze = Maze()
    prompt = Actions()
    maze.prompt = "You're lost! Find your way out!"
    print(maze)
    prompt.prompt = "\nEnter your action:\n>"
    prompt.cmdloop()
                    
