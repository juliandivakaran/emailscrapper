from httpcore import TimeoutException
from scrapper.fetch import get_channel_ids_from_db, process_channels, input_queue_channels_url
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
import time
from lxml import html
import re


def display():
    get_channel_ids_from_db()
    """# Populates the queue
    temp_list = list(input_queue_channels_url.queue)
    for url in temp_list:
        print(url)
    process_channels()         # Processes the queue"""
    if not input_queue_channels_url.empty():
        first_url = input_queue_channels_url.queue[100]
        print(first_url)
        return first_url

def scraping():
    #target url we need to scrap
    target_url = display()
    #about_url = generate_youtube_about_url(target_url)

    #selenium configurations
    driver_path = r"C:\Users\user\Desktop\EmailScrapper\tools\geckodriver.exe"
    firefox_options = Options()
    firefox_options.add_argument("--headless")
    service = Service(driver_path)
    driver = webdriver.Firefox(service=service, options=firefox_options)


    try:
        driver.get(target_url)
        time.sleep(3)
        # Wait for the element to be visible before interacting with it

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="link-list-container"]'))
        )
        about_container = driver.find_element(By.XPATH, '//*[@id="link-list-container"]')
        about_html = about_container.get_attribute("innerHTML")
        # Parse the HTML with lxml
        tree = html.fromstring(about_html)
        links = tree.xpath("//a")  # Select all anchor tags
        print("Extracted External Links:")
        for link in links:
            label = link.text_content().strip()
            href = link.get("href", "").strip()

            # Format nicely
            print(f"{label}\n")

           #email _______________________________________________________

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH,'//*[@id="additional-info-container"]'))
            )
            more_container = driver.find_element(By.XPATH, '//*[@id="additional-info-container"]')
            more_info = more_container.get_attribute("innerHTML")
            #print(more_info)
            tree2 = html.fromstring(more_info)
            more_informations = tree2.xpath("//a")
            for more_information in more_informations:
                more_label = more_information.text_content().strip()
                print(f"{more_label}\n")

    except TimeoutException:
        print("The element could not be located within the given time.")

    finally:
        driver.quit()

if __name__ == "__main__":
    display()
