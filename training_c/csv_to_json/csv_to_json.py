"""
Converts data in "user_data.csv" from a CSV to JSON format.
"""


def file_reader():
    """Read csv data from user_data.csv, return as list of strings."""
    with open("user_data.csv") as f:
        lines = f.readlines()
    return lines


def parser(lines):
    with open("user_data.json", 'w+') as f:
        header = lines[0].split(';')
        for line in lines[1:]:
            line = line.strip()
            f.write('{\n')
            for key, value in zip(header, line.split(';')):
                f.write(f'\t"{key}": "{value}",\n')
            f.write('},\n')
        f.seek(0)
        print(f.read())


if __name__ == "__main__":
    parser(file_reader())
