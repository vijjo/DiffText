import difflib
from difflib import SequenceMatcher
from pprint import pprint
from read_csv import csv_to_list
from difftext import equalize

data = csv_to_list('sbs-dpd.csv')[0:100]
for pair in data:
    sent1 = pair[0]
    sent2 = pair[1]
    seq = SequenceMatcher(a=sent1, b=sent2)
    print(seq.ratio())

