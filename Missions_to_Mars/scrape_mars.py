# Import Dependancies
import pandas as pd
import requests
import time
import datetime as dt
from splinter import Browser
from bs4 import BeautifulSoup as bs
from webdriver_manager.chrome import ChromeDriverManager

# Create function to hold scrape items
def scrape_all():
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=False)

    news_title, news_p =  scrape_mars_news(browser)
    hemisphere_image_urls = get_hemispheres(browser)

    # Scrapped items 
    data = {
        "news_title": news_title,
        "news_p": news_p,
        "featured_image": scrape_featured_images(browser),
        "facts": scrape_mars_facts(),
        "hemispheres": get_hemispheres(browser), 
        "last_modified": dt.datetime.now()
    }
    # Quit browser and return web scrape data
    browser.quit()
    return data

############ News Title & Paragraph ############

def scrape_mars_news(browser):
    url = "https://redplanetscience.com/"
    browser.visit(url)
    browser.is_element_present_by_css("div.list_text", wait_time=4)

    html = browser.html
    soup = bs(html, "html.parser")

    try:
        element = soup.select_one("div.list_text")
        news_title = element.find("div", class_="content_title").get_text()
        news_p = element.find("div", class_="article_teaser_body").get_text()
    except:
        return None, None
    
    return news_title, news_p

############ Featured Image ############

def scrape_featured_images(browser):
    url = "https://spaceimages-mars.com" 
    browser.visit(url)

    browser.find_by_tag("button")[1].click()

    html = browser.html
    soup = bs(html, "html.parser")

    try:
        img_url_path = soup.find("img", class_="fancybox-image").get("src")
    except:
        return None
    return f"{url}/{img_url_path}"

############ Scrape Mars news title and paragraph ############

def scrape_mars_facts():
    url = "https://galaxyfacts-mars.com"

    try:
        df = pd.read_html(url)[0]
        df.columns = ["Description", "Mars", "Earth"]
        df.set_index("Description", inplace=True)
        return df.to_html(classes="table table-stripped")
    except:
        return None

############ Hemisphere and Title ############

def get_hemispheres(browser):
    url = "https://marshemispheres.com/"

    browser.visit(url + "index.html")

    hemisphere_image_urls=[]

    for i in range(4):
        browser.find_by_css("a.product-item img")[i].click()
        data = _scrape_hemisphere(browser.html)
        data["img_url"] = url + data["img_url"]
        hemisphere_image_urls.append(data)
        browser.back()
        
    return hemisphere_image_urls

def _scrape_hemisphere(html_text):
    soup = bs(html_text, 'html.parser')

    try:
        title = soup.find("h2", class_="title").get_text()
        sample_element = soup.find("a", text="Sample").get("href")
    except:
        title, sample_element = None, None

    return {
        "title": title,
        "img_url": sample_element
    }

# End scrape and print all
if __name__ == "__main__":
    print(scrape_all())
