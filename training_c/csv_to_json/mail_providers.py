"""
Collects count of different email providers in user_data.json.
"""


def file_reader():
    """Read json data from user_data.json, return as list of strings."""
    with open("user_data.json") as f:
        lines = f.readlines()
    return lines


def mail_adresses(lines):
    adresses = []
    for line in lines:
        if line.strip().startswith('"email":'):
            adress = line.replace('"email":', '').replace('"', '').strip()
            if is_valid(adress):
                adresses.append(adress)
    return adresses


def is_valid(adress):
    try:
        name, domain = adress.split('@')
    except ValueError:
        return False
    try:
        provider, tld = domain.split('.')   
    except ValueError:
        return False
    return True


def mail_providers(adresses):
    providers = []
    for adress in adresses:
        _, domain = adress.split('@')
        provider, _ = domain.split('.')
        providers.append(provider)
    return providers


def unique_count(providers):
    unique_count = dict()
    for provider in providers:
        if provider in unique_count:
            unique_count[provider] += 1
        else:
            unique_count[provider] = 1
    print(unique_count)
    return unique_count


if __name__ == "__main__":
    unique_count(mail_providers(mail_adresses(file_reader())))
