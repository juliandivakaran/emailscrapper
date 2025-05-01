import requests
from bs4 import BeautifulSoup
from fastapi.responses import HTMLResponse
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import *
import multiprocessing
import time
import random

from database.database import print_scraped_words


class url_separation(ThreadPoolExecutor):
    def __init__(self,max_crawl=2000):
        self.success_urls = []
        self.error_urls = []
        self.max_crawl = max_crawl or multiprocessing.cpu_count() * 2
        print(f"[URLSeparation] Available CPU cores: {multiprocessing.cpu_count()}")
        print(f"[URLSeparation] Max worker threads set to: {self.max_crawl}")


    def fetch_url(self, web_url):
        print(web_url)
        print(f"[fetch_url] Fetching: {web_url}")
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
            }
            response = requests.get(web_url, headers=headers, timeout=10)
            response.raise_for_status()
            sleep_time =  random.uniform(8, 15)
            print(f"[fetch_url] Sleeping for {sleep_time:.2f} seconds to avoid rate-limiting.")
            time.sleep(sleep_time)
            self.success_urls.append(web_url)
            return response.text

        except:
            print("Something went wrong")
            self.error_urls.append(web_url)
            return None

    def report(self):
        print(f"\nTotal Successful URLs: {len(self.success_urls)}")
        print(f"Total Failed URLs: {len(self.error_urls)}")


    def run(self, web_url):
        if not web_url.endswith('/'):
            web_url += '/'

        urls_to_visit = [web_url]
        visited_urls = set()
        crawl_count = 0
        print(f"[URLSeparation] Starting crawl with {self.max_crawl} worker threads.")

        with ThreadPoolExecutor(max_workers = self.max_crawl) as executor:
            while urls_to_visit:
                future_to_url = {executor.submit(self.fetch_url, url): url for url in urls_to_visit}
                urls_to_visit = []

                for future in as_completed(future_to_url):
                    current_url = future_to_url[future]

                    try:
                        result = future.result()
                        if result is None:
                            continue

                        soup = BeautifulSoup(result, "html.parser")
                        link_elements = soup.select("a[href]")

                        for link_element in link_elements:
                            url = link_element["href"]
                            absolute_url = requests.compat.urljoin(web_url, url)

                            if absolute_url.startswith(web_url) and absolute_url not in visited_urls:
                                urls_to_visit.append(absolute_url)
                                visited_urls.add(absolute_url)

                        crawl_count += 1  # One page processed!

                    except Exception as e:
                        print(f"Error processing {current_url}: {e}")

            #print(f"all {len(visited_urls)}")
            return list(visited_urls)


class Scrapper:
    def __init__(self):
        cpu_cores = multiprocessing.cpu_count() * 2
        print(f"[Scrapper] Available CPU cores: {cpu_cores}")
        print(f"[Scrapper] Max worker threads set to: 10")


    def run(self, visited_urls):
        all_scraped_text = []

        with ThreadPoolExecutor(max_workers=20) as executor:
            future_to_url = {executor.submit(self.scrape, url): url for url in visited_urls}

            for future in as_completed(future_to_url):
                result = future.result()
                if result and 'text' in result:
                    all_scraped_text.append(result['text'])


        combined_text = ' '.join(all_scraped_text)
        words = combined_text.split()
        """
        count = 0
        for word in words:
            print(f"[Scrapper] Scraping {count} words...: {word}")
            count +=1
            """
        #count = len(words)
        print_scraped_words(words)
        return all_scraped_text

    def scrape(self, url):
        print(f"Scraping {url}")
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "lxml")

            for script in soup(["script", "style"]):
                script.decompose()

            text = soup.get_text(separator=' ', strip=True)
            cleaned_text = re.sub(r"\s+", " ", text)

            return {'url': url, 'text': cleaned_text}

        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return {'url': url, 'error': str(e)}















"""
max_crawl = 200

def fetch_url(web_url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }
        response = requests.get(web_url, headers=headers)
        response.raise_for_status()
        return response.text

    except Exception as e:
        print(e)
        return web_url, None


def crawler(web_url):

    if not web_url.endswith('/'):
        web_url += '/'

    urls_to_visit = [web_url]
    visited_urls = set()
    crawl_count = 0

    with ThreadPoolExecutor(max_workers=10) as executor:
        while urls_to_visit and crawl_count < max_crawl:
            future_to_url = {executor.submit(fetch_url, url): url for url in urls_to_visit}
            urls_to_visit = []

            for future in as_completed(future_to_url):
                current_url = future_to_url[future]

                try:
                    result = future.result()
                    if result is None:
                        continue

                    soup = BeautifulSoup(result, "html.parser")
                    link_elements = soup.select("a[href]")

                    for link_element in link_elements:
                        url = link_element["href"]
                        absolute_url = requests.compat.urljoin(web_url, url)

                        if absolute_url.startswith(web_url) and absolute_url not in visited_urls:
                            urls_to_visit.append(absolute_url)
                            visited_urls.add(absolute_url)

                    crawl_count += 1  # One page processed!

                except Exception as e:
                    print(f"Error processing {current_url}: {e}")

    return list(visited_urls)




def scraper(visited_urls):
    all_scraped_text = []
    if visited_urls:  # make sure the list is not empty
        #craw_url = len(visited_urls)
        for index, crawl_url in enumerate(visited_urls):
            print(f'crawling {crawl_url}')
            try:
                html_content = requests.get(crawl_url).text
                soup = BeautifulSoup(html_content, "lxml")

                for script in soup(["script", "style"]):
                    script.decompose()

                text = soup.get_text(separator=' ', strip=True)
                cleaned_text = re.sub(r"\s+", " ", text)

                all_scraped_text.append(
                    {
                    'url': crawl_url,
                    'text':cleaned_text
                }
                )

            except Exception as e:
                print(f'error scraping{crawl_url}:{e}')
                all_scraped_text.append({
                    'url': crawl_url,
                    'error':str(e)
                })
                return None


        #print(soup.title.text())
    else:
        print("No URLs found.")
        return None

    return all_scraped_text

"""






