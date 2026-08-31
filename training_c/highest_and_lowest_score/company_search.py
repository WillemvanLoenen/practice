def file_reader():
    with open("company.csv") as f:
        lines = f.readlines()
    return lines


def parser(lines):
    header = lines[0].split('\t')
    company = []
    lead_score = []
    for line in lines[1:]:
        line = line.split('\t')
        company.append(line[0])
        lead_score.append(line[5])
    return company, lead_score


def highest_score():
    indices = [index for index, value in enumerate(lead_score) if value == max(lead_score)]
    highest_company = [company[index] for index in indices]
    highest_score = [lead_score[index] for index in indices]
    print("The highest score is obtained by:")
    print(highest_company, highest_score)


def lowest_score():
    indices = [index for index, value in enumerate(lead_score) if value == min(lead_score)]
    lowest_company = [company[index] for index in indices]
    lowest_score = [lead_score[index] for index in indices]
    print("The lowest score is obtained by:")
    print(lowest_company, lowest_score)


if __name__ == "__main__":
    company, lead_score = parser(file_reader())
    highest_score()
    lowest_score()

    # for c, s in zip(company, lead_score):
    #     print(s, c) 
