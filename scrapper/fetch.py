import database.database as db
import requests
import queue

#create a queue to store the channel URLs
input_queue_channels_url = queue.Queue()

def get_channel_ids_from_db():
    collection = db.db['channels']
    channel_ids = []
    try:
        channels = collection.find({},{'_id':0, 'channel_id':1})

        #adding orginal url to queue
        for channel in channels:
            feed = ("https://www.youtube.com/channel/"+channel['channel_id']+"/about")
            input_queue_channels_url.put(feed)
            #print(feed)

        print(f"Found {input_queue_channels_url.qsize()} channels")


    except Exception as e:
        print(e)

    return channel_ids



def process_channels():
    while not input_queue_channels_url.empty():
        url = input_queue_channels_url.get()
        #print(f"Processing URL: {url}")
        input_queue_channels_url.task_done()

if __name__ == "__main__":
    get_channel_ids_from_db()
    process_channels()