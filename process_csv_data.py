import csv
from pprint import pprint
import difflib
# from difflib import SequenceMatcher
from thefuzz import fuzz
import re


def clean_sentence(example):
    example = re.sub(r'<[^>]+>', '', example)
    example = example.replace('bhikkhave', '')
    example = example.replace('bhante', '')
    example = example.replace('&nbsp;', ' ')
    example = example.translate(str.maketrans('', '', "'?.!-,"))
    example = re.sub(r'\s+', ' ', example)
    return example


def show_diff(sent1, sent2):
    sent1 = sent1.splitlines()
    sent2 = sent2.splitlines()
    d = difflib.Differ()
    diff = d.compare(sent1, sent2)
    return '\n'.join(diff)


def ratios(sent1, sent2):
    simple = fuzz.ratio(sent1, sent2)
    partial = fuzz.partial_ratio(sent1, sent2)
    token_sort = fuzz.token_sort_ratio(sent1, sent2)
    token_set = fuzz.token_set_ratio(sent1, sent2)
    return [simple, partial, token_sort, token_set]


def example_group(source, sutta, example, dpd, chant_pali='', chant_eng='', sbs_chapter=''):
    group = {'source': source, 'sutta': sutta, 'example': example, 'dpd': dpd,
             'chant_pali': chant_pali, 'chant_eng': chant_eng, 'sbs_chapter': sbs_chapter}
    return group


csv_file = "dps-dpd-ex.csv"
SIMPLE_BOUND = 96
PARTIAL_BOUND = 95
count_deleted_example = 0
total_example = 0
modified_entry = 0
total_entry = 0
with open(csv_file) as f:
    reader = csv.reader(f, delimiter='\t')
    headings = next(reader)
    pprint(headings)
for i in range(1, 7):
    headings.append(f'u{i}_source')
    headings.append(f'u{i}_sutta')
    headings.append(f'u{i}_example')
    headings.append(f'u{i}_dpd')
    headings.append(f'u{i}_chant_pali')
    headings.append(f'u{i}_chant_eng')
    headings.append(f'u{i}_sbs_chapter')
# pprint(headings)

with open(csv_file) as f, open("unified_data.csv", "w") as f_out, open('deleted_example.txt', 'w') as deleted_out, open('unmodified_entry.txt', 'w') as unmodified_out:
    dict_reader = csv.DictReader(f, delimiter='\t')
    dict_writer = csv.DictWriter(f_out, headings, delimiter='\t')
    dict_writer.writeheader()
    # read csv into dictionary
    for index, row in enumerate(dict_reader):
        total_entry += 1

        # if index == 100:
        #     break

        dpd_list = []
        for i in range(1, 3):
            if row[f'DPD_example_{i}']:
                group = example_group(
                    row[f'DPD_source_{i}'], row[f'DPD_sutta_{i}'], row[f'DPD_example_{i}'], True)
                dpd_list.append(group)
        example_list = []
        for i in range(1, 5):
            if row[f'sbs_example_{i}']:
                group = example_group(
                    row[f'sbs_source_{i}'], row[f'sbs_sutta_{i}'], row[f'sbs_example_{i}'], False, 
                    row[f'sbs_chant_pali_{i}'], row[f'sbs_chant_eng_{i}'], row[f'sbs_chapter_{i}'])
                example_list.append(group)
        deleted_list = []
        modified = False
        for unit in example_list[:]:
            total_example += 1
            removed = False
            for dpd in dpd_list:
                example_cleaned = clean_sentence(unit['example'])
                dpd_cleaned = clean_sentence(dpd['example'])
                simple_ratio = fuzz.ratio(example_cleaned, dpd_cleaned)
                partial_ratio = fuzz.partial_ratio(
                    example_cleaned, dpd_cleaned)
                # if row['pali_1'] == 'akata 2':
                #     print(ratios(example_cleaned, dpd_cleaned))
                #     print(show_diff(example_cleaned, dpd_cleaned))
                #     print(dpd_cleaned.count(' ') + 1, example_cleaned.count(' ') + 1)
                #     print(dpd['source'], dpd['sutta'])
                #     print(unit['source'], unit['sutta'])
                if simple_ratio >= SIMPLE_BOUND or partial_ratio >= PARTIAL_BOUND:
                    removed = True
                    deleted_list.append(example_cleaned)
                    break
                elif partial_ratio >= 94 and unit['source'] == dpd['source']:
                #     print(row['id'], row['pali_1'])
                #     print(ratios(example_cleaned, dpd_cleaned))
                #     print(show_diff(example_cleaned, dpd_cleaned))
                #     print(dpd_cleaned.count(' ') + 1, example_cleaned.count(' ') + 1)
                #     print(dpd['source'], dpd['sutta'])
                #     print(unit['source'], unit['sutta'])
                #     print('----------------------------------------------------------------')
                    removed = True
                    deleted_list.append(example_cleaned)
                    break
                    
            if removed:
                modified = True
                count_deleted_example += 1
                example_list.remove(unit)
        if modified:
            modified_entry += 1
            deleted_out.write(f"{row['id']}\t{row['pali_1']}\n")
            for deleted in deleted_list:
                deleted_out.write(f'•\t{example_cleaned}\n')
        else:
            unmodified_out.write(f"{row['id']}\t{row['pali_1']}\n")
        unified_list = dpd_list + example_list

        for i, unified in enumerate(unified_list):
            i += 1
            row[f'u{i}_source'] = unified['source']
            row[f'u{i}_sutta'] = unified['sutta']
            row[f'u{i}_example'] = unified['example']
            row[f'u{i}_dpd'] = unified['dpd']
            row[f'u{i}_chant_pali'] = unified['chant_pali']
            row[f'u{i}_chant_eng'] = unified['chant_eng']
            row[f'u{i}_sbs_chapter'] = unified['sbs_chapter']
        dict_writer.writerow(row)

print(f'Simple Bound: {SIMPLE_BOUND}\tPartial Bound: {PARTIAL_BOUND}')
print(f'Total number of examples: {total_example}')
print(f'Removed examples: {count_deleted_example}')
print(f'Total number of words: {total_entry}')
print(f'Modified words:: {modified_entry}')
