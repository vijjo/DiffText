import csv
from pprint import pprint
import difflib
from difflib import SequenceMatcher
from thefuzz import fuzz
import re


def clean_sentence(example):
    example = re.sub(r'<[^>]+>', '', example)
    example = example.replace('bhikkhave', '')
    example = example.replace('&nbsp;', ' ')
    example = example.translate(str.maketrans('', '', "'?.!-,"))
    example = re.sub(r'\s+', ' ', example)
    return example


def print_diff(sent1, sent2):
    sent1 = sent1.splitlines()
    sent2 = sent2.splitlines()
    d = difflib.Differ()
    diff = d.compare(sent1, sent2)
    print('\n'.join(diff))


def ratios(sent1, sent2):
    simple = fuzz.ratio(sent1, sent2)
    partial = fuzz.partial_ratio(sent1, sent2)
    token_sort = fuzz.token_sort_ratio(sent1, sent2)
    token_set = fuzz.token_set_ratio(sent1, sent2)
    return [simple, partial, token_sort, token_set]


def example_group(source, sutta, example, dpd):
    group = {'source': source, 'sutta': sutta, 'example': example, 'dpd': dpd}
    return group


csv_file = "dps-dpd-ex.csv"
# lower_bound = float(input('lower bound: '))
# upper_bound = float(input('upper bound: '))
simple_bound = 96
partial_bound = 95
count_removed_example = 0
total_example = 0
modified_entry = 0
total_entry = 0
with open(csv_file) as f:
    reader = csv.reader(f, delimiter='\t')
    headings = next(reader)
for i in range(1, 7):
    headings.append(f'u{i}_source')
    headings.append(f'u{i}_sutta')
    headings.append(f'u{i}_example')
    headings.append(f'u{i}_dpd')
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
            if row[f'DPD-Example{i}']:
                group = example_group(
                    row[f'DPD-Source{i}'], row[f'DPD-Sutta{i}'], row[f'DPD-Example{i}'], True)
                dpd_list.append(group)
        example_list = []
        for i in range(1, 5):
            if row[f'Example{i}']:
                group = example_group(
                    row[f'Source{i}'], row[f'Sutta{i}'], row[f'Example{i}'], False)
                example_list.append(group)
        # unified_list = dpd_list + example_list
        # original_list = unified_list.copy()
        # if row['Pāli1'] == 'viditvā 2':
        #     pprint(dpd_list)
        #     pprint(example_list)
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
                # print(ratios(example_cleaned, dpd_cleaned))
                # print_diff(example_cleaned, dpd_cleaned)
                if simple_ratio >= simple_bound or partial_ratio >= partial_bound:
                    removed = True
                    deleted_list.append(example_cleaned)
                    break
            if removed:
                modified = True
                count_removed_example += 1
                example_list.remove(unit)
        if modified:
            modified_entry += 1
            deleted_out.write(f"{row['ID']}\t{row['Pāli1']}\n")
            for deleted in deleted_list:
                deleted_out.write(f'•\t{example_cleaned}\n')
        else:
            unmodified_out.write(f"{row['ID']}\t{row['Pāli1']}\n")
        unified_list = dpd_list + example_list

        for i, unified in enumerate(unified_list):
            i += 1
            row[f'u{i}_source'] = unified['source']
            row[f'u{i}_sutta'] = unified['sutta']
            row[f'u{i}_example'] = unified['example']
            row[f'u{i}_dpd'] = unified['dpd']
        dict_writer.writerow(row)

print(f'Total number of examples: {total_example}')
print(f'Removed examples: {count_removed_example}')
print(f'Total number of words: {total_entry}')
print(f'Modified words:: {modified_entry}')
