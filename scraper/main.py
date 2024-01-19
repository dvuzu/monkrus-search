import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

def scrape_page(url):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")

        post_data = []
        post_titles = soup.find_all("h2", class_="post-title")

        for post_title in post_titles:
            title_element = post_title.find("a")
            if title_element:
                title = title_element.text.strip()
                href = title_element.get("href")
                post_data.append({"title": title, "link": href})

        return post_data
    else:
        print("Failed to retrieve the web page. Status code:", response.status_code)
        return None

def scrape_range(start_year, start_month, end_year, end_month):
    base_url = "https://w14.monkrus.ws/{}/{:02d}/"
    data = []

    current_year = start_year
    current_month = start_month

    while (current_year, current_month) >= (end_year, end_month):
        print(str(current_year)+"/"+str(current_month))

        url = base_url.format(current_year, current_month)
        page_data = scrape_page(url)
        
        if page_data:
            data.extend(page_data)

        # Move to the next month
        current_month -= 1
        if current_month < 1:
            current_month = 12
            current_year -= 1

    return data

# Get the current date and time
current_date = datetime.now()

start_year, start_month = current_date.year, current_date.month
end_year, end_month = 2010, 11 # Date of first monkrus post

result_data = scrape_range(start_year, start_month, end_year, end_month)

if result_data:
    with open("scraped_data.json", "w", encoding="utf-8") as json_file:
        json.dump(result_data, json_file, ensure_ascii=False, indent=2)

    print("Data saved successfully to scraped_data.json.")
else:
    print("No data to save.")
