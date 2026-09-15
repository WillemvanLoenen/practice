#!/usr/bin/env python3

"""
Simplified implementation of bash command ls in python using argparse.
"""

from argparse import ArgumentParser
import os


def main():
    parser = ArgumentParser()
    
    parser.add_argument(
        "path",
        nargs="?",
        default=os.path.dirname(__file__),
        help="directory to list"
    )
    parser.add_argument(
        "-a", "--all",
        action="store_true",
        help="do not ignore entries starting with ."
    )
    parser.add_argument(
        "-d", "--directory",
        action="store_true",
        help="list only directories"
    )
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="list subdirectories recursively"
    )
    parser.add_argument(
        "-i", "--ignore",
        metavar="PATTERN",
        help="do not list implied entries matching PATTERN"
    )
    
    args = parser.parse_args()

    print_items(args)
    

def print_items(args, path=None, depth=0):
    if not path:
        path = args.path

    for item in sorted(os.listdir(path), key=str.lower):

        if all(conditions(item, args, path)):
            print(formatter(item, depth))

            if args.recursive and os.path.isdir(os.path.join(path, item)):
                print_items(args, os.path.join(path, item), depth+1)


def conditions(item, args, path):
    return (
        args.all or not item.startswith("."),
        not args.directory or os.path.isdir(os.path.join(path, item)),
        not args.ignore or not match_pattern(args.ignore, item),
    )


def match_pattern(pattern, item):
    """Treats * as zero or more characters and ? as single character."""
    subpatterns = pattern.split("*")

    if not pattern.startswith("*"):
        if not match_qmark(subpatterns[0], item[:len(subpatterns[0])]):
            return False
    if not pattern.endswith("*"):
        if not match_qmark(subpatterns[-1], item[-len(subpatterns[-1]):]):
            return False

    search_range = [0, len(item) - len(pattern.replace("*","")) + 1]
    for subpattern in subpatterns:
        for idx in range(*search_range):
            if match_qmark(subpattern, item[idx:idx+len(subpattern)]):
                search_range[0] += idx + len(subpattern)
                search_range[1] += idx + len(subpattern)
                break
        else:
            return False

    return True


def match_qmark(pattern, string):
    return all(p == "?" or p == s for s, p in zip(pattern, string))


def formatter(item, depth):
    return (depth-1) * "|   " + bool(depth) * "|-- " + item


if __name__ == "__main__":
    main()
