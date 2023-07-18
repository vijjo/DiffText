import csv
from pprint import pprint
import difflib
from thefuzz import fuzz
import re

SIMPLE_BOUND = 85
PARTIAL_BOUND = 80
TOKEN_BOUND = 80
WORD_LIST = [
    '',
    '',
]


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


def example_dict(source, sutta, example, dpd, chant_pali='', chant_eng='', sbs_chapter='', priority: int = 999):
    dict_entry = {'source': source, 'sutta': sutta, 'example': example, 'dpd': dpd,
             'chant_pali': chant_pali, 'chant_eng': chant_eng, 'sbs_chapter': sbs_chapter, 'priority': priority}
    return dict_entry

if __name__ == '__main__':
    count_deleted_example = 0
    total_example = 0
    modified_entry = 0
    total_entry = 0

    csv_file = "updated-dps-dpd-ex.csv"
    changed_heading_file = "temp-" + csv_file

    with open(csv_file, 'r') as f, \
        open(changed_heading_file, 'w') as f_out:
        text = re.sub(r'\t(source|sutta|example)_(1|2)', r'\tsbs_\g<1>_\g<2>', f.read())
        f_out.write(text)

    # read headings from csv_file
    with open(changed_heading_file) as f:
        reader = csv.reader(f, delimiter='\t')
        headings = next(reader)
    for i in range(1, 8):
        headings.append(f'u{i}_source')
        headings.append(f'u{i}_sutta')
        headings.append(f'u{i}_example')
        headings.append(f'u{i}_dpd')
        headings.append(f'u{i}_chant_pali')
        headings.append(f'u{i}_chant_eng')
        headings.append(f'u{i}_sbs_chapter')

    # create mini_headings
    mini_headings = ['id', 'pali_1']
    for i in range(1, 8):
        mini_headings.append(f'u{i}_source')
        mini_headings.append(f'u{i}_sutta')
        mini_headings.append(f'u{i}_example')
        mini_headings.append(f'u{i}_dpd')

    # create list of names
    NAMES = []
    with open('names.txt') as f:
        dict_reader = csv.DictReader(f, delimiter=',')
        for row in dict_reader:
            name = re.sub(r'\s[\d\.\s]+$', '', row['pali_1'])
            NAMES.append(name)
    NAMES = NAMES + ['bhante', 'bhikkhave', 'na']

    with open(changed_heading_file) as f, \
            open('output2/unified_data.csv', 'w') as f_out, \
            open('output2/unified_data_mini.csv', 'w') as f_out_mini, \
            open('output2/deleted_example.txt', 'w') as deleted_out, \
            open('output2/unmodified_entry.txt', 'w') as unmodified_out:

        # prepare output files
        dict_writer = csv.DictWriter(f_out, headings)
        dict_writer.writeheader()
        mini_dict_writer = csv.DictWriter(f_out_mini, mini_headings)
        mini_dict_writer.writeheader()

        # read csv into dictionary
        dict_reader = csv.DictReader(f, delimiter='\t')
        for index, row in enumerate(dict_reader):
            total_entry += 1

            # if index == 100:
            #     break

            # create a list of all dpd examples
            dpd_list = []
            for i in range(1, 3):
                if row[f'DPD_example_{i}']:
                    dict_entry = example_dict(
                        row[f'DPD_source_{i}'], row[f'DPD_sutta_{i}'], row[f'DPD_example_{i}'], True)
                    if dict_entry['source'] and dict_entry['sutta']:
                        dpd_list.append(dict_entry)

            # create lists to sort dps examples
            dps_list = []

            for i in range(1, 6):
                if row[f'sbs_example_{i}']:
                    dict_entry = example_dict(
                        row[f'sbs_source_{i}'], row[f'sbs_sutta_{i}'], row[f'sbs_example_{i}'], False,
                        row[f'sbs_chant_pali_{i}'], row[f'sbs_chant_eng_{i}'], row[f'sbs_chapter_{i}'])
                    dps_list.append(dict_entry)
                    

            
            # create dps_list following the arrangement rules
            

            deleted_list = []
            dpd_matched = []
            modified = False
            # loop through dps_list and compare them with dpd_list
            for dps in dps_list[:]:
                total_example += 1
                # mark dps as tentatively not being removed
                removed = False
                for dpd in dpd_list:
                    # clean up examples before comparing them
                    example_cleaned = clean_sentence(dps['example'])
                    dpd_cleaned = clean_sentence(dpd['example'])
                    simple_ratio = fuzz.ratio(example_cleaned, dpd_cleaned)
                    partial_ratio = fuzz.partial_ratio(
                        example_cleaned, dpd_cleaned)
                    token_set_ratio = fuzz.token_set_ratio(example_cleaned, dpd_cleaned)

                    # if row['pali_1'] in WORD_LIST:
                    #     print(row['pali_1'])
                    #     print(ratios(example_cleaned, dpd_cleaned))
                    #     print(show_diff(example_cleaned, dpd_cleaned))
                    #     print('----------------------------------------------------------------')

                    # check the similarity and partial similarity
                    if simple_ratio >= SIMPLE_BOUND or partial_ratio >= PARTIAL_BOUND or \
                            (token_set_ratio >= TOKEN_BOUND):
                        # move chant_pali, chant_eng, and sbs_chapter from dps to dpd
                        if not dpd in dpd_matched:
                            dpd['dpd'] = dps['dpd']
                            dpd['chant_pali'] = str(dps['chant_pali'])
                            dpd['chant_eng'] = dps['chant_eng']
                            dpd['sbs_chapter'] = dps['sbs_chapter']
                            dpd_matched.append(dpd)
                            if row['pali_1'] == 'sabyañjana':
                                print(row['id'])
                                pprint(dpd) 
                                pprint(dps) 
                                print('-----')
                        # mark dps as being removed
                        removed = True
                        deleted_list.append(example_cleaned)
                        # dpd_matched.append(dpd)
                        break
                # remove marked dps from dps_list
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
            nikaya_examples = []
            trad_examples = []
            arranged_list = []
            empty_example = example_dict("", "", "", False)
            traditional_sources = [
                'Thai',
                'Trad',
                'Sri Lanka',
                'MJG'
            ]

            for unified in unified_list:
                if unified['source'] in traditional_sources or unified['sutta'].startswith('Trad'):
                    trad_examples.append(unified)
                else:
                    nikaya_examples.append(unified)
            
            if trad_examples:
                if len(nikaya_examples) > 2:
                    arranged_list = nikaya_examples[:3] + trad_examples + nikaya_examples[3:]
                elif len(nikaya_examples) == 2:
                    arranged_list = nikaya_examples + trad_examples
                elif len(nikaya_examples) == 1:
                    arranged_list = nikaya_examples + [empty_example] + trad_examples
                else:
                    arranged_list = [empty_example] + [empty_example] + trad_examples
            else:
                arranged_list = nikaya_examples
            # if row['pali_1'] == 'sabyañjana':
            #     pprint(unified_list)
            #     pprint(arranged_list)
                

            for i, item in enumerate(arranged_list):
                i += 1
                # expand current row to include arranged examples
                row[f'u{i}_source'] = item['source']
                row[f'u{i}_sutta'] = item['sutta']
                row[f'u{i}_example'] = item['example']
                row[f'u{i}_dpd'] = item['dpd']
                row[f'u{i}_chant_pali'] = item['chant_pali']
                # if i == 1 and row['pali_1'] == 'sabyañjana':
                #     print(row['u1_chant_pali'])
                #     print(item['chant_pali'])
                row[f'u{i}_chant_eng'] = item['chant_eng']
                row[f'u{i}_sbs_chapter'] = item['sbs_chapter']
            # if row['id'] == '3695':
            # if row['pali_1'] == 'sabyañjana':
            #     print(row['u1_chant_pali'])
            dict_writer.writerow(row)

            # write unified_data_mini.csv
            mini_row = {}
            mini_row['id'] = row['id']
            mini_row['pali_1'] = row['pali_1']
            for i, item in enumerate(arranged_list):
                i += 1
                mini_row[f'u{i}_source'] = item['source']
                mini_row[f'u{i}_sutta'] = item['sutta']
                mini_row[f'u{i}_example'] = item['example']
                mini_row[f'u{i}_dpd'] = item['dpd']
                # if i == 4:
                #     break
            mini_dict_writer.writerow(mini_row)

    print(f'Simple Bound: {SIMPLE_BOUND}\tPartial Bound: {PARTIAL_BOUND}')
    print(f'Total number of examples: {total_example}')
    print(f'Removed examples: {count_deleted_example}')
    print(f'Total number of words: {total_entry}')
    print(f'Modified words: {modified_entry}')
