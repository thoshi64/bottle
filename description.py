import requests #for grabbing html
from bs4 import BeautifulSoup
import os #for generate_csv
import tablib #for generate_csv
import time #for tracking time
import parseAmazon

def get_descriptions(list):

    count = 0 #testing
    print 'List length:', len(list) #testing
    
    descriplist = []

    for product in list:
        count+=1 #testing
        print count #testing
        
        url = "http://www.amazon.com/dp/" + str(product)
        htmltext = requests.get(url).content

        pageinfo = BeautifulSoup(htmltext, 'lxml')
        if pageinfo.find("div", { "class" : "productDescriptionWrapper" }) is not None:
            descrip = pageinfo.find("div", { "class" : "productDescriptionWrapper" }).text
        elif pageinfo.find("div", { "class" : "a-section a-spacing-small", 'id' : 'productDescription' }) is not None:
            descrip = pageinfo.find("div", { "class" : "a-section a-spacing-small", 'id' : 'productDescription' }).text
        else:
            descrip = None
        descrip = descrip.replace('\n', '').replace('\t', '').replace('\r', '') #remove all "\n" "\t" "\r"
        descriplist.append({'ASIN' : product, 'Description' : descrip})

    return descriplist

def generate_csv(lists, output_file):
    """Writes the given platforms into a CSV file specified by the output_file
    parameter.

    The output_file is a path.  If not existing, a new file with that path will be created.
    """
    with open(output_file, 'w+') as fp:
        dataset = tablib.Dataset(headers=['ASIN', 'Description'])
        for l in lists:
            dataset.append([l['ASIN'], l['Description']])
        fp.writelines(dataset.csv)


def main():
    #initialize start time
    start = time.time()

    normal = "/Users/Thoshi64/bottle/AmazonTestData.csv" #CHANGE THIS

    list = parseAmazon.parse(normal,',')
    descriplist = get_descriptions(list)
    generate_csv(descriplist, "DescriptionsList.csv")

    print 'It took', float(time.time()-start)/60.0, 'minutes.' #returns time to complete

if __name__ == "__main__":
    main()
