import csv
import clipboard
from process_csv_data import example_dict
from thefuzz import fuzz
from pprint import pprint
import re
import os

CSV_DATA = 'dps-full.csv'
CSV_FIXED = 'data-fixed.csv'
CSV_EXTRA = 'extra-ex.csv'
CSV_EXTRA_FIXED = 'extra-fixed.csv'
SIMPLE_BOUND = 95
PARTIAL_BOUND = 94
TOKEN_BOUND = 95
BOUNDS = {'simple': SIMPLE_BOUND,
          'partial': PARTIAL_BOUND, 'token': TOKEN_BOUND}
EXCLUDED_HEADERS = [
    'sbs_source_1', 'sbs_sutta_1', 'sbs_example_1', 'sbs_chant_pali_1', 'sbs_chant_eng_1', 'sbs_chapter_1',
    'sbs_source_2', 'sbs_sutta_2', 'sbs_example_2', 'sbs_chant_pali_2', 'sbs_chant_eng_2', 'sbs_chapter_2',
    'sbs_source_3', 'sbs_sutta_3', 'sbs_example_3', 'sbs_chant_pali_3', 'sbs_chant_eng_3', 'sbs_chapter_3',
    'sbs_source_4', 'sbs_sutta_4', 'sbs_example_4', 'sbs_chant_pali_4', 'sbs_chant_eng_4', 'sbs_chapter_4',
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
            for i in range(1, 6):
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


def fix_csv(csv_file, fixed_file, delimiter=','):
    with open(csv_file, 'r') as f, \
            open(fixed_file, 'w') as f_out:
        reader = csv.reader(f, delimiter=delimiter)
        writer = csv.writer(f_out)
        for index, row in enumerate(reader):
            if index == 0:
                # print(row)
                for i in range(len(row)):
                    pattern = re.compile(r'^(source|sutta|example)(_\d)$')
                    if pattern.match(row[i]):
                        row[i] = pattern.sub(r'sbs_\1\2', row[i])
                writer.writerow(row)
                # print(row)
            else:
                writer.writerow(row)
    return fixed_file

def unfix_csv(csv_file, delimiter=','):
    text = []
    with open(csv_file, 'r') as f:
        reader = csv.reader(f, delimiter=delimiter)
        for index, row in enumerate(reader):
            if index == 0:
                for i in range(len(row)):
                    pattern = re.compile(r'^sbs_(source|sutta|example)(_(?:1|2))$')
                    if pattern.match(row[i]):
                        row[i] = pattern.sub(r'\1\2', row[i])
                text.append(row)
            else:
                text.append(row)
    with open(csv_file, 'w') as f_out:
        writer = csv.writer(f_out)
        writer.writerows(text)

if __name__ == '__main__':
    # create list of names
    NAMES = []
    with open('names.txt', 'r') as f:
        dict_reader = csv.DictReader(f, delimiter=',')
        for row in dict_reader:
            name = re.sub(r'\s[\d\.\s]+$', '', row['pali_1'])
            NAMES.append(name)
    NAMES = NAMES + ['bhante', 'bhikkhave', 'na']

    fix_csv(CSV_DATA, CSV_FIXED, '\t')
    fix_csv(CSV_EXTRA, CSV_EXTRA_FIXED)

    data_dict, data_example_dict = extract_dicts(CSV_FIXED)
    extra_example_dict = extract_dicts(CSV_EXTRA_FIXED)[1]
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
    
    headers = heading_list(CSV_FIXED, example_number)
    # pprint(headers)

    for key in data_dict.keys():
        row = {}
        for header in data_dict[key].keys():
            if header not in EXCLUDED_HEADERS:
                row[header] = data_dict[key][header]
        for i in range(example_number):
            i += 1
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
        dict_writer = csv.DictWriter(f, headers)
        dict_writer.writeheader()
        for key in unified_dict.keys():
            dict_writer.writerow(unified_dict[key])
    unfix_csv('data_with_extra.csv')
                
