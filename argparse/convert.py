#!/usr/bin/env python3

"""
convert.py
Convert data from one CSV format to another CSV format or JSON.
"""


from argparse import ArgumentParser


def read_csv(path):
    """
    Read CSV formatted data from `path` and return a list of lines
    """
    with open(path) as f:
        lines = f.readlines()
    return lines


def write_out(path, data):
    """
    Write every line in `data` to `path`.`formatting`
    """
    with open(path, "w") as f:
        for line in data:
            f.write(line)


def convert():
    """
    Convert data from one CSV format to another CSV format or JSON.
    """

    parser = ArgumentParser()
    parser.add_argument(
        "-d", "--old_delim",
        action="store",
        default=",",
        help="The delimiter in the source",
    )
    parser.add_argument(
        "-D", "--new_delim",
        action="store",
        default="|",
        help="The delimiter for the output",
        )
    parser.add_argument(
        "--headers",
        action="store_true",
        help="Remove headers",
    )
    parser.add_argument(
        "-f", "--format",
        choices=["csv", "json"],
        help="Format output as csv or json",
    )
    parser.add_argument(
        "source",
        help="Path of source",
    )
    parser.add_argument(
        "destination",
        help="Path of source",
    )
    parser.add_argument(
        "--keys",
        nargs="+",
        help="Keys for json when no header",
    )

    args = parser.parse_args()

    old = read_csv(args.source)
    new = []

    if args.old_delim:
        old_delim = args.old_delim
    if args.new_delim:
        new_delim = args.new_delim

    if args.format == "csv" and args.keys:
        parser.error("argument --keys is forbidden when --format is csv") 
    if args.format == "json" and not args.headers and not args.keys:
        parser.error(
            "argument --keys is required when no --header and --format is json")

    if args.headers:
        if args.format == "json":
            header = old[0].strip().split(old_delim)
        del old[0]
    elif args.format == "json":                
        header = args.keys

    if args.format == "csv":
        for line in old:
            parts = line.split(old_delim)
            new.append(new_delim.join(parts))
    elif args.format == "json":
        new.append("[\n")
        for line in old:
            parts = line.strip().split(old_delim)
            new.append("\t{\n")
            for key, value in zip(header, parts):
                new.append(f'\t\t"{key}": "{value}",\n')
            new.append("\t},\n")
        new.append("]")

    write_out(args.destination, new)


if __name__ == "__main__":
    convert()
