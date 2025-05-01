import uvicorn
from fastapi import FastAPI, BackgroundTasks,Query
from channelprocess.filter import get_channel_ids_api
from scrapper.scrap import scraping
from channelprocess.wordscraper.keyworks_scraper import *
from typing import List
from datetime import datetime
import os
from database.database import fetc_last_record
from database.retriview_key_words import get_keyword_list
app = FastAPI()

@app.get("/databasekeyword")
async def database_keyword():
    get_keyword_list()

@app.get("/home")
async def root():
    return {"message": "Hello World"}


@app.get("/scrap_data_from_youtube_api")
async def scrape_channels_details():
    get_channel_ids_api()
    #return {"message": "Channel scraping completed!"}
    return {"message": "Channel scraping completed!"}

@app.get("/scrap_email_from_youtube")
async def scrap_email_from_channel_ID_video_id(background_tasks: BackgroundTasks):
    background_tasks.add_task(scraping)
    return {"message": "Channel fetch completed!"}

#from dotenv import load_dotenv
#load_dotenv()
url_helper = url_separation()
scrapper_helper = Scrapper()
@app.get("/keywords_generator")
async def keywords(link: List[str] =Query(..., Description="Enter the url to Scrap: ")):
    all_results = {}
    words = {}
    for url in link:
        visited_urls = url_helper.run(url)
        scraped_data = scrapper_helper.run(visited_urls)
        all_results[url] = scraped_data
        combined_text = ' '.join(scraped_data)
        word_list =  combined_text.split()
        words[url] =word_list

        fetc_last_record()


    return {
        "message": "Keywords scraping completed!",
        "total_input_links": len(link),
        "scraped_results": all_results
    }




#main
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)

