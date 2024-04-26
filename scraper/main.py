import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import threading

def scrape_links(url):
    """Scrapes links from a given URL, handling potential errors."""
    #print(url)
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        links = [link.get('href') for link in soup.find("div", class_="post-indent").find_all('a', attrs={'rel': 'nofollow', 'target': '_blank'})]
        return links
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve {url}: {e}")
        return []  # Return empty list on error

def scrape_page(url):
    """Scrapes post data from a given URL, handling potential errors."""
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        post_data = []

        post_titles = soup.find_all("h2", class_="post-title")
        for post_title in post_titles:
            title_element = post_title.find("a")
            if title_element:
                title = title_element.text.strip()
                href = title_element.get("href")
                post_data.append({
                    "title": title,
                    "link": href,
                    "links": []  # Placeholder for scraped links (fetched later)
                })

        # Fetch links for each post in a separate thread (potential bottleneck)
        threads = []
        for post in post_data:
            thread = threading.Thread(target=lambda url=post['link']: post['links'].extend(scrape_links(url)))
            thread.start()
            threads.append(thread)

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

        return post_data
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve {url}: {e}")
        return []  # Return empty list on error

def scrape_range(start_year, start_month, end_year, end_month):
    """Scrapes data within a date range, utilizing threading."""
    base_url = "https://w14.monkrus.ws/{}/{:02d}/"
    data = []

    current_year = start_year
    current_month = start_month

    while (current_year, current_month) >= (end_year, end_month):
        url = base_url.format(current_year, current_month)
        print(url)

        # Create and start a thread for scraping the page
        thread = threading.Thread(target=lambda url=url: data.extend(scrape_page(url)))
        thread.start()
        thread.join()  # Wait for the thread to finish before moving on

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
