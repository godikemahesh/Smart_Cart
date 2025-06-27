import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import time
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9"
}

# 1️⃣ Flipkart





#HEADERS = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
# }


def scrape_shopclues(query, max_results=1):
    url = f"https://www.shopclues.com/search?q={query.replace(' ', '+')}"
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    products = []

    for item in soup.select(".column.col3.search_blocks"):
        title = item.select_one(".prod_name")
        link = item.select_one("a")
        image = item.select_one("img")
        price = item.select_one(".p_price")
        rating = item.select_one(".star_rating")  # Ratings often not available

        # Description from the listing page (fallback)
        discription = ""
        if link and "href" in link.attrs:
            product_url = link["href"]
            try:
                product_resp = requests.get(product_url, headers=HEADERS)
                product_soup = BeautifulSoup(product_resp.text, "html.parser")
                desc = product_soup.select_one(".spec_scroll")
                if desc:
                    discription = desc.get_text(strip=True)
            except:
                discription = ""

        if title and link and image and price:
            products.append({
                "title": title.get_text(strip=True),
                "price": price.get_text(strip=True),
                "rating": rating.get_text(strip=True) if rating else "N/A",
                "reviews": "N/A",  # ShopClues usually hides reviews
                "image": image["src"],
                "link": link["href"],
                "description": discription
            })

        if len(products) >= max_results:
            break

    return products


# 2️⃣ Amazon
def scrape_amazon(query, max_results=2):
    url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    products = []
    description=""
    b_points=""
    for item in soup.select(".s-result-item"):
        title = item.select_one("h2 span")
        link = item.select_one("a.a-link-normal")
        image = item.select_one("img")
        price_whole = item.select_one(".a-price-whole")
        price_frac = item.select_one(".a-price-fraction")
        price_offscreen = item.select_one(".a-price .a-offscreen")
        rating = item.select_one(".a-icon-alt")
        bullet_points = soup.select("#feature-bullets ul li span")
        if bullet_points:
            b_points= " | ".join([point.text.strip() for point in bullet_points if point.text.strip()])

        # Fallback to productDescription div
        desc_div = soup.select_one("#productDescription")
        if desc_div:
            description= desc_div.text.strip()
        description+=b_points
        if title and link and image:
            if price_offscreen:
                price = price_offscreen.text.strip()
            elif price_whole and price_frac:
                price = price_whole.text.strip() + price_frac.text.strip()
            else:
                price = "N/A"
            products.append({
                "title": title.text.strip(),
                "price": "" + price,
                "rating": rating.text.strip().split(" ")[0] if rating else "N/A",
                "reviews": "N/A",  # Amazon hides reviews in JS
                "image": image["src"],
                "link": "https://www.amazon.in" + link["href"],
                "description": description
            })

        if len(products) >= max_results:
            break

    return products


# 3️⃣ Meesho
def scrape_meesho(query, max_results=1):
    products = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        url = f"https://www.meesho.com/search?q={query.replace(' ', '%20')}"
        page.goto(url)
        page.wait_for_timeout(5000)  # Wait for content to load

        soup = BeautifulSoup(page.content(), "html.parser")
        cards = soup.select(".SearchProduct__ProductWrapper-sc-__sc-1r82m12-0")

        for card in cards:
            title = card.select_one("p")
            price = card.select_one("h5")
            image = card.select_one("img")
            link = card.select_one("a")

            if title and price and image and link:
                products.append({
                    "title": title.text.strip(),
                    "price": price.text.strip(),
                    "rating": "Coming Soon 😅",  # Still tricky in Meesho
                    "reviews": "Coming Soon 😅",
                    "image": image["src"],
                    "link": "https://www.meesho.com" + link["href"],
                    "description": title.text.strip()
                })

            if len(products) >= max_results:
                break

        browser.close()

    return products



# 4️⃣ Snapdeal
def scrape_snapdeal(query, max_results=2):
    url = f"https://www.snapdeal.com/search?keyword={query.replace(' ', '%20')}"
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    products = []

    for item in soup.select(".product-tuple-listing"):
        title = item.select_one(".product-title")
        price = item.select_one(".product-price")
        image = item.select_one("img")
        link = item.select_one("a.dp-widget-link")
        rating = item.select_one(".filled-stars")

        if title and price and image and link:
            products.append({
                "title": title.text.strip(),
                "price": price.text.strip(),
                "rating": rating['style'].split(":")[1] if rating else "N/A",
                "reviews": "N/A",
                "image": image["src"],
                "link": link["href"],
                "description":title.text.strip()

            })

        if len(products) >= max_results:
            break

    return products


# 🔄 Combine All Platforms
def scrape_all(query, platforms):
    results = {}
    if "Amazon" in platforms:
        results["Amazon"] = scrape_amazon(query)
    if "Shopclues" in platforms:
        results["Shopclues"] = scrape_shopclues(query)
    if "Meesho" in platforms:
        results["Meesho"] = scrape_meesho(query)
    if "Snapdeal" in platforms:
        results["Snapdeal"] = scrape_snapdeal(query)
    return results



result=scrape_shopclues("mobiles")
print(result)
