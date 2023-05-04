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
SBS_PRIORITY = ['Verses',
                'Teachings',
                'Reflections',
                'Cardinal Suttas',
                'Thanksgiving Recitations',
                'Protective Recitations',
                'Funeral Chants',
                'Sharing of Merits',
                'Homage to the Triple Gem',
                'International Pātimokkha',
                'Post Pātimokkha',
                'Prefixes'
                ]
SUTTA_LIST = ['nīvaraṇappahāna',
              'pabbajitābhiṇhasuttaṃ',
              'sacittasuttaṃ',
              'girimānandasuttaṃ',
              'mettāsuttaṃ',
              'loṇakapallasuttaṃ',
              'devadūtasuttaṃ',
              'kesamuttisuttaṃ',
              'abhayasuttaṃ',
              'rohitassasuttaṃ',
              'vipallāsasuttaṃ',
              'sappurisasuttaṃ',
              'abhiṇhapaccavekkhitabbaṭhānasuttaṃ',
              'soṇasuttaṃ',
              'majjhesuttaṃ',
              'nibbedhikasuttaṃ',
              'pacalāyamānasuttaṃ',
              'mettāsuttaṃ',
              'paññāsuttaṃ',
              'sīhanādasuttaṃ',
              'mahāsatipaṭṭhānasuttaṃ',
              'gaṇakamoggallānasuttaṃ',
              'ānāpānassatisuttaṃ',
              'saḷāyatanavibhaṅgasuttaṃ',
              'araṇavibhaṅgasuttaṃ',
              'indriyabhāvanāsuttaṃ',
              'madhupiṇḍikasuttaṃ',
              'dvedhāvitakkasuttaṃ',
              'sabbāsavasuttaṃ',
              'vitakkasaṇṭhānasuttaṃ',
              'mahāassapurasuttaṃ',
              'mahārāhulovādasuttaṃ',
              'sallekhasuttaṃ',
              'puttamaṃsūpamasuttaṃ',
              'nakulapitusuttaṃ',
              'dutiyagaddulabaddhasuttaṃ',
              'vāsijaṭasuttaṃ',
              'soṇasuttaṃ',
              'khajjanīyasuttaṃ',
              'yamakasuttaṃ',
              'pheṇapiṇḍūpamasuttaṃ',
              'udāyīsuttaṃ',
              'ādittapariyāyasuttaṃ',
              'āsīvisopamasuttaṃ',
              'kummopamasuttaṃ',
              'paṭhamadārukkhandhopamasuttaṃ',
              'vīṇopamasuttaṃ',
              'chappāṇakopamasuttaṃ',
              'yavakalāpisuttaṃ',
              'channasuttaṃ',
              'mālukyaputtasuttaṃ',
              'bhadrakasuttaṃ',
              'saṅgāravasuttaṃ',
              'bhikkhunupassayasuttaṃ',
              'janapadakalyāṇīsuttaṃ',
              'bāhiyasuttaṃ']


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

    csv_file = "dps-dpd-ex.csv"

    # read headings from csv_file
    with open(csv_file) as f:
        reader = csv.reader(f, delimiter='\t')
        headings = next(reader)
    for i in range(1, 7):
        headings.append(f'u{i}_source')
        headings.append(f'u{i}_sutta')
        headings.append(f'u{i}_example')
        headings.append(f'u{i}_dpd')
        headings.append(f'u{i}_chant_pali')
        headings.append(f'u{i}_chant_eng')
        headings.append(f'u{i}_sbs_chapter')

    # create mini_headings
    mini_headings = ['id', 'pali_1']
    for i in range(1, 5):
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

    with open(csv_file) as f, \
            open('output/unified_data.csv', 'w') as f_out, \
            open('output/unified_data_mini.csv', 'w') as f_out_mini, \
            open('output/deleted_example.txt', 'w') as deleted_out, \
            open('output/unmodified_entry.txt', 'w') as unmodified_out:

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
                    dpd_list.append(dict_entry)

            # create lists to sort dps examples
            sbs_class_examples = []
            sbs_examples = []
            vinaya_examples = []
            dhammmapda_examples = []
            sutta_examples = []
            other_examples = []
            dps_list = []

            for i in range(1, 3):
                if row[f'example_{i}']:
                    dict_entry = example_dict(
                        row[f'source_{i}'], row[f'sutta_{i}'], row[f'example_{i}'], False,
                        row[f'sbs_chant_pali_{i}'], row[f'sbs_chant_eng_{i}'], row[f'sbs_chapter_{i}'])
                    if row[f'sbs_chapter_{i}']:
                        if dict_entry['sbs_chapter'] in SBS_PRIORITY:
                            dict_entry['priority'] = SBS_PRIORITY.index(dict_entry['sbs_chapter'])
                        sbs_examples.append(dict_entry)
                    else:
                        if row[f'source_{i}'].startswith('DHP'):
                            dhammmapda_examples.append(dict_entry)
                        elif row[f'source_{i}'].startswith('VIN PAT'):
                            vinaya_examples.append(dict_entry)
                        elif row[f'sutta_{i}'] in SUTTA_LIST:
                            # print(row[f'sutta_{i}'])
                            sutta_examples.append(dict_entry)
                        else:
                            other_examples.append(dict_entry)

            for i in range(3, 5):
                if row[f'sbs_example_{i}']:
                    dict_entry = example_dict(
                        row[f'sbs_source_{i}'], row[f'sbs_sutta_{i}'], row[f'sbs_example_{i}'], False,
                        row[f'sbs_chant_pali_{i}'], row[f'sbs_chant_eng_{i}'], row[f'sbs_chapter_{i}'])
                    if i == 3 and row['sbs_class_anki']:
                        sbs_class_examples.append(dict_entry)
                    elif row[f'sbs_chapter_{i}']:
                        if dict_entry['sbs_chapter'] in SBS_PRIORITY:
                            dict_entry['priority'] = SBS_PRIORITY.index(dict_entry['sbs_chapter'])
                        sbs_examples.append(dict_entry)
                    else:
                        if row[f'sbs_source_{i}'].startswith('DHP'):
                            dhammmapda_examples.append(dict_entry)
                        elif row[f'sbs_source_{i}'].startswith('VIN PAT'):
                            # print(row[f'sbs_source_{i}'])
                            vinaya_examples.append(dict_entry)
                        elif row[f'sbs_sutta_{i}'] in SUTTA_LIST:
                            # print(row[f'sbs_sutta_{i}'])
                            sutta_examples.append(dict_entry)
                        else:
                            other_examples.append(dict_entry)

            if sbs_examples:
                # sort sbs_examples by chapters in SBS_PRIORITY
                sbs_examples = sorted(sbs_examples, key=lambda k: k['priority'])
                dps_list = sbs_examples[0:1] + sbs_class_examples + \
                    vinaya_examples + sutta_examples + dhammmapda_examples + \
                    sbs_examples[1:] + other_examples
            else:
                dps_list = sbs_class_examples + \
                    vinaya_examples + sutta_examples + dhammmapda_examples + \
                    other_examples

            deleted_list = []
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

                    if row['pali_1'] in WORD_LIST:
                        print(row['pali_1'])
                        print(ratios(example_cleaned, dpd_cleaned))
                        print(show_diff(example_cleaned, dpd_cleaned))
                        print('----------------------------------------------------------------')

                    # check the similarity and partial similarity
                    if simple_ratio >= SIMPLE_BOUND or partial_ratio >= PARTIAL_BOUND or \
                            (token_set_ratio >= TOKEN_BOUND):
                        # mark dps as being removed
                        removed = True
                        deleted_list.append(example_cleaned)
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
            for i, unified in enumerate(unified_list):
                i += 1
                # expand current row to include unified examples
                row[f'u{i}_source'] = unified['source']
                row[f'u{i}_sutta'] = unified['sutta']
                row[f'u{i}_example'] = unified['example']
                row[f'u{i}_dpd'] = unified['dpd']
                row[f'u{i}_chant_pali'] = unified['chant_pali']
                row[f'u{i}_chant_eng'] = unified['chant_eng']
                row[f'u{i}_sbs_chapter'] = unified['sbs_chapter']
            dict_writer.writerow(row)

            # write unified_data_mini.csv
            mini_row = {}
            mini_row['id'] = row['id']
            mini_row['pali_1'] = row['pali_1']
            for i, unified in enumerate(unified_list):
                i += 1
                mini_row[f'u{i}_source'] = unified['source']
                mini_row[f'u{i}_sutta'] = unified['sutta']
                mini_row[f'u{i}_example'] = unified['example']
                mini_row[f'u{i}_dpd'] = unified['dpd']
                if i == 4:
                    break
            mini_dict_writer.writerow(mini_row)

    print(f'Simple Bound: {SIMPLE_BOUND}\tPartial Bound: {PARTIAL_BOUND}')
    print(f'Total number of examples: {total_example}')
    print(f'Removed examples: {count_deleted_example}')
    print(f'Total number of words: {total_entry}')
    print(f'Modified words:: {modified_entry}')
