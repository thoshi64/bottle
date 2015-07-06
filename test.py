import bottlenose
from lxml import objectify
import parseAmazon as pA
import tablib
import os
import string

#for time
import time


AWS_ACCESS_KEY_ID = "AKIAJH3LHWXFCW5MKY5A"
AWS_SECRET_ACCESS_KEY = "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"
AWS_ASSOCIATE_TAG = "reddit0b3-20"

 #initialize amazon api
amazon = bottlenose.Amazon(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_ASSOCIATE_TAG, MaxQPS=0.9)

def _safe_get_element(path, root):
    """Safe Get Element.

    Get a child element of root (multiple levels deep) failing silently
    if any descendant does not exist.

    :param root:
        Lxml element.
    :param path:
        String path (i.e. 'Items.Item.Offers.Offer').
    :return:
        Element or None.
    """
    elements = path.split('.')
    parent = root
    for element in elements[:-1]:
        parent = getattr(parent, element, None)
        if parent is None:
            return None
    return getattr(parent, elements[-1], None)

def _safe_get_element_text(path, root):
    """Safe get element text.

    Get element as string or None,
    :param root:
        Lxml element.
    :param path:
        String path (i.e. 'Items.Item.Offers.Offer').
    :return:
        String or None.
    """
    element = _safe_get_element(path, root)
    if element is not None:
        return element.text
    else:
        return None

def get_similar_products(list):
    """return a list of dictionaries of similar bought products"""
    #initialize cart with random ASIN
    params = {"Item.1.ASIN":'B000DLB2FI', 'Item.1.Quantity':1}
    cart = amazon.CartCreate(**params)
    root = objectify.fromstring(cart)
    cartid = _safe_get_element_text('Cart.CartId', root)
    hmac = _safe_get_element_text('Cart.HMAC', root)

    #create empty list of similar products
    sblist = []
    count = 0 #testing

    #iterate through list of original ASINs and retrieve also bought products
    print 'Retrieving \"Also Bought\" Products!' #testing
    for item in list:
        #add to cart
        amazon.CartClear(CartId=cartid, HMAC=hmac)
        params = {"Item.1.ASIN":item, 'Item.1.Quantity':1, 'CartId':cartid, 'HMAC':hmac, 'ResponseGroup':'Cart,CartSimilarities'}
        cart = amazon.CartAdd(**params)
        #print cart #for testing
        root = objectify.fromstring(cart)
        count +=1 #testing
        print count #testing
        #iterate through each similar product and add to list
        if ("SimilarProduct" in cart and _safe_get_element_text('Title', root.Cart.SimilarProducts.SimilarProduct) is not None):# HOW TO ACCOUNT FOR NO SIMILAR PRODUCTS
            for item2 in root.Cart.SimilarProducts.SimilarProduct:
                sblist.append({'Original ASIN' : item,
                               'Associated ASIN' : item2.ASIN,
                               'Title' : item2.Title,
                               'Price' : None,
                               'Currency Code' : None,
                               'Relationship' : "Also Bought"})

    print 'Total # of \"Also Bought\" Products: ' + str(len(sblist)) #for testing
    count = 0 #testing
    #iterate through each similar prodcut and obtain highest price
    print 'Retrieving prices!' #testing
    for item in sblist:
        if item['Title'] is not None:
            title = filter(lambda x: x in string.printable, item['Title'].text) #remove non-ascii
            item['Title'] = title
        count+=1 #testing
        print count #testing
        #print str(item["Associated ASIN"]) + "sm" #testing
        pricelist = amazon.ItemLookup(ItemId=item['Associated ASIN'],ResponseGroup="OfferSummary,VariationSummary")
        priceroot = objectify.fromstring(pricelist)
        #conditionals to check if parent or child ASIN or OOS
        if _safe_get_element_text("Items.Item.VariationSummary.HighestPrice.FormattedPrice", priceroot) is not None: #Parent ASIN
            item['Price'] = _safe_get_element_text('Items.Item.VariationSummary.HighestPrice.FormattedPrice', priceroot)
            item['Currency Code'] = _safe_get_element_text('Items.Item.VariationSummary.HighestPrice.CurrencyCode', priceroot)
        elif _safe_get_element_text("Items.Item.OfferSummary.LowestNewPrice.FormattedPrice", priceroot) is not None: #Child ASIN
            #save price and currency in case no other sellers
            price = _safe_get_element_text("Items.Item.OfferSummary.LowestNewPrice.FormattedPrice", priceroot)
            currencycode = _safe_get_element_text("Items.Item.OfferSummary.LowestNewPrice.CurrencyCode", priceroot)
            amazon.CartClear(CartId=cartid, HMAC=hmac)
            params = {"Item.1.ASIN":item['Associated ASIN'], 'Item.1.Quantity':1, 'CartId':cartid, 'HMAC':hmac}
            cart = amazon.CartAdd(**params)
            rootcart = objectify.fromstring(cart)
            parentASIN = _safe_get_element_text("Cart.ParentASIN",rootcart) #get Parent ASIN
            parentproduct = amazon.ItemLookup(ItemId=parentASIN, ResponseGroup="OfferSummary,VariationSummary")
            rootparent = objectify.fromstring(parentproduct)
            #No way to obtain highest price without through VariationSummary
            if _safe_get_element_text('Items.Item.VariationSummary.HighestPrice.FormattedPrice', rootparent) is not None:
                item['Price'] = _safe_get_element_text('Items.Item.VariationSummary.HighestPrice.FormattedPrice', rootparent)
                item['Currency Code'] = _safe_get_element_text('Items.Item.VariationSummary.HighestPrice.CurrencyCode', rootparent)
            else:
                item['Price'] = price
                item['Currency Code'] = currencycode

    return sblist


def get_viewed_products(list):
    """return a list of dictionaries of similar viewed products"""
    #initialize cart with random ASIN
    params = {"Item.1.ASIN":'B000DLB2FI', 'Item.1.Quantity':1}
    cart = amazon.CartCreate(**params)
    root = objectify.fromstring(cart)
    cartid = _safe_get_element_text('Cart.CartId', root)
    hmac = _safe_get_element_text('Cart.HMAC', root)

    #create empty list of similar products
    svlist = []
    count = 0 #testing

    #iterate through list of original ASINs and retrieve also viewed products
    print 'Retrieving \"Also Viewed\" Products!' #testing
    for item in list:
        #add to cart
        amazon.CartClear(CartId=cartid, HMAC=hmac)
        params = {"Item.1.ASIN":item, 'Item.1.Quantity':1, 'CartId':cartid, 'HMAC':hmac, 'ResponseGroup':'Cart,CartSimilarities'}
        cart = amazon.CartAdd(**params)
        #print cart #testing
        root = objectify.fromstring(cart)
        count +=1 #testing
        print count #testing

        #iterate through each similar product and add to list
        #issue with ASIN = B004NK6DFE <- fixed
        if ("SimilarViewedProduct" in cart and _safe_get_element_text('Title', root.Cart.SimilarViewedProducts.SimilarViewedProduct) is not None):
            for item2 in root.Cart.SimilarViewedProducts.SimilarViewedProduct:
                #print _safe_get_element_text('Title', item) #testing
                #print item2.ASIN #testing
                svlist.append({'Original ASIN':item,
                               'Associated ASIN':item2.ASIN,
                               'Title':item2.Title,
                               'Price': None,
                               'Currency Code':None,
                               'Relationship':"Also Viewed"})

    print 'Total # of \"Also Viewed\" Products: ' + str(len(svlist))
    count = 0 #testing

    #iterate through each also viewed prodcut and obtain lowest price
    print 'Retrieving prices!' #testing
    for item in svlist:
        if item['Title'] is not None:
            title = filter(lambda x: x in string.printable, item['Title'].text) #remove non-ascii
            item['Title'] = title
            #print title #testing
        count+=1 #testing
        print count #testing
        #print 'Associated ASIN: ' + str(item['Associated ASIN'])
        pricelist = amazon.ItemLookup(ItemId=item['Associated ASIN'],ResponseGroup="OfferSummary,VariationSummary")
        priceroot = objectify.fromstring(pricelist)
        #conditionals to check if parent or child ASIN or OOS, Variation pricing can only be called on parent
        if _safe_get_element_text("Items.Item.OfferSummary.LowestNewPrice.FormattedPrice", priceroot) is not None: #Child ASIN
            item['Price'] = _safe_get_element_text('Items.Item.OfferSummary.LowestNewPrice.FormattedPrice', priceroot)
            item['Currency Code'] = _safe_get_element_text('Items.Item.OfferSummary.LowestNewPrice.CurrencyCode', priceroot)
        else:
            item['Price'] = _safe_get_element_text('Items.Item.VariationSummary.LowestPrice.FormattedPrice', priceroot)
            item['Currency Code'] = _safe_get_element_text('Items.Item.VariationSummary.LowestPrice.CurrencyCode', priceroot)
    return svlist


def generate_csv(lists, output_file):
    """Writes the given platforms into a CSV file specified by the output_file
    parameter.

    The output_file can either be the path to a file or a file-like object.
    """
    if os.path.isfile(output_file):
        with open(output_file, 'a') as file:
            dataset = tablib.Dataset()
            for l in lists:
                dataset.append([l['Original ASIN'], l['Associated ASIN'], l['Title'], l['Price'], l['Currency Code'], l['Relationship']])
            file.write(dataset.csv)
    else:
        with open(output_file, 'w+') as fp:
            dataset = tablib.Dataset(headers=['Original ASIN', 'Associated ASIN', 'Title', 'Price', 'Currency Code', 'Relationship'])
            for l in lists:
                dataset.append([l['Original ASIN'], l['Associated ASIN'], l['Title'], l['Price'], l['Currency Code'], l['Relationship']])
            fp.writelines(dataset.csv)
    """
    if isinstance(output_file, basestring):
        with open(output_file, 'w+') as fp:
            fp.writelines(dataset.csv)
    else:
        output_file.writelines(dataset.csv)"""


def main():
    #initialize start time
    start = time.time()

    #testing
    single = "/Users/Thoshi64/bottle/AmazonTestDataSingle.csv"
    shortest = "/Users/Thoshi64/bottle/AmazonTestDataShortest.csv"
    shorter = "/Users/Thoshi64/bottle/AmazonTestDataShorter.csv"
    short = "/Users/Thoshi64/bottle/AmazonTestDataShort.csv"
    normal = "/Users/Thoshi64/bottle/AmazonTestData.csv"

    """for i in range(10):
        if (i == 0 or i == 1):
            list = pA.parse(shortestx2,",")
        elif (i == 2 or i == 3):
            list = pA.parse(shortest,",")
        elif(i == 4 or i == 5):
            list = pA.parse(shorter,",")
        elif (i == 6 or i == 7):
            list = pA.parse(short,",")
        else:
            list = pA.parse(normal,",")"""
    for i in range(1):
        #parse the input file
        list = pA.parse(normal,",")

        #get also view and bought products
        list2 = get_similar_products(list)
        list3 = get_viewed_products(list)

        #generate the final output csv file
        generate_csv(list2, 'AlsoBoughtViewedProducts_' + str(i) + '.csv')
        generate_csv(list3, 'AlsoBoughtViewedProducts_' + str(i) + '.csv')
        #print 'done with ' + str(i) + '!'
        #generate_csv(list2, 'SimilarProducts-SimilarViewed.csv')
        #generate_csv(list3, 'SimilarProducts-SimilarViewed.csv')

    print 'ALL DONE!'
    print 'It took', float(time.time()-start)/60.0, 'minutes.' #returns time to complete



    """non ascii testing
    product = amazon.ItemLookup(ItemId='B0046KIJ12')
    root = objectify.fromstring(product)
    title = _safe_get_element_text('Title', root.Items.Item.ItemAttributes)
    print title
    fixedtitle = filter(lambda x: x in string.printable, title)
    print fixedtitle"""




    """params = {"Item.1.ASIN":'B00G7LEZUW', 'Item.1.Quantity':1, 'ResponseGroup':'Cart,CartSimilarities'}
    cart = amazon.CartCreate(**params)
    root = objectify.fromstring(cart)
    for item in root.Cart.SimilarViewedProducts.SimilarViewedProduct:
        print filter(lambda x: x in string.printable, _safe_get_element_text('Title', item))"""





if __name__ == "__main__":
    main()






"""
#how to create cart
params = {"Item.1.ASIN": 'B000DLB2FI', 'Item.1.Quantity':1}
cartresponse = amazon.CartCreate(**params)
rootcart = objectify.fromstring(cartresponse)
CartId = rootcart.Cart.CartId
print CartId
#CartItemId = rootcart.Cart.CartItemId
#print CartItemId
HMAC = rootcart.Cart.HMAC
print HMAC



#how to get similar products and similar viewed products
cart2 = amazon.CartGet(CartId=CartId, HMAC = HMAC, ResponseGroup='CartSimilarities')
root2 = objectify.fromstring(cart2)
print "SimilarProduct"
for item in root2.Cart.SimilarProducts.SimilarProduct:
    print item.ASIN

print "SimilarViewedProduct"

for item in root2.Cart.SimilarViewedProducts.SimilarViewedProduct:
    print item.ASIN


#how to get lowest and highest price
#Variation pricing can only be called on Parent it seems

#child
product = amazon.ItemLookup(ItemId="B000072UPN", ResponseGroup='Small, OfferSummary, VariationSummary')
root5 = objectify.fromstring(product)
print root5.Items.Item.ItemAttributes.Title
print product
#print root3.Items.Item.LowestPrice.FormattedPrice

#parent
product2 = amazon.ItemLookup(ItemId="B00006XXGO", ResponseGroup='Small, OfferSummary, VariationSummary')
root3 = objectify.fromstring(product2)
print root3.Items.Item.ItemAttributes.Title
print product2
"""
