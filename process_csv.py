import csv

def read_file(filename):
    """
    Return the head and the data (head, data)
    Takes a string to the file path/name as an input
    """
    head = []
    data = []
    
    with open(filename) as industry_data:
        reader = csv.reader(industry_data)
        data_tuples = list(reader)
        head = data_tuples.pop(0)
        data = data_tuples

    return head, data

def main(filename):
    read_file(filename)

if __name__ == "__main__":
    main("constituents_csv.csv")
