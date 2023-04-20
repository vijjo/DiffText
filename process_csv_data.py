import csv
from pprint import pprint
import difflib
from difflib import SequenceMatcher
from thefuzz import fuzz
import re

def clean_sentence(example):
    example = example.replace('<br/>', '')
    example = example.replace('<b>', '')
    example = example.replace('</b>', '')
    example = example.replace('bhikkhu', '')
    example = example.replace('bhikkhave', '')
    example = example.replace('  ', ' ')
    example = example.translate(str.maketrans('', '', "'?.!-,"))
    return example    

def print_diff(sent1, sent2):
    sent1 = sent1.splitlines()
    sent2 = sent2.splitlines()
    d = difflib.Differ()
    diff = d.compare(sent1, sent2)
    print('\n'.join(diff))

def example_group(source, sutta, example):
    group = {'source': source, 'sutta': sutta, 'example': example}
    return group

csv_file = "dps-dpd-ex.csv"
# lower_bound = float(input('lower bound: '))
# upper_bound = float(input('upper bound: '))
count = 0
total = 0
modified_entry = 0
total_entry = 0
with open(csv_file) as f:
    reader = csv.DictReader(f, delimiter='\t')
    for index, row in enumerate(reader):
        total_entry += 1
        # if index == 1020:
        #     break
        dpd_list = []
        for i in range(1, 3):
            if row[f'DPD-Example{i}']:
                group = example_group(row[f'DPD-Source{i}'], row[f'DPD-Sutta{i}'], row[f'DPD-Example{i}'])
                dpd_list.append(group)
        example_list = []
        for i in range(1, 5):
            if row[f'Example{i}']:
                group = example_group(row[f'Source{i}'], row[f'Sutta{i}'], row[f'Example{i}'])
                example_list.append(group)
        removed_list = []
        stored_list = []
        # if bool(example_list):
        modified = False
        for unit in example_list[:]:
            total += 1
            removed = False
            for dpd in dpd_list:
                example_cleaned = clean_sentence(unit['example'])
                dpd_cleaned = clean_sentence(dpd['example'])
                seq = SequenceMatcher(a=example_cleaned, b=dpd_cleaned)
                # print(seq.ratio())
                # print(fuzz.ratio(example_cleaned, dpd_cleaned))
                # print("----------------")
                fuzz_ratio = fuzz.partial_ratio(example_cleaned, dpd_cleaned)
                # if seq.ratio() < 0.2 and fuzz_ratio >= 90:
                #     print("\n----------------------------------------------------")
                #     print(f'Similarity: {seq.ratio()}\t\tFuzz: {fuzz_ratio}')
                #     print_diff(example_cleaned, dpd_cleaned)
                if seq.ratio() >= 0.95 or fuzz_ratio >= 95:
                    # print(f"Removed: {unit['example']}")
                    removed = True
                    break
                # elif seq.ratio() >= 0.85 fuzz_ratio >= 90:
                #     print("\n----------------------------------------------------")
                #     print(f'Similarity: {seq.ratio()}\t\tFuzz: {fuzz_ratio}')
                #     print_diff(example_cleaned, dpd_cleaned)
                #     removed = True
                #     break
            if removed:
                modified = True
                count += 1
                example_list.remove(unit)
        if modified:
            modified_entry += 1 
                    # count += 1
                    # print("\n----------------------------------------------------")
                    # print(f'Similarity: {seq.ratio()}\t\tFuzz: {fuzz_ratio}')
                    # print_diff(example_cleaned, dpd_cleaned)
            
        # print(f"{row['ID']}\t\t{row['Pāli1']}")
        # print('PDD_LIST:')
        # pprint(dpd_list)
        # print('EXAMPLE_LIST:')
        # pprint(example_list) 
        # print('----------------------------------')
    #     total += 1
    #     dpd_1 = clean_sentence(row['DPD-Example1'])
    #     example_1 = clean_sentence(row['Example1'])
    #     seq = SequenceMatcher(a=dpd_1, b=example_1)
    #     if seq.ratio() >= lower_bound and seq.ratio() <= upper_bound:
    #         count += 1
    #         print("\n----------------------------------------------------")
    #         print(f"{row['ID']}\t{row['Pāli1']}")
    #         print('----')
    #         print(seq.ratio())
    #         print_diff(dpd_1, example_1)
    # print(f"lower bound: {lower_bound}, upper bound: {upper_bound}")
    print(f'Total number of examples: {total}')
    print(f'Removed examples: {count}')
    print(f'Total number of words: {total_entry}')
    print(f'Modified words:: {modified_entry}')