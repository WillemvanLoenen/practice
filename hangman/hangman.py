#!/usr/bin/env python3

"""
Play a game of hangman in the CLI.

Words are all 96 words of 7 letters selected from:
https://nl.wiktionary.org/wiki/WikiWoordenboek:Lijst_met_1000_basiswoorden
"""

import random
from datetime import date
import time


def get_difficulty_idx(lives_per_word):
    """
    Returns idx of line where difficulty level is located in highscores.txt.
    Returns None if there are not yet highscores for the diffulty level.
    """
    with open("highscores.txt", 'w+') as f:
        lines = f.readlines()

    for idx, line in enumerate(lines):
        if line.strip():
            *_, line_lives_per_word = line.strip().split('\t')
            if int(line_lives_per_word) == lives_per_word:
                return idx
    return None


def add_highscore(name, score, failure_count, lives_per_word, difficulty_idx, rank, elapsed_time):
    """
    Writes score to highscores.txt at the right position at the diffulty level.
    """
    with open("highscores.txt", 'w+') as f:
        lines = f.readlines()

    new_highscore = (f"{name}\t"
                     f"{date.today()}\t"
                     f"{score}\t"
                     f"{failure_count}\t"
                     f"{score/(score+failure_count):.2f}\t"
                     f"{elapsed_time}\t"
                     f"{lives_per_word}\n")
    if difficulty_idx is None:
        lines.insert(rank - 1, new_highscore + '\n')
    else:
        lines.insert(difficulty_idx + rank - 1, new_highscore)

    with open("highscores.txt", 'w') as f:
        f.writelines(lines)


def get_rank(score, failure_count, difficulty_idx, elapsed_time, cutoff):
    """
    Returns rank where score would place within difficulty level.
    """
    if difficulty_idx is None:
        return 1

    with open("highscores.txt", 'w+') as f:
        lines = f.readlines()

        for i, line in enumerate(lines[difficulty_idx:]):
            if line.strip():
                _, _, line_score, linefailure, _, line_time, _ = line.split('\t')
                if score > int(line_score):
                    return i + 1 
                elif score == int(line_score):
                    if failure_count < int(linefailure):
                        return i + 1
                    elif failure_count == int(linefailure):
                        if elapsed_time < int(line_time):
                            return i + 1
            elif i < cutoff:
                return i + 1
            else:
                return None


def print_gallow(lives_per_word, lives):
    """
    Prints gallow depending on remaining lives.
    Only set up to print for difficulty levels 6 and 10.
    """
    gallow = [""]
    gallow.append("\n|\n|\n|\n|\n")
    gallow.append("\n| /\n|/\n|\n|\n")
    gallow.append("______\n| /\n|/\n|\n|\n")
    gallow.append("______\n| /  |\n|/\n|\n|\n")
    gallow.append("______\n| /  |\n|/   o\n|\n|\n")
    gallow.append("______\n| /  |\n|/   o\n|    |\n|\n")
    gallow.append("______\n| /  |\n|/   o/\n|    |\n|\n")
    gallow.append("______\n| /  |\n|/  \\o/\n|    |\n|\n")
    gallow.append("______\n| /  |\n|/  \\o/\n|    |\n|     \\\n")
    gallow.append("______\n| /  |\n|/  \\o/\n|    |\n|   / \\\n")

    print(gallow[max(10 - lives, 0)])


def print_highscore(difficulty_idx, rank=None):
    """
    Prints the complete highscore of the difficulty level.
    """
    if not difficulty_idx:
        difficulty_idx = 0

    print("\n\tRang\tNaam\tDatum\t\tScore\tMislukt\tPercent\tTijd(s)\tLevens") 
    
    with open("highscores.txt", 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines[difficulty_idx:]):
        if line.strip():
            if rank == i+1:
                print(f"--->\t{i+1}\t" + line.strip())
            else:
                print(f"\t{i+1}\t" + line.strip())
        else:
            break


def main():
    cutoff = 10 
    score = 0
    failure_count = 0
    name = input("Geef je naam: ")
    lives_per_word = int(input("Hoeveel levens wil je hebben per woord? "))
    difficulty_idx = get_difficulty_idx(lives_per_word)
    start_time = time.perf_counter()

    for word in words:
        if score > 0 or failure_count > 0:
            print(f"Je hebt tot dusver {score} uit {score + failure_count} woorden goed geraden.")
        if (score + failure_count) % 10 == 0:
            print(f"Score = {score}, \t Mislukt = {failure_count}, \t Moeilijkheidsgraad = {lives_per_word}")
            current_time = time.perf_counter()
            elapsed_time = round(current_time - start_time)
            rank = get_rank(score, failure_count, difficulty_idx, elapsed_time, cutoff)
            if rank:
                print(f"Daarmee plaats je je tot dusver als {rank}e in de highscore!")
            else:
                print("Dat is nog niet goed genoeg voor de highscore.")

        lives = lives_per_word
        guess = "_" * len(word)
        guessed_letters = []

        while lives > 0 and guess != word:
            print(f"Raad een letter! Je hebt nog {lives} levens over.")
            print(f"Je hebt {guessed_letters} al geprobeerd.")
            print_gallow(lives_per_word, lives)
            print(guess, "\n")
            letter = input().lower()
            if letter in alfabet:
                if letter in guessed_letters:
                    print("Die letter heb je al geraden! Probeer het nog eens!")
                    continue
                elif letter in word:
                    guessed_letters.append(letter)
                    for i, char in enumerate(word):
                        if letter == char:
                            guess = guess[:i] + letter + guess[i+1:]
                else:
                    guessed_letters.append(letter)
                    lives -= 1
            else:
                print("Dat is geen letter uit het alfabet! Probeer het nog eens!")
                continue

        if lives == 0:
            failure_count += 1
            print_gallow(lives_per_word, lives)
            print(f"Helaas, je bent af! Het woord was {word}.")
            answer = input("Wil je nog een woord proberen te raden? (j/n) ")
            if answer == 'j':
                continue
            elif answer == 'n':
                print("Tot de volgende keer!")
                break
            else:
                print("Als je niet je niet j/n wilt antwoorden, stoppen we er toch gewoon mee?!")
                break
        elif guess == word:
            score += 1
            print(f"Goed geraden! Het woord was {word}.")
            answer = input("Wil je nog een woord proberen te raden? (j/n) ")
            if answer == 'j':
                continue
            elif answer == 'n':
                print("Tot volgende keer!")
                break
            else:
                print("Als je niet je niet j/n wilt antwoorden, stoppen we er toch gewoon mee?!")
                break
        else:
            print("Dit zou niet moeten kunnen!")

      
    end_time = time.perf_counter()
    elapsed_time = round(end_time - start_time)

    rank = get_rank(score, failure_count, difficulty_idx, elapsed_time, cutoff)
    if rank:
        add_highscore(name, score, failure_count, lives_per_word, difficulty_idx, rank, elapsed_time)

    print_highscore(difficulty_idx, rank)

    if not rank:
        print("\t|")
        print("--->\t*" + (f"\t{name}"
                           f"\t{date.today()}\t"
                           f"{score}\t"
                           f"{failure_count}\t"
                           f"{score/(score+failure_count):.2f}\t"
                           f"{elapsed_time}\t"
                           f"{lives_per_word}"))


if __name__ == "__main__":
    with open("woordenlijst.txt") as f:
        line = f.readlines()
        words = line[0].replace(',', '').split()

    words = [word for word in words if 6 < len(word) < 8]
    random.shuffle(words)

    alfabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
               'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    main()
