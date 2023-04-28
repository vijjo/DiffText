import csv
from os.path import basename

csv_file = 'dps-dpd-ex.csv'

with open(csv_file) as f:
    reader = csv.reader(f, delimiter='\t')
    headings = next(reader)

with open(csv_file) as f, \
        open('filtered_csv/plus_case.csv', 'w') as plus_case, \
        open('filtered_csv/meaning_1.csv', 'w') as meaning_1, \
        open('filtered_csv/meaning_lit.csv', 'w') as meaning_lit, \
        open('filtered_csv/root_pali.csv', 'w') as root_pali, \
        open('filtered_csv/root_base.csv', 'w') as root_base, \
        open('filtered_csv/construction.csv', 'w') as construction, \
        open('filtered_csv/sanskrit.csv', 'w') as sanskrit, \
        open('filtered_csv/variant.csv', 'w') as variant, \
        open('filtered_csv/commentary.csv', 'w') as commentary, \
        open('filtered_csv/notes.csv', 'w') as notes:
    dict_reader = csv.DictReader(f, delimiter='\t')
    out_files = [plus_case, meaning_1, meaning_lit, root_pali, root_base,
                 construction, sanskrit, variant, commentary, notes]
    dict_writers = {}
    for file in out_files:
        name = basename(file.name)[:-4]
        dict_writers[name] = csv.DictWriter(file, headings, delimiter='\t')
        dict_writers[name].writeheader()
    print(dict_writers.keys())
    
    for row in dict_reader:
        for name in dict_writers.keys():
            dpd_name = 'DPD_' + name
            if row[name] and not row[dpd_name]:
                dict_writers[name].writerow(row)
    #     if row['plus_case'] and not row['DPD_plus_case']:
        
        
