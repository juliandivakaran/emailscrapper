import time
from googleapiclient.discovery import build
#from channelprocess.input import keywords
from database.retriview_key_words import get_keyword_list
from datetime import datetime, timedelta
# YouTube API Key
API_KEY = "AIzaSyDZwaX7U_eOb2wGHI_YuPsQkMt8SOP4GFg"

# Keywords to search for
SEARCH_QUERIES = get_keyword_list()
MAX_RESULTS = 50  # Max allowed per request
TOTAL_IDS_NEEDED = 5000  # Goal

current_start = datetime.strptime('2016-01-01T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')
def iso_format(dt):
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')

# Initialize YouTube API client
youtube = build("youtube", "v3", developerKey=API_KEY)

def get_channel_ids(search_queries, max_results, total_needed):
    collected_count = 0
    request_count = 0
    seen_channel_ids = set()
    current_end = current_start + timedelta(seconds=1)

    for query in search_queries:
        print(f"\n Searching for: {query}")
        next_page_token = None

        while collected_count < total_needed and request_count < 1000:
            request = youtube.search().list(
                q=query,
                type="channel",
                part="snippet",
                publishedAfter=iso_format(current_start),
                publishedBefore=iso_format(current_end),
                maxResults=max_results,
                pageToken=next_page_token
            )
            response = request.execute()
            request_count += 1

            for item in response.get("items", []):
                channel_id = item["id"]["channelId"]

                if channel_id not in seen_channel_ids:
                    seen_channel_ids.add(channel_id)
                    channel_name = item["snippet"]["title"]
                    channel_created_date = item["snippet"]["publishedAt"]

                    print(f" {collected_count+1}. {channel_name} ({channel_id}) — Created on {channel_created_date}")
                    collected_count += 1

                if collected_count >= total_needed:
                    break

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

            time.sleep(1)  # Respect API limits

        if collected_count >= total_needed:
            break

    print(f"\n Collected {collected_count} unique channel IDs.")
    return collected_count

# For external usage
def get_channel_ids_api():
    return get_channel_ids(SEARCH_QUERIES, MAX_RESULTS, TOTAL_IDS_NEEDED)

# Run the script directly
if __name__ == "__main__":
    get_channel_ids(SEARCH_QUERIES, MAX_RESULTS, TOTAL_IDS_NEEDED)
