#!/usr/bin/env python3

"""
This program takes input to construct and display a phonebook.
"""


def add_entry():
    """
    Ask for input twice and add to phonebook if new.
    1. Name
    2. Email
    """
    name = input("Please enter your name: ")
    while True:
        email = input("Please enter your email adress: ")
        if not is_valid_email(email):
            print("That is not a valid adress.")
            continue
        if not is_unique(email):
            print("That adress already exists in the phonebook.")
            return
        entries.append([name, email])
        return


def is_valid_email(email):
    """
    Returns True if email adress is valid.
    """
    if " " in email:
        return False
    try:
        _, domain = email.split("@")
    except ValueError:
        return False
    try:
        _, _ = domain.split(".")
    except ValueError:
        return False
    return True
    

def is_unique(email):
    """
    Returns True if email adress is not yet in phonebook.
    """
    for entry in entries:
        if email == entry[1]:
            return False
    return True


def list_entries():
    """
    List all entries.
    """
    for entry in entries:
        print(f"{entry[0]}:{entry[1]}")


def interface():
    """
    Main loop to ask for:
    1. List all entries
    2. Add a new entry
    3. Close the program
    """
    while True:
        menu = (
            "What do you want to do? (1/2/3)",
            "1. List all entries",
            "2. Add a new entry",
            "3. Close the program",
        )
        print("\n".join(menu))
        answer = input()
        match answer:
            case "1":
                list_entries()
            case "2":
                add_entry()
            case "3":
                return
            case _:
                print("That is not valid input!\n")
                continue
        print()


if __name__ == "__main__":
    entries = []
    interface()
