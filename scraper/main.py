import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import threading
import time

def scrape_links(url):
    """Scrapes links from a given URL, handling errors."""
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        return [link.get('href') for link in soup.find("div", class_="post-indent").find_all('a', attrs={'rel': 'nofollow', 'target': '_blank'})]
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve {url}, trying again in 5 seconds...")
        time.sleep(5)
        return scrape_links(url)

def process_post(post):
    post["links"] = scrape_links(post["link"])

def scrape_page(url):
    """Scrapes post data and links from a given URL, handling errors."""
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        post_data = []

        for post_title in soup.find_all("h2", class_="post-title"):
            title_element = post_title.find("a")
            if title_element:
                title = title_element.text.strip()
                href = title_element.get("href")
                post_data.append({
                    "title": title,
                    "link": href,
                    "links": []
                })

        threads = []
        for post in post_data:
            thread = threading.Thread(target=process_post, args=(post,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

        return post_data
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve {url}, trying again in 5 seconds...")
        time.sleep(5)
        return scrape_page(url)


def scrape_range(start_year, start_month, end_year, end_month):
    """Scrapes data within a date range, utilizing threading."""
    base_url = "https://w14.monkrus.ws/{}/{:02d}/"
    data = []

    current_year = start_year
    current_month = start_month

    while (current_year, current_month) >= (end_year, end_month):
        url = base_url.format(current_year, current_month)
        print(url)

        # Scrape page data with links in a single thread
        data.extend(scrape_page(url))

        current_month -= 1
        if current_month < 1:
            current_month = 12
            current_year -= 1

    return data


# Main execution
current_date = datetime.now()

start_year, start_month = current_date.year, current_date.month
end_year, end_month = 2010, 11

result_data = scrape_range(start_year, start_month, end_year, end_month)

if result_data:
    with open("scraped_data.json", "w", encoding="utf-8") as json_file:
        json.dump(result_data, json_file, ensure_ascii=False, indent=2)

    print("Data saved successfully to scraped_data.json.")
else:
    print("No data to save.")
