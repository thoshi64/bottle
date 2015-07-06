"""Parse data from AmazonTestData.csv into a list of asin values

Assumptions:
-product information in csv file is accurate ie. corresponding ASIN matches correctly with title/product

"""

import csv

my_file = "/Users/Thoshi64/bottle/AmazonTestData.csv" #testing

def parse(raw_file, delimiter):
    """parses csv file into list format and return list variable"""

    opened_file = open(raw_file)

    csv_data = csv.reader(opened_file, delimiter=delimiter)
    parsed_data = []

    #pull headers from csv
    headers = csv_data.next()

    #pull data into list of dictionaries --> more workable to pull ASIN out
    for row in csv_data:
        parsed_data.append(dict(zip(headers, row)))

    ASIN_list = []
    #pull ASIN out from parsed_data
    for product in parsed_data:
        ASIN_list.append(product["ASIN"])

    opened_file.close()

    return ASIN_list


def main(): #testing
    list = parse(my_file, ',')
    print list

if __name__ == "__main__":
    main()
