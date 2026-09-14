import time
import tkinter as tk
from tkinter import messagebox, simpledialog

import highscores as hs
from board import Board, CellState, GameState
from solver import Solver

DIFFICULTIES = {
    "Beginner": (9, 9, 10),
    "Intermediate": (16, 16, 40),
    "Expert": (30, 16, 99),
}


class MinesweeperApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Minesweeper")

        self.highscores = hs.load_highscores()
        self.highscore_eligible = True

        self.current_difficulty = "Beginner"
        self.width, self.height, self.num_mines = DIFFICULTIES["Beginner"]
        self.auto_resolve_flags = tk.BooleanVar(value=False)

        self.board: Board | None = None
        self.buttons = []

        self.timer_running = False
        self.start_time = None
        self.elapsed = 0
        self._timer_job = None

        self._build_menu()
        self._build_status_bar()
        self.board_frame = tk.Frame(self.root)
        self.board_frame.pack()

        self.root.bind("<Control-n>", lambda event: self.new_game())
        self.root.bind_all("<Control-q>", lambda event: self.root.destroy())
        self.root.bind("<Control-h>", lambda event: self.get_hint())
        self.root.bind("<Control-s>", lambda event: self.solve())

        self.new_game()

    # ---------------- Menu ----------------

    def _build_menu(self):
        menubar = tk.Menu(self.root)

        game_menu = tk.Menu(menubar, tearoff=0)
        game_menu.add_command(label="New Game", command=self.new_game, accelerator="Ctrl+N")
        game_menu.add_separator()

        diff_menu = tk.Menu(game_menu, tearoff=0)
        for level in DIFFICULTIES:
            diff_menu.add_command(
                label=level, command=lambda level=level: self.set_difficulty(level)
            )
        diff_menu.add_separator()
        diff_menu.add_command(label="Custom...", command=self.set_custom_difficulty)
        game_menu.add_cascade(label="Difficulty", menu=diff_menu)


        game_menu.add_separator()
        game_menu.add_command(label="Highscores", command=self.show_highscores)
        game_menu.add_separator()
        game_menu.add_command(label="Exit", command=self.root.destroy, accelerator="Ctrl+Q")

        menubar.add_cascade(label="Game", menu=game_menu)
        self.root.config(menu=menubar)

        help_menu = tk.Menu(menubar, tearoff=0)

        help_menu.add_checkbutton(
            label="Auto resolve flags",
            variable=self.auto_resolve_flags,
            onvalue=True,
            offvalue=False,
            command=self.toggle_auto_resolve_flags
        )

        help_menu.add_separator()
        help_menu.add_command(label="Hint", command=self.get_hint, accelerator="Ctrl+H")
        help_menu.add_separator()
        help_menu.add_command(label="Solve", command=self.solve, accelerator="Ctrl+S")

        menubar.add_cascade(label="Help", menu=help_menu)

    def _build_status_bar(self):
        status = tk.Frame(self.root)
        status.pack(fill=tk.X)

        self.mine_label = tk.Label(status, text="Mines: 0")
        self.mine_label.pack(side=tk.LEFT, padx=6, pady=4)

        self.timer_label = tk.Label(status, text="Time: 0")
        self.timer_label.pack(side=tk.RIGHT, padx=6, pady=4)

    # ---------------- Difficulty selection ----------------

    def set_difficulty(self, level: str):
        self.current_difficulty = level
        self.width, self.height, self.num_mines = DIFFICULTIES[level]
        self.new_game()

    def toggle_auto_resolve_flags(self):
        self.board.auto_resolve_flags = self.auto_resolve_flags.get()
        self.highscore_eligible = False

    def set_custom_difficulty(self):
        width = simpledialog.askinteger(
            "Custom game", "Width:", minvalue=2, maxvalue=50, parent=self.root
        )
        if width is None:
            return
        height = simpledialog.askinteger(
            "Custom game", "Height:", minvalue=2, maxvalue=50, parent=self.root
        )
        if height is None:
            return

        max_mines = max(1, width * height - 9)
        mines = simpledialog.askinteger(
            "Custom game",
            f"Mines (1-{max_mines}):",
            minvalue=1,
            maxvalue=max_mines,
            parent=self.root,
        )
        if mines is None:
            return

        self.current_difficulty = "Custom"
        self.width, self.height, self.num_mines = width, height, mines
        self.new_game()

    # ---------------- Game lifecycle ----------------

    def new_game(self):
        self._stop_timer()
        self.elapsed = 0
        self.timer_label.config(text="Time: 0")
        self.highscore_eligible = not self.auto_resolve_flags

        for widget in self.board_frame.winfo_children():
            widget.destroy()

        self.board = Board(self.width, self.height, self.num_mines)
        self.mine_label.config(text=f"Mines: {self.num_mines}")
        self.board.auto_resolve_flags = self.auto_resolve_flags.get()

        self.buttons = [[None] * self.width for _ in range(self.height)]
        for y in range(self.height):
            for x in range(self.width):
                btn = tk.Button(
                    self.board_frame,
                    text="",
                    width=2,
                    height=1,
                    command=lambda x=x, y=y: self.on_left_click(x, y),
                )
                btn.bind("<Button-3>", lambda event, x=x, y=y: self.on_right_click(x, y))
                btn.grid(row=y, column=x)
                self.buttons[y][x] = btn

        self.root.title(f"Minesweeper — {self.current_difficulty}")

    # ---------------- Click handling ----------------

    def on_left_click(self, x: int, y: int):
        if self.board.state != GameState.PLAYING:
            return

        if not self.timer_running and self.board.grid[y][x].state == CellState.HIDDEN:
            self._start_timer()

        self.board.reveal(x, y)
        self.refresh()

    def on_right_click(self, x: int, y: int):
        if self.board.state != GameState.PLAYING:
            return

        self.board.toggle_flag(x, y)
        self.refresh()
        self._update_mine_count()

    # ---------------- Timer ----------------

    def _start_timer(self):
        self.timer_running = True
        self.start_time = time.time()
        self._tick()

    def _tick(self):
        if not self.timer_running:
            return
        self.elapsed = int(time.time() - self.start_time)
        self.timer_label.config(text=f"Time: {self.elapsed}")
        self._timer_job = self.root.after(1000, self._tick)

    def _stop_timer(self):
        self.timer_running = False
        if self._timer_job is not None:
            self.root.after_cancel(self._timer_job)
            self._timer_job = None

    def _update_mine_count(self):
        flagged = sum(
            1
            for row in self.board.grid
            for cell in row
            if cell.state == CellState.FLAGGED
        )
        self.mine_label.config(text=f"Mines: {self.num_mines - flagged}")

    # ---------------- Rendering ----------------

    def refresh(self):
        for y in range(self.height):
            for x in range(self.width):
                cell = self.board.grid[y][x]
                btn = self.buttons[y][x]

                if cell.state == CellState.HIDDEN:
                    btn.config(text="", relief=tk.RAISED, bg="lightgrey")
                elif cell.state == CellState.FLAGGED:
                    btn.config(text="F", relief=tk.RAISED, bg="yellow")
                elif cell.state == CellState.REVEALED:
                    if cell.is_mine:
                        btn.config(text="*", relief=tk.SUNKEN, bg="red")
                    else:
                        text = str(cell.adjacent_count) if cell.adjacent_count > 0 else ""
                        btn.config(text=text, relief=tk.SUNKEN, bg="white")

        if self.board.state == GameState.LOST:
            self._stop_timer()
            self._reveal_all_mines()
            self._disable_all()
        elif self.board.state == GameState.WON:
            self._stop_timer()
            self._disable_all()
            self._handle_win()

    def _reveal_all_mines(self):
        for y in range(self.height):
            for x in range(self.width):
                cell = self.board.grid[y][x]
                if cell.is_mine:
                    self.buttons[y][x].config(text="*", bg="red")

    def _disable_all(self):
        for row in self.buttons:
            for btn in row:
                btn.config(state=tk.DISABLED)

    # ---------------- Highscores ----------------

    def _handle_win(self):
        if (self.current_difficulty not in hs.RANKED_DIFFICULTIES 
                or not self.highscore_eligible):
            messagebox.showinfo("You won!", f"Solved in {self.elapsed} seconds.")
            return

        if hs.qualifies(self.highscores, self.current_difficulty, self.elapsed):
            name = simpledialog.askstring(
                "New highscore!",
                f"Top {hs.MAX_ENTRIES} for {self.current_difficulty} — {self.elapsed}s!\n"
                "Enter your name:",
                parent=self.root,
            )
            name = (name or "").strip() or "Anonymous"
            hs.add_score(self.highscores, self.current_difficulty, name, self.elapsed)
            self.show_highscores()
        else:
            messagebox.showinfo("You won!", f"Solved in {self.elapsed} seconds.")

    def show_highscores(self):
        win = tk.Toplevel(self.root)
        win.title("Highscores")
        win.resizable(False, False)

        for col, level in enumerate(hs.RANKED_DIFFICULTIES):
            tk.Label(win, text=level, font=("TkDefaultFont", 10, "bold")).grid(
                row=0, column=col, padx=12, pady=(8, 4)
            )
            entries = self.highscores.get(level, [])
            if not entries:
                tk.Label(win, text="—").grid(row=1, column=col, padx=12)
            for i, entry in enumerate(entries):
                tk.Label(win, text=f"{i + 1}. {entry['name']} — {entry['time']}s").grid(
                    row=i + 1, column=col, sticky="w", padx=12
                )

        tk.Button(win, text="Close", command=win.destroy).grid(
            row=hs.MAX_ENTRIES + 1, column=0, columnspan=len(hs.RANKED_DIFFICULTIES), pady=8
        )
    
    # ---------------- Solver ----------------

    def solve(self):
        if self.board.state != GameState.PLAYING:
            return

        self.highscore_eligible = False

        solver = Solver(
            self.board.width,
            self.board.height,
            self.board.num_mines,
            self.board.grid
        )
        gen = iter(solver)

        cell, flag = next(gen)
        if flag:
            self.on_right_click(cell.x, cell.y)
        else:
            self.on_left_click(cell.x, cell.y)
        while self.board.state == GameState.PLAYING:
            cell, flag = gen.send(self.board.grid)
            if flag:
                self.on_right_click(cell.x, cell.y)
            else:
                self.on_left_click(cell.x, cell.y)

    def get_hint(self):
        if self.board.state != GameState.PLAYING:
            return

        self.highscore_eligible = False

        solver = Solver(
            self.board.width,
            self.board.height,
            self.board.num_mines,
            self.board.grid
        )
        gen = iter(solver)

        cell, flag = next(gen)
        if flag:
            self.on_right_click(cell.x, cell.y)
        else:
            self.on_left_click(cell.x, cell.y)
    

def main():
    root = tk.Tk()
    MinesweeperApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
