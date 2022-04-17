from bs4 import BeautifulSoup as soup

from urllib.request import urlopen

import re


if __name__ == '__main__':

    """----------------------web scraping prices of graphics cards from newegg.com----------------------------------
     1) Specify file to write data to and open it.
     2)  create headers for data and write them to the csv file.
     3) Assign url to variable then open, read and close the webpage.

     4) Use beautifulSoup to parse the text in the correct language so that it can be navigated/accessed and modified
     5) Find all item-cells on the page that contain an id
     6) Extract number of pages from first page
     7) for the second page to last page, scrape the data in each cell and write it to csv.
    
      7.1) finding all item containers, branding containers, title containers and shipping containers
      7.2) getting the brand, product name and shipping price from their respective containers
           ...then assign each to a variable
      7.3) Deal with formatting edge cases
      7.4) print each output for each data variable in console  [optional]
      7.5) write data to specified (csv) file. 

     8) close csv file.
       """

    # 1) specify a file in the local directory where you want to write the scraped data to and open file in write mode
    file_name = "gcards.csv"
    f = open(file_name, "w")

    # 2) create headers for (csv) file. Csv files are delimited by a comma (columns) and '\n'(rows) .
    # write headers into csv file.
    headers = "brand, product_price, product_name, shipping_price\n"
    f.write(headers)

    # 3) Assign url to variable, Connect to webpage, download markup
    # Read webpage into page_html' and close connection to webpage'
    first_page = 'https://www.newegg.com/p/pl?d=graphics+cards'

    url_client = urlopen(first_page)
    page_html = url_client.read()
    url_client.close()

    # 4) soup() method will convert the string of html so the html markup can....
    # this is done by using the appropriate parser included in the soup package.
    parsed_html = soup(page_html, "html.parser")

    # 5) finds all 'divs that have the html class called item-cell.
    cells = parsed_html.find_all("div", {"id": re.compile(r"^item_cell")})

    # 6)  extract number of pages from first page (scrape_url) then...
    # generate urls in range of page numbers
    pagination = parsed_html.find("span", {"class": "list-tool-pagination-text"})
    page_range = str(pagination.strong).strip("</strong>")
    page_num = int(page_range.partition("/<!-- -->")[2])
    print(len(cells))
    pages = (first_page + "&page=" + str(page) for page in range(1, page_num+1))

    # 7) for the second page to last page, scrape the data in each cell
    for page in pages:
        if page == first_page + "&page=1":
            page = first_page
            print("this is the first page", page)
        else:
            print("this is page", page)
            url_client = urlopen(page)
            page_html = url_client.read()
            url_client.close()
            parsed_html = soup(page_html, "html.parser")
            cells = parsed_html.find_all("div", {"id": re.compile(r"^item_cell")})
            print(len(cells))

        for cell in cells:

            # 7.1) finding all item containers, branding containers, title containers and shipping containers
            container = cell.find("div", {"class": "item-container"})
            title_container = container.find("a", {"class": "item-title"})
            shipping_container = container.find("li", {"class": "price-ship"})
            price_container = container.find("li", {"class": "price-current"})
            branding_container = container.find("div", {"class": "item-branding"})

            # 7.2) getting data from containers .
            # Edge case handling employed for tag doesnt exist or attribute does not exist.
            if hasattr(branding_container.a, "img"):
                if hasattr(branding_container.a.img, "title"):
                    print("banding has img att")
                    brand = branding_container.a.img["title"].replace(",", " ")
            else:
                brand = "NULL"

            if hasattr(price_container.strong, "text"):

                price_major = price_container.strong.text
                price_minor = price_container.sup.text
            else:
                price_major = "NULL"
                price_minor = "NULL"

            if hasattr(title_container, "text"):
                product_name = title_container.text.strip()

            else:
                product_name = "NULL"

            if hasattr(shipping_container, "text"):
                shipping = shipping_container.text.strip()
            else:
                shipping = "NULL"

            # 7.3) edge case cleaning and standardising data
            # replacing substrings with digit characters
            product_name = product_name.replace("\n", "|")

            if shipping.find("Free Shipping") != -1:
                shipping = "0"
            elif shipping.find("$") != -1:
                shipping = shipping.replace("$", "")
                shipping = shipping.replace("Shipping", "")
            elif shipping.find("Special") != -1:
                shipping = "0"

            # 7.4) print brand to console.( Optional) - comment out for increased performance
            print("Brand: " + brand)
            print("Price ($): " + price_major.replace(",", "") + price_minor.replace(",", ""))
            print("Product_Name : " + product_name)
            print("Shipping ($) : " + shipping)

            # 7.5) brand, product_name and shipping can contain commas which affect the position of the data in the csv
            f.write(brand + "," + price_major.replace(",", "") + price_minor.replace(",", "")
                    + "," + product_name.replace(",", "|") + "," + shipping + "," + "\n")

        # 8)
    f.close()
