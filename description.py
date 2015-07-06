import requests
from bs4 import BeautifulSoup


import parseAmazon
single = "/Users/Thoshi64/bottle/AmazonTestDataSingle.csv"
shortestx2 = "/Users/Thoshi64/bottle/AmazonTestDataShortestx2.csv"
shortest = "/Users/Thoshi64/bottle/AmazonTestDataShortest.csv"
shorter = "/Users/Thoshi64/bottle/AmazonTestDataShorter.csv"
short = "/Users/Thoshi64/bottle/AmazonTestDataShort.csv"
normal = "/Users/Thoshi64/bottle/AmazonTestData.csv"

list = parseAmazon.parse(single,',')
for product in list:
    print product
    url = "http://www.amazon.com/dp/" + str(product)
    htmltext = requests.get(url).content

    pageinfo = BeautifulSoup(htmltext, 'html.parser')
    #print(pageinfo.prettify())
    #print pageinfo.find_all()
    print (pageinfo.get_text())
    """for i in range(5):
        print"""
