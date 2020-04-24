from flask import Flask, render_template,Markup
from flask_pymongo import PyMongo

import scrape_mars  

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_db"
mongo = PyMongo(app)
#db = mongo.mars_db

@app.route("/")
def home_page():
    mars_info = mongo.db.mars.find_one()
    news_data=mars_info['news_data']
    featured_image = mars_info['featured_image_url']
    weather=mars_info['mars_weather']
    mars_facts=mars_info['mars_facts']
    hemisphere_image_urls = mars_info['mars_hemispheres']

    return render_template("index.html",
        news_data=news_data,
        featured_image=featured_image,
        weather=weather,
        mars_facts=mars_facts,
        hemisphere_image_urls = hemisphere_image_urls
        )

@app.route("/scrape")
def scrape():
    scrape_mars.scrape()
    return render_template('done.html')        

if __name__ == "__main__":
    app.run(debug=True)    