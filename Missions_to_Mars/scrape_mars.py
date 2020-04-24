from bs4 import BeautifulSoup
from splinter import Browser
import os
import pandas as pd
import time
import pymongo


def initializeMongo():
    conn = 'mongodb://localhost:27017'
    client = pymongo.MongoClient(conn)
    db = client.mars_db
    collection = db.mars
    collection.drop() # if it exists drop it 
    return db.mars


def saveMongo(data):
    collection = initializeMongo()
    collection.insert_one(data)

def initializeBrowser():
     # Chromedriver windows
    executable_path = {'executable_path': 'chromedriver.exe'}
    return Browser('chrome', **executable_path, headless=False)    

def cleanupBrowser(browser):
    browser.quit()

def scrape():
    ## 
    browser = initializeBrowser()
    mars_data = {}
    mars_data["news_data"] = marsNews(browser)
    mars_data["featured_image_url"] = marsFeaturedImageURL(browser)
    mars_data["mars_weather"] = marsTwitterWeather(browser)
    mars_data["mars_facts"] = marsFacts(browser)
    mars_data["mars_hemispheres"] = marsHemisphereImageURLs(browser)
    saveMongo(mars_data)
    cleanupBrowser(browser)

    # 
    # return mars_data dict
    return mars_data    

def marsNews(browser):
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)
    html = browser.html
    soup = BeautifulSoup(html,"html.parser")
    time.sleep(10) # Need to wait for page to load for some reason

    article_list = soup.find('ul',class_='item_list')
    latest_title = article_list.find("div",class_="content_title").text
    latest_paragraph = article_list.find("div", class_="article_teaser_body").text
    print(f"Title     : {latest_title}")
    print(f"Paragraph : {latest_paragraph}")
    return {"title":latest_title,'paragraph':latest_paragraph}

def marsFeaturedImageURL(browser):
    # JPL Featured Mars Featured image
    root_url = 'https://www.jpl.nasa.gov'
    url_image = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(url_image)

    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    #lets get mars image
    image_list = soup.find('li', class_="slide")
    images = image_list.find('a', class_='fancybox')
    image_txt = images.find_all('div','article_teaser_body')
    image_text = ""
    for txt in image_txt:
        image_text +=txt.text.lstrip()
        #print(txt.text.lstrip())
    print(image_text)    
    image_ref = images['data-fancybox-href']
    featured_url = root_url + image_ref
    print(featured_url)
    #Image(url= featured_url)
    return {'featured_url':featured_url,'featured_desc':image_text}

def marsTwitterWeather(browser):
    weather_url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(weather_url)
    html = browser.html

    # Parse HTML with Beautiful Soup
    soup = BeautifulSoup(html, 'html.parser')

    ## TODO --- Need to figure out how to parse twitter

    mars_weather="""
    InSight sol 498 (2020-04-21) low -94.3ºC (-137.7ºF) high -5.7ºC (21.8ºF)
    winds from the SW at 5.0 m/s (11.3 mph) gusting to 16.6 m/s (37.2 mph)
    pressure at 6.60 hPa"""

    return mars_weather


def marsFacts(browser):
    facts_url = 'https://space-facts.com/mars/'
    facts_df = pd.read_html(facts_url)
    mars_facts = facts_df[0]
    mars_facts.columns = ["Category", "Fact"]
    html_table = mars_facts.to_html()
    return html_table


def marsHemisphereImageURLs(browser):    

    print("Hemisphere")
    hemispheres_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(hemispheres_url)
    time.sleep(10) 
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    
    hemisphere_image_urls = []
    
    hemispheres = soup.find_all('div','item')
    for hemisphere in hemispheres:
        name = hemisphere.find('div', class_='description')
        title_text = name.h3.text
        browser.click_link_by_partial_text(title_text)
        usgs_html = browser.html
        usgs_soup = BeautifulSoup(usgs_html, 'html.parser')
        img_url = usgs_soup.find('div', class_='downloads').ul.li.a['href']
        hemisphere_image_urls.append({'title': title_text, 'img_url': img_url})
    # go back 
        browser.back()

    print(hemisphere_image_urls)
    return hemisphere_image_urls


if __name__ == "__main__":
    scrape()