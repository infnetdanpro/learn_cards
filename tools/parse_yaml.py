import yaml
import os


def list_files(directory: str) -> list:
    files = os.listdir(directory)
    i = 0
    for file in files:
        if '.yaml' not in file:
            files.pop(i)
        i += 1
    return files


def parse_yaml(file: str) -> dict:
    with open(file, encoding='utf-8-sig') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    return data


if __name__ == '__main__':
    directory = 'D:\\Develop\\srpski_card\\dictionary'
    file = os.path.join(directory, 'restoran.yaml')
    file_dict = parse_yaml(file)
    # print(file_dict)

    file_list = list_files(directory)
    print(file_list)
