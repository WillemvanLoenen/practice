import tkinter as tk
from board import Board, CellState, GameState


class BoardGUI:
    def __init__(self, root: tk.Tk, width: int, height: int, num_mines: int):
        self.board = Board(width, height, num_mines)
        self.root = root

        self.frame = tk.Frame(root)
        self.frame.pack()

        self.buttons = [[None for _ in range(width)] for _ in range(height)]

        for y in range(height):
            for x in range(width):
                btn = tk.Button(
                    self.frame,
                    text="",
                    width=2,
                    height=1,
                    command=lambda x=x, y=y: self.on_left_click(x, y),
                )
                btn.bind("<Button-3>", lambda e, x=x, y=y: self.on_right_click(x, y))
                btn.grid(row=y, column=x)
                self.buttons[y][x] = btn

    def on_left_click(self, x: int, y: int):
        self.board.reveal(x, y)
        self.refresh()

    def on_right_click(self, x: int, y: int):
        self.board.toggle_flag(x, y)
        self.refresh()

    def refresh(self):
        """Sync every button's appearance with the current board state."""
        for y in range(self.board.height):
            for x in range(self.board.width):
                cell = self.board.grid[y][x]
                btn = self.buttons[y][x]

                if cell.state == CellState.HIDDEN:
                    btn.config(text="", relief=tk.RAISED, bg="lightgray")
                elif cell.state == CellState.FLAGGED:
                    btn.config(text="F", relief=tk.RAISED, bg="yellow")
                elif cell.state == CellState.REVEALED:
                    if cell.is_mine:
                        btn.config(text="*", relief=tk.SUNKEN, bg="red")
                    else:
                        text = str(cell.adjacent_count) if cell.adjacent_count > 0 else ""
                        btn.config(text=text, relief=tk.SUNKEN, bg="lightgray")

        if self.board.state == GameState.LOST:
            self.reveal_all_mines()
            self.disable_all()
            self.frame.master.title("Minesweeper — You lost!")
        elif self.board.state == GameState.WON:
            self.disable_all()
            self.frame.master.title("Minesweeper — You won!")

    def reveal_all_mines(self):
        for y in range(self.board.height):
            for x in range(self.board.width):
                cell = self.board.grid[y][x]
                if cell.is_mine:
                    self.buttons[y][x].config(text="*", bg="red")

    def disable_all(self):
        for row in self.buttons:
            for btn in row:
                btn.config(state=tk.DISABLED)


def main():
    root = tk.Tk()
    root.title("Minesweeper")
    BoardGUI(root, width=9, height=9, num_mines=10)
    root.mainloop()


if __name__ == "__main__":
    main()
