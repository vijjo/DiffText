import csv
import clipboard
from process_csv_data import example_dict
from thefuzz import fuzz
from pprint import pprint
import re

CSV_DATA = 'dps-full.csv'
CSV_EXTRA = 'extra-ex.csv'
SIMPLE_BOUND = 95
PARTIAL_BOUND = 94
TOKEN_BOUND = 95
BOUNDS = {'simple': SIMPLE_BOUND,
          'partial': PARTIAL_BOUND, 'token': TOKEN_BOUND}
EXCLUDED_HEADERS = [
    'source_1', 'sutta_1', 'example_1', 'sbs_chant_pali_1', 'sbs_chant_eng_1', 'sbs_chapter_1',
    'source_2', 'sutta_2', 'example_2', 'sbs_chant_pali_2', 'sbs_chant_eng_2', 'sbs_chapter_2',
    'sbs_source_3', 'sbs_sutta_3', 'sbs_example_3', 'sbs_chant_pali_3', 'sbs_chant_eng_3', 'sbs_chapter_3',
    'sbs_source_4', 'sbs_sutta_4', 'sbs_example_4', 'sbs_chant_pali_4', 'sbs_chant_eng_4', 'sbs_chapter_4'
    'sbs_source_5', 'sbs_sutta_5', 'sbs_example_5', 'sbs_chant_pali_5', 'sbs_chant_eng_5', 'sbs_chapter_5'
]

def heading_list(csv_file, example_number):
    with open(csv_file, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        headers = next(reader)
    for header in headers[:]:
        if header in EXCLUDED_HEADERS:
            headers.remove(header)
    for i in range(example_number):
        i += 1
        if i <= 2:
            headers.append(f'source_{i}')
            headers.append(f'sutta_{i}')
            headers.append(f'example_{i}')
            headers.append(f'sbs_chant_pali_{i}')
            headers.append(f'sbs_chant_eng_{i}')
            headers.append(f'sbs_chapter_{i}')
        if i > 2:
            headers.append(f'sbs_source_{i}')
            headers.append(f'sbs_sutta_{i}')
            headers.append(f'sbs_example_{i}')
            headers.append(f'sbs_chant_pali_{i}')
            headers.append(f'sbs_chant_eng_{i}')
            headers.append(f'sbs_chapter_{i}')
    return headers
    


def extract_dicts(csv_file, delimiter=','):
    data_dict = {}
    data_example_dict = {}
    with open(csv_file, 'r') as f:
        dict_reader = csv.DictReader(f, delimiter=delimiter)
        for row in dict_reader:
            data_example_list = []
            data_dict[row['id']] = row
            for i in range(1, 3):
                if row[f'example_{i}']:
                    dict_entry = example_dict(
                        row[f'source_{i}'], row[f'sutta_{i}'], row[f'example_{i}'], False,
                        row[f'sbs_chant_pali_{i}'], row[f'sbs_chant_eng_{i}'], row[f'sbs_chapter_{i}'])
                    data_example_list.append(dict_entry)
            for i in range(3, 6):
                if f'sbs_example_{i}' in row:
                    if row[f'sbs_example_{i}']:
                        dict_entry = example_dict(
                            row[f'sbs_source_{i}'], row[f'sbs_sutta_{i}'], row[f'sbs_example_{i}'], False,
                            row[f'sbs_chant_pali_{i}'], row[f'sbs_chant_eng_{i}'], row[f'sbs_chapter_{i}'])
                        data_example_list.append(dict_entry)
            data_example_dict[row['id']] = data_example_list
    return (data_dict, data_example_dict)


def unify_example_dict_lists(data_list: list, extra_list: list, bounds: dict):
    for extra in extra_list[:]:
        removed = False
        for data in data_list:
            cleaned_extra = clean_sentence(extra['example'])
            cleaned_data = clean_sentence(data['example'])
            simple_ratio = fuzz.ratio(cleaned_extra, cleaned_data)
            partial_ratio = fuzz.partial_ratio(cleaned_extra, cleaned_data)
            token_ratio = fuzz.token_set_ratio(cleaned_extra, cleaned_data)
            if simple_ratio >= bounds['simple'] or \
                    partial_ratio >= bounds['partial'] or \
                    token_ratio >= bounds['token']:
                removed = True
                break
        if removed:
            extra_list.remove(extra)
    unified_list = data_list + extra_list
    return unified_list


def clean_sentence(example):
    # example = re.sub(r'<[^>]+>', '', example)
    example = re.sub(r'<br/>', '', example)
    example = example.replace('&nbsp;', ' ')
    example = example.translate(str.maketrans('', '', "'?.!-,…"))
    example = re.sub(r'\s+', ' ', example)
    example = example.strip()
    words = example.split()
    result_words = []
    for word in words:
        if word not in NAMES:
            result_words.append(word)
    filtered_example = ' '.join(result_words)
    return filtered_example


if __name__ == '__main__':
    # create list of names
    NAMES = []
    with open('names.txt', 'r') as f:
        dict_reader = csv.DictReader(f, delimiter=',')
        for row in dict_reader:
            name = re.sub(r'\s[\d\.\s]+$', '', row['pali_1'])
            NAMES.append(name)
    NAMES = NAMES + ['bhante', 'bhikkhave', 'na']

    data_dict, data_example_dict = extract_dicts(CSV_DATA)
    extra_example_dict = extract_dicts(CSV_EXTRA)[1]
    unified_example_dict = {}
    unified_dict = {}
    example_number = 0

    for key in data_example_dict.keys():
        if key in extra_example_dict:
            unified_list = unify_example_dict_lists(
                data_example_dict[key], extra_example_dict[key], BOUNDS)
            unified_example_dict[key] = unified_list
            if len(unified_list) > example_number:
                example_number = len(unified_list)
        else:
            unified_example_dict[key] = data_example_dict[key]
    
    headers = heading_list(CSV_DATA, example_number)
    pprint(headers)

    for key in data_dict.keys():
        row = {}
        for header in data_dict[key].keys():
            if header not in EXCLUDED_HEADERS:
                row[header] = data_dict[key][header]
        for i in range(example_number):
            i += 1
            if i <= 2:
                if i <= len(unified_example_dict[key]):
                    # pprint(unified_example_dict[key])
                    row[f'source_{i}'] = unified_example_dict[key][i - 1]['source']
                    row[f'sutta_{i}'] = unified_example_dict[key][i - 1]['sutta']
                    row[f'example_{i}'] = unified_example_dict[key][i - 1]['example']
                    row[f'sbs_chant_pali_{i}'] = unified_example_dict[key][i - 1]['chant_pali']
                    row[f'sbs_chant_eng_{i}'] = unified_example_dict[key][i - 1]['chant_eng']
                    row[f'sbs_chapter_{i}'] = unified_example_dict[key][i - 1]['sbs_chapter']
                else:
                    row[f'source_{i}'] = ""
                    row[f'sutta_{i}'] = ""
                    row[f'example_{i}'] = ""
                    row[f'sbs_chant_pali_{i}'] = ""
                    row[f'sbs_chant_eng_{i}'] = ""
                    row[f'sbs_chapter_{i}'] = ""
            else:
                if i <= len(unified_example_dict[key]):
                    row[f'sbs_source_{i}'] = unified_example_dict[key][i - 1]['source']
                    row[f'sbs_sutta_{i}'] = unified_example_dict[key][i - 1]['sutta']
                    row[f'sbs_example_{i}'] = unified_example_dict[key][i - 1]['example']
                    row[f'sbs_chant_pali_{i}'] = unified_example_dict[key][i - 1]['chant_pali']
                    row[f'sbs_chant_eng_{i}'] = unified_example_dict[key][i - 1]['chant_eng']
                    row[f'sbs_chapter_{i}'] = unified_example_dict[key][i - 1]['sbs_chapter']
                else:
                    row[f'sbs_source_{i}'] = ""
                    row[f'sbs_sutta_{i}'] = ""
                    row[f'sbs_example_{i}'] = ""
                    row[f'sbs_chant_pali_{i}'] = ""
                    row[f'sbs_chant_eng_{i}'] = ""
                    row[f'sbs_chapter_{i}'] = ""
        unified_dict[key] = row
    with open('data_with_extra.csv', 'w') as f:
        dict_writer = csv.DictWriter(f, headers, delimiter='\t')
        dict_writer.writeheader()
        for key in unified_dict.keys():
            dict_writer.writerow(unified_dict[key])
                
