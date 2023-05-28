import requests
from bs4 import BeautifulSoup
import csv
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Function to send a GET request with retries and delay
def send_get_request(url, headers):
    session = requests.Session()
    retry_strategy = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    response = session.get(url, headers=headers)
    return response

# Send a GET request to the URL
base_url = "https://www.amazon.in/s?k=bags&ref=sr_pg_{}"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
}

filename = "amazon_products.csv"

# Create a CSV file and write headers
with open(filename, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Product Name", "Product Price", "Product Rating", "Product URL", "Number of Ratings", "Description", "ASIN", "Product Description", "Manufacturer"])

    # Iterate through the next 20 pages
    for page in range(1, 21):
        url = base_url.format(page)

        # Send a GET request with retries and delay
        response = send_get_request(url, headers)
        response.raise_for_status()

        # Parse the HTML content
        soup = BeautifulSoup(response.content, "html.parser")

        # Find all the product containers
        product_containers = soup.find_all("div", {"data-component-type": "s-search-result"})

        # Extract information from each product container and write to the CSV file
        for container in product_containers:
            # Extract the product name
            product_name = container.find("span", {"class": "a-size-medium"})
            if product_name:
                product_name = product_name.text.strip()

            # Extract the product price
            product_price = container.find("span", {"class": "a-price-whole"})
            if product_price:
                product_price = product_price.text.strip()

            # Extract the product rating
            product_rating = container.find("span", {"class": "a-icon-alt"})
            if product_rating:
                product_rating = product_rating.text.strip()

            # Extract the product URL
            product_url = container.find("a", {"class": "a-link-normal"})
            if product_url:
                product_url = "https://www.amazon.in" + product_url["href"]

                # Send a GET request to the product URL with retries and delay
                product_response = send_get_request(product_url, headers)
                product_response.raise_for_status()

                # Parse the product HTML content
                product_soup = BeautifulSoup(product_response.content, "html.parser")

                # Extract additional information
                description_element = product_soup.find("span", {"id": "productTitle"})
                if description_element:
                    description = description_element.text.strip()
                else:
                    description = ""

                asin_element = product_soup.find("th", string="ASIN")
                if asin_element:
                    asin = asin_element.find_next("td").text.strip()
                else:
                    asin = ""

                product_description_element = product_soup.find("div", {"id": "productDescription"})
                if product_description_element:
                    product_description = product_description_element.text.strip()
                else:
                    product_description = ""

                manufacturer_element = product_soup.find("a", {"id": "bylineInfo"})
                if manufacturer_element:
                    manufacturer = manufacturer_element.text.strip()
                else:
                    manufacturer = ""

                # Extract the number of ratings
                num_ratings = container.find("span", {"class": "a-size-base"})
                if num_ratings:
                    num_ratings = num_ratings.text.strip()
                else:
                    num_ratings = ""

                # Write the data to the CSV file
                writer.writerow([product_name, product_price, product_rating, product_url, num_ratings, description, asin, product_description, manufacturer])

        print("Page", page, "scraped successfully.")

        # Delay between requests
        time.sleep(1)

print("Data extracted and saved to", filename)
