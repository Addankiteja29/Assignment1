import requests
from bs4 import BeautifulSoup
import json

# Scraping Function
def scrape_nifty_data(redis_client):
    url = 'https://www.nseindia.com/'
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the Nifty 50 table or data (modify this as per actual HTML structure)
        nifty_table = soup.find('table', {'id': 'nifty50'})  # Ensure this matches the correct ID or class
        rows = nifty_table.find_all('tr')

        # Collecting the required data
        nifty_data = []
        for row in rows:
            columns = row.find_all('td')
            if columns:
                company = columns[0].text.strip()
                last_price = columns[1].text.strip()
                change = columns[2].text.strip()

                nifty_data.append({
                    'company': company,
                    'last_price': last_price,
                    'change': change
                })

        # Store in Redis
        redis_client.set("nifty_data", json.dumps(nifty_data))

    except Exception as e:
        print(f"Error scraping data: {e}")
