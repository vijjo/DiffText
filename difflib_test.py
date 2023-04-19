import difflib
from difflib import SequenceMatcher
from pprint import pprint
from read_csv import csv_to_list
from difftext import equalize

data = csv_to_list('sbs-dpd.csv')[0:100]
def print_diff(sent1, sent2):
    sent1 = sent1.splitlines()
    sent2 = sent2.splitlines()
    d = difflib.Differ()
    diff = d.compare(sent1, sent2)
    print('\n'.join(diff))
    
lower_bound = float(input('Lower bound: '))
upper_bound = float(input('Upper bound: '))
count = 0

for pair in data:
    sent1 = pair[0]
    sent2 = pair[1]
    seq = SequenceMatcher(a=sent1, b=sent2)

    if seq.ratio() > lower_bound and seq.ratio() < upper_bound:
        count += 1
        print(seq.ratio())
        print_diff(sent1, sent2)
        print('---------------------------------')

