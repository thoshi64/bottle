#Readme

#Requirements
-used Python 2.7.5        
-BeautifulSoup -> pip install beautifulsoup4    
-lxml -> pip install lxml    
-requests -> pip install requests     
-tablib -> pip install tablib    
-bottlenose -> pip install bottlenose    

#What to Execute


-test.py -> will output a csv of "also bought" and "also viewed" products -> ~30 min to complete   
    -you will need to change in main() the path for the normal file before executing   
    -you will need to include an access key, secret access key, and associate tag for the AWS and Associate account
  
-description.py -> will output a csv of the descriptions -> ~3 min to complete   
    -you will need to change in main() the path for the normal file before executing    

#Example Final Outputs
Should anything malfunction, I included outputs for when I ran the scripts labeled as "AlsoBoughtViewedProducts_Final.csv" and "DescriptionsList_Final.csv"

#Thought Process
I started with understanding the different ways to scrape off Amazon and came to the conslusion of two alternatives, scrape through html and using the Amazon Product Advertising API.  The Amazon API doesn't offer an option for pulling descriptions so I was forced to pull the html and filter through that using BeautifulSoup.    

-test.py
  The script uses parseAmazon.py to parse the input csv given into an output list of ASINs.  That list is then fed into the get_similar_products and get_viewed_products.  The ouput lists from those calls are fed into generate_csv to create the final output file.     
  
  -In the output csv file, if the price and currency code show "None" it's because the product is out of stock.  Else if it shows "Too Low to Display" this is because of the MAP by the manufacturer.  Should the price go below the MAP, Amazon requires the shopper to add and view the price in the cart through the webpage.  
  
-description.py
  Luckily BeautifulSoup exists to help filter out information from html.  It made writing this script much easier.  There are still a few kinks to work out with the ouput format but all the descriptions are there that have them.

Challenges

-Finding the highest price for "also bought" products
  -In the API you can only call the highest price using the VariationSummary response group which in turn can only be called on a parent ASIN.  I wrote the method to check if the associated ASIN is a child or parent and grab the highest price from there.  If it was a child, I grabbed the ParentASIN from the Cart response group. 

-Extra bugs
  -The majority of challenges was dealing with the unstructured data that would be returned at times.  To list a few, the title sometimes included a trademark symbol that needed to be removed, one of the ASINs returned wonky "also viewed" products and kept crashing the script, testing for if there are any "also viewed" or "also bought" products.  All of these challenges led to fixes in the code but I most likely did not account for all of them since I am limited by the dataset and time constraint.
  


