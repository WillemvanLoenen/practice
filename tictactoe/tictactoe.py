#!/usr/bin/env python3

"""
Play a game of tictactoe with 2 players or against the computer.
Computer always begins, starts with the middle square followed by random moves.

Game state is represented as 18-bit int.

18-bit int: 0bXXXXXXXXXOOOOOOOOO
Player:       |playerX||playerO|
Square:        987654321987654321

Square position 1 to 9 is counted from left to right, top to bottom.
"""


from random import randrange


def display_board():
    print("+-------+-------+-------+")
    print("|       |       |       |")
    print(f"|   {board[0]}   |   {board[1]}   |   {board[2]}   |")
    print("|       |       |       |")
    print("+-------+-------+-------+")
    print("|       |       |       |")
    print(f"|   {board[3]}   |   {board[4]}   |   {board[5]}   |")
    print("|       |       |       |")
    print("+-------+-------+-------+")
    print("|       |       |       |")
    print(f"|   {board[6]}   |   {board[7]}   |   {board[8]}   |")
    print("|       |       |       |")
    print("+-------+-------+-------+")


def enter_move(game_state, sign):
    """
    Prompts player for a move and validates the move
    Returns increment for player_state
    """
    while True:
        try:
            move = int(input("Enter your move: "))
        except ValueError:
            print("That is not a legal move!")  
            continue
        square = 1 << move - 1
        if square & free_squares(game_state):
            board[move - 1] = sign
            return square
        print("That is not a legal move!")


def draw_move(game_state):
    """
    Draws a random move for the computer in a one player game
    Returns increment for player_state
    """
    while True:
        move = randrange(1, 10)
        square = 1 << move - 1 #2**(col + 3*row)
        if square & free_squares(game_state):
            board[move - 1] = 'X'
            return square


def free_squares(game_state):
    return ~((game_state & 0b111111111) | (game_state >> 9)) & 0b111111111


def victory_for(player_state):
    """
    Returns True if player_state is a victory
    """
    binary_victories = [
            0b_000_000_111,
            0b_000_111_000,
            0b_111_000_000,
            0b_001_001_001,
            0b_010_010_010,
            0b_100_100_100,
            0b_100_010_001,
            0b_001_010_100,
            ]
    return any(victory in binary_victories for victory in 
               (player_state & victory for victory in binary_victories))


def one_player_game():
    game_state = 0
    board[5] = 'X'
    display_board()
    while True:
        game_state += enter_move(game_state, 'O')
        display_board()
        if victory_for(game_state & 0b111111111):
            print("You won!")
            return
        game_state += draw_move(game_state) << 9
        display_board()
        if victory_for(game_state >> 9):
            print("You lost!")
            return
        if not free_squares(game_state):
            print("It's a tie!")
            return


def two_player_game():
    game_state = 0
    display_board()
    while True:
        game_state += enter_move(game_state, 'X') << 9
        display_board()
        if victory_for(game_state >> 9):
            print("Player X won!")
            return
        if not free_squares(game_state):
            print("It's a tie!")
            return
        game_state += enter_move(game_state, 'O')
        display_board()
        if victory_for(game_state & 0b111111111):
            print("Player O won!")
            return


def interface():
    while True:
        answer = input("Do you want to play with 1 or 2 players? (1/2) ")
        match answer:
            case "1":
                one_player_game()
                break
            case "2":
                two_player_game()
                break
            case _:
                print("That is not a valid answer.\n")
                continue


if __name__ == "__main__":
    board = [idx for idx in range(1, 10)]
    interface()
