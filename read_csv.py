import csv
from pprint import pprint

def csv_to_list(file):
    csvfile = open(file)
    csvreader = csv.reader(csvfile, delimiter='\t')
    data = list(csvreader)
    data.pop(0)
    csvfile.close()
    return data        