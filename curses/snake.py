import curses
import time
import random


class Player:
    active_players = 0
    init_len = 4
    width = None
    height = None
    snake_color = {
        "green": [4, 5],
        "cyan": [6, 7],
        "yellow": [8, 9],
        "magenta": [10, 11],
        "blue": [12, 13],
    }

    def __init__(self, position, moves, direction, color, active):
        self.moves = moves
        self.direction = moves[direction]
        self.color = self.__class__.snake_color[color]

        self.deaths = 0
        self.dead = False
        self.death_timer = 0
        self.invincible_timer = 0

        self.snake = [position]
        for _ in range(self.__class__.init_len - 1):
            self.move(direction)

        self.highscore = len(self.snake)

        self.active = False
        if active:
            self.activate()

        self.start_position = position
        self.start_direction = direction

    def move(self, direction):
        if self.death_timer:
            self.death_timer -= 1
            if not self.death_timer and self.__class__.active_players == 1:
                self.dead = False
                self.snake = self.snake[-self.__class__.init_len - 1:]
                self.invincible_timer = 5
            return
        if self.dead:
            if self.__class__.active_players > 1:
                self.snake = []
            return
        if self.invincible_timer:
            self.invincible_timer -= 1

        if self.moves[direction] == self.moves["up"]:
            self._up()
        elif self.moves[direction] == self.moves["down"]:
            self._down()
        elif self.moves[direction] == self.moves["left"]:
            self._left()
        elif self.moves[direction] == self.moves["right"]:
            self._right()

    def _up(self):
        snake = self.snake
        width = self.__class__.width
        height = self.__class__.height
        snake.append((snake[-1][0] % width, (snake[-1][1]-1) % height))
        self.snake = snake

    def _down(self):
        snake = self.snake
        width = self.__class__.width
        height = self.__class__.height
        snake.append((snake[-1][0] % width, (snake[-1][1]+1) % height))
        self.snake = snake

    def _left(self):
        snake = self.snake
        width = self.__class__.width
        height = self.__class__.height
        snake.append(((snake[-1][0]-1) % width, snake[-1][1] % height))
        self.snake = snake

    def _right(self):
        snake = self.snake
        width = self.__class__.width
        height = self.__class__.height
        snake.append(((snake[-1][0]+1) % width, snake[-1][1] % height))
        self.snake = snake

    def remove_tail(self):
        if not self.dead and not self.death_timer:
            self.snake.pop(0)

    def swap_moves(self, other):
        for key, value in self.moves.items():
            if self.direction == value:
                self.direction = other.moves[key]
        for key, value in other.moves.items():
            if other.direction == value:
                other.direction = self.moves[key]
        self.moves, other.moves = other.moves, self.moves

    def die(self):
        self.dead = True
        if not self.__class__.active_players > 1:
            self.deaths += 1
        self.death_timer = 20

    def activate(self):
        self.active = True
        self.__class__.active_players += 1

    def deactivate(self):
        self.active = False
        self.__class__.active_players -= 1

    def reset(self):
        self.deaths = 0
        self.dead = False
        self.death_timer = 0
        self.invincible_timer = 0
        self.direction = self.moves[self.start_direction]
        self.snake = [self.start_position]
        for _ in range(self.__class__.init_len - 1):
            self.move(self.start_direction)
        self.highscore = len(self.snake)

    def status(self):
        if self.__class__.active_players > 1:
            return "      {}  SCORE: {}         ".format(
                "✝" if self.dead else " ",
                self.highscore,
            )
        else:
            return "  SCORE: {} | HIGHSCORE: {} | DEATHS: {}  ".format(
                len(self.snake),
                self.highscore,
                self.deaths,
            )


def draw_game(stdscr): 
    time_step_init = .1
    time_step = time_step_init
    time_decrement = .99

    curses.curs_set(0)
    curses.set_escdelay(25)
    stdscr.nodelay(True)

    curses.start_color()
    curses.init_color(10, 0, 400, 0)
    curses.init_color(11, 0, 400, 400)
    curses.init_color(12, 400, 400, 0)
    curses.init_color(13, 400, 0, 400)
    curses.init_color(14, 0, 0, 600)
    curses.init_color(15, 400, 0, 0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_RED)
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_GREEN)
    curses.init_pair(5, curses.COLOR_WHITE, 10)
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_CYAN)
    curses.init_pair(7, curses.COLOR_WHITE, 11)
    curses.init_pair(8, curses.COLOR_WHITE, curses.COLOR_YELLOW)
    curses.init_pair(9, curses.COLOR_WHITE, 12)
    curses.init_pair(10, curses.COLOR_WHITE, curses.COLOR_MAGENTA)
    curses.init_pair(11, curses.COLOR_WHITE, 13)
    curses.init_pair(12, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(13, curses.COLOR_WHITE, 14)
    curses.init_pair(14, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(15, curses.COLOR_WHITE, 15)
    colors = {
        "status": 1,
        "menu": 2,
        "food": 3,
        "dead_odd": 14,
        "dead_even": 15,
    }

    menu_keys = {
        "pause": ord(" "),
        "resume": ord(" "),
        "new_game": ord("n"),
        "quit": ord("q"),
        "toggle_focus_player": ord("\t"),
        "focus_player_1": ord("1"),
        "focus_player_2": ord("2"),
        "focus_player_3": ord("3"),
        "activate_player": ord("a"),
        "set_wasd": ord("w"),
        "set_arrows": curses.KEY_UP,
        "set_vim": ord("k"),
        "toggle_color": ord("c"),
    }
    arrow_keys = {
        "up": curses.KEY_UP,
        "down": curses.KEY_DOWN,
        "left": curses.KEY_LEFT,
        "right": curses.KEY_RIGHT,
    }
    wasd_keys = {
        "up": ord("w"),
        "down": ord("s"),
        "left": ord("a"),
        "right": ord("d"),
    }
    vim_keys = {
        "up": ord("k"),
        "down": ord("j"),
        "left": ord("h"),
        "right": ord("l"),
    }

    height, width = stdscr.getmaxyx()
    width //= 2
    height -= 1

    move_str = {
        arrow_keys["up"]: "ARROWS", 
        wasd_keys["up"]: "WASD  ",
        vim_keys["up"]: "VIM   ",
    }
    message =  "Press SPACE to go to the MENU" 
    header = "    [TAB]            [C]         [W/UP/K]            [A]   "
    player_template = "  {} PLAYER [{}]" + 20 * " " + "{}      {} ACTIVE   "
    footer = "    [N] for NEW GAME     [SPC] to RESUME     [Q] to QUIT   "
    menu_height = 20
    menu_width = len(footer)
    menu_x = width - menu_width//2 - 1
    menu_y = height//2 - menu_height//2
    focus = [True, False, False]
    tails = [4, 4, 4]


    def create_menu():
        stdscr.attron(curses.color_pair(colors["menu"]))
        for idx in range(menu_height):
            stdscr.addstr(menu_y + idx, menu_x, menu_width*" ")
        stdscr.addstr(menu_y + 2, menu_x, header)
        stdscr.addstr(menu_y + 17, menu_x, footer)

        for idx, p in enumerate(all_players):
            player_str = player_template.format(
                "*" if focus[idx] else " ",
                idx + 1,
                move_str[p.moves["up"]],
                "NOT" if not p.active else "   ",
            )
            if focus[idx]:
                stdscr.attroff(-1)
                stdscr.addstr(menu_y + 4 + 4 * idx, menu_x, menu_width * " ")
                stdscr.addstr(menu_y + 5 + 4 * idx, menu_x, player_str)
                stdscr.addstr(menu_y + 6 + 4 * idx, menu_x, menu_width * " ")
                stdscr.attron(curses.color_pair(colors["menu"]))
            else:
                stdscr.attron(curses.color_pair(colors["menu"]))
                stdscr.addstr(menu_y + 5 + 4 * idx, menu_x, player_str)
            create_menu_snakes()


    def create_menu_snakes():
        for idx, p in enumerate(all_players):
            if focus[idx]:
                stdscr.attroff(-1)
                stdscr.addstr(menu_y + 5 + 4 * idx, menu_x + 14, 10 * "  ")
            for jdx in range(4):
                delta = (2 * jdx + tails[idx]) % 16
                stdscr.attron(curses.color_pair(p.color[(jdx+1)%2]))
                stdscr.addstr(menu_y + 5 + 4 * idx, menu_x + 16 + delta, "  ")


    def process_key(k):
        if k == menu_keys["toggle_focus_player"]:
            focus.insert(0, focus.pop())
        elif k == menu_keys["focus_player_1"]:
            focus[0] = True
            focus[1] = focus[2] = False
        elif k == menu_keys["focus_player_2"]:
            focus[1] = True
            focus[0] = focus[2] = False
        elif k == menu_keys["focus_player_3"]:
            focus[2] = True
            focus[0] = focus[1] = False

        elif k == menu_keys["activate_player"]:
            p = [p for p, f in zip(all_players, focus) if f][0]
            if p.active:
                p.deactivate()
            else:
                p.activate()

        elif k == menu_keys["toggle_color"]:
            p = [p for p, f in zip(all_players, focus) if f][0]
            p.color[0] += 2
            p.color[1] += 2
            if p.color[0] == 14:
                p.color[0] -= 10
                p.color[1] -= 10

        elif k in (
            menu_keys["set_wasd"],
            menu_keys["set_arrows"],
            menu_keys["set_vim"]
            ):
            k_moves = [
                moves for moves in (wasd_keys, arrow_keys, vim_keys)
                if k == moves["up"]
            ][0]
            p1 = [p for p, f in zip(all_players, focus) if f][0]
            p2 = [p for p in all_players if k_moves == p.moves][0]
            p1.swap_moves(p2)

        create_menu()


    Player.width = width
    Player.height = height

    p1 = Player(
        position=(0, height//2),
        moves=arrow_keys,
        direction="right",
        color="green",
        active=True,
    )
    p2 = Player(
        position=(width, height//2),
        moves=wasd_keys,
        direction="left",
        color="cyan",
        active=False,
    )
    p3 = Player(
        position=(width//2, height),
        moves=vim_keys,
        direction="up",
        color="yellow",
        active=False,
    )
    all_players = [p1, p2, p3]
    players = [p for p in all_players if p.active]

    num_food = max(3, width * height // 500)
    food = create_food(height, width, players, num_food=num_food)

    while True:
        stdscr.refresh()
        keys = []
        while True:
            k = stdscr.getch()

            if k == menu_keys["pause"]:
                create_menu()
                create_menu_snakes()
                counter = 0
                
                while True:
                    stdscr.refresh()
                    k = stdscr.getch()
                    curses.flushinp()
                    time.sleep(.01)

                    if k == menu_keys["new_game"]:
                        for p in all_players:
                            p.reset()
                            if p.active and p not in players:
                                players.append(p)
                            elif not p.active and p in players:
                                players.remove(p)
                        food = create_food(height, width, players, num_food=num_food)
                        time_step = time_step_init
                        break
                    elif k == menu_keys["resume"]:
                        for p in all_players:
                            if p.active and p not in players:
                                p.deactivate()
                            elif not p.active and p in players:
                                p.activate()
                        break
                    elif k == menu_keys["quit"]:
                        return
                    elif k in menu_keys.values():
                        process_key(k)

                    counter += 1
                    if counter % 50 == 0:
                        tails = [t + f * 2 for t, f in zip(tails, focus)] 
                    create_menu_snakes()

            if k == -1:
                break
            keys.append(k)
        curses.flushinp()
        time.sleep(time_step)
        stdscr.clear()

        for p in players:
            for k in keys:
                if k in p.moves.values() and k != opposite(p.direction, p.moves):
                    break
            else:
                k = p.direction

            if k == p.moves["up"]:
                p.move("up")
            elif k == p.moves["down"]:
                p.move("down")
            elif k == p.moves["left"]:
                p.move("left")
            elif k == p.moves["right"]:
                p.move("right")

            p.direction = k

        for p in players:
            if not p.dead and p.snake[-1] in food:
                food.extend(create_food(height, width, players, food))
                food.remove(p.snake[-1])
                time_step *= time_decrement ** (1 / len(players))
            else:
                p.remove_tail()

        dead = []
        for p1 in players:
            if p1.dead or p1 in dead:
                continue
            if p1.snake[-1] in p1.snake[:-1]:
                dead.append(p1)
            for p2 in players:
                if p1 == p2:
                    continue
                if p1.snake[-1] in p2.snake:
                    dead.append(p1)
        
        for p in dead:
            if not p.invincible_timer:
                p.die()
                if len(players) == 1:
                    time_step = time_step_init

        stdscr.attron(curses.color_pair(colors["status"]) | curses.A_BOLD)
        stdscr.addstr(height, 0, (2 * width - 1) * " ")
        if len(players) == 1:
            stdscr.addstr(height, 2 * width - len(message) - 4, message)

        for p in players:
            p.highscore = max(p.highscore, len(p.snake))
            
            if p.death_timer and p.death_timer % 2:
                stdscr.attron(curses.color_pair(colors["dead_odd"]))
            else:
                stdscr.attron(curses.color_pair(p.color[0]))

            for part in p.snake[(len(p.snake)+1)%2::2]:
                stdscr.addstr(part[1] % height, 2*(part[0] % width), "  ")

            if p.start_position[0] == 0:
                stdscr.addstr(height, 2, p.status())
            if p.start_position[0] == width//2:
                stdscr.addstr(height, width - len(p.status()) // 2, p.status())
            if p.start_position[0] == width:
                stdscr.addstr(height, 2 * width - len(p.status()) - 4, p.status())

            if p.death_timer and p.death_timer % 2:
                stdscr.attron(curses.color_pair(colors["dead_even"]))
            else:
                stdscr.attron(curses.color_pair(p.color[1]))

            for part in p.snake[len(p.snake)%2::2]:
                stdscr.addstr(part[1] % height, 2*(part[0] % width), "  ")

        stdscr.attron(curses.color_pair(colors["food"]))
        for item in food:
            stdscr.addstr(item[1], 2*item[0], "  ")


def create_food(height, width, players, food=[], num_food=1):
    excluded = []
    excluded.extend(food)
    for p in players:
        excluded.extend(p.snake)
    sample_space = [
        (x, y) for x in range(width) for y in range(height) 
        if (x, y) not in excluded
    ]
    return random.sample(sample_space, num_food)   


def opposite(k, keys):
    if k == keys["down"]:
        return keys["up"]
    elif k == keys["up"]:
        return keys["down"]
    elif k == keys["left"]:
        return keys["right"]
    elif k == keys["right"]:
        return keys["left"]


def main():
    curses.wrapper(draw_game)


if __name__ == "__main__":
    main()
