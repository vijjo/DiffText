import csv
from pprint import pprint
import difflib
# from difflib import SequenceMatcher
from thefuzz import fuzz
import re


def clean_sentence(example):
    example = re.sub(r'<[^>]+>', '', example)
    example = example.replace('&nbsp;', ' ')
    example = example.translate(str.maketrans('', '', "'?.!-,"))
    example = re.sub(r'\s+', ' ', example)
    example = example.strip()
    words = example.split()
    result_words = []
    for word in words:
        if word not in NAMES:
            result_words.append(word) 
    filtered_example = ' '.join(result_words)
    return filtered_example


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
    # pprint(headings)
for i in range(1, 7):
    headings.append(f'u{i}_source')
    headings.append(f'u{i}_sutta')
    headings.append(f'u{i}_example')
    headings.append(f'u{i}_dpd')
    headings.append(f'u{i}_chant_pali')
    headings.append(f'u{i}_chant_eng')
    headings.append(f'u{i}_sbs_chapter')
# pprint(headings)

NAMES = []
with open('names.txt') as f:
    dict_reader = csv.DictReader(f, delimiter=',')
    for row in dict_reader:
        name = re.sub(r'\s[\d\.\s]+$', '', row['pali_1'])
        NAMES.append(name)
NAMES = NAMES + ['bhante', 'bhikkhave', 'na']
# pprint(NAMES)

with open(csv_file) as f, \
        open('output/unified_data.csv', 'w') as f_out, \
        open('output/deleted_example.txt', 'w') as deleted_out, \
        open('output/unmodified_entry.txt', 'w') as unmodified_out:
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
        sbs_class_examples = []
        sbs_examples = []
        other_examples = []
        dps_list = []
        for i in range(1, 3):
            if row[f'example_{i}']:
                group = example_group(
                    row[f'source_{i}'], row[f'sutta_{i}'], row[f'example_{i}'], False, 
                    row[f'sbs_chant_pali_{i}'], row[f'sbs_chant_eng_{i}'], row[f'sbs_chapter_{i}'])
                if row[f'sbs_chapter_{i}']:
                    sbs_examples.append(group)
                else:
                    other_examples.append(group)
        for i in range(3, 5):
            if row[f'sbs_example_{i}']:
                group = example_group(
                    row[f'sbs_source_{i}'], row[f'sbs_sutta_{i}'], row[f'sbs_example_{i}'], False, 
                    row[f'sbs_chant_pali_{i}'], row[f'sbs_chant_eng_{i}'], row[f'sbs_chapter_{i}'])
                if i == 3 and row['sbs_class_anki']:
                    sbs_class_examples.append(group)
                elif row[f'sbs_chapter_{i}']:
                    sbs_examples.append(group)
                else:
                    other_examples.append(group)
        if sbs_examples:
            dps_list = sbs_examples[0:1] + sbs_class_examples + sbs_examples[1:] + other_examples
        else:
            dps_list = sbs_class_examples + other_examples
        deleted_list = []
        modified = False
        for dps in dps_list[:]:
            total_example += 1
            removed = False
            for dpd in dpd_list:
                example_cleaned = clean_sentence(dps['example'])
                dpd_cleaned = clean_sentence(dpd['example'])
                simple_ratio = fuzz.ratio(example_cleaned, dpd_cleaned)
                partial_ratio = fuzz.partial_ratio(
                    example_cleaned, dpd_cleaned)
                if simple_ratio >= SIMPLE_BOUND or partial_ratio >= PARTIAL_BOUND or \
                    (partial_ratio >= 94 and dps['source'] == dpd['source']):
                    if dps['chant_pali']:
                        dpd['chant_pali'] = dps['chant_pali']
                    if dps['chant_eng']:
                        dpd['chant_eng'] = dps['chant_eng']
                    if dps['sbs_chapter']:
                        dpd['sbs_chapter'] = dps['sbs_chapter']
                    removed = True
                    deleted_list.append(example_cleaned)
                    break
            if removed:
                modified = True
                count_deleted_example += 1
                dps_list.remove(dps)
        
        # write into txt files: deleted_examples & unmodified entries
        if modified:
            modified_entry += 1
            deleted_out.write(f"{row['id']}\t{row['pali_1']}\n")
            for deleted in deleted_list:
                deleted_out.write(f'•\t{example_cleaned}\n')
        else:
            unmodified_out.write(f"{row['id']}\t{row['pali_1']}\n")
        
        # write unified_data.csv
        unified_list = dpd_list + dps_list
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
