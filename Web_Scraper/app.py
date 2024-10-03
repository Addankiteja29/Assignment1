from flask import Flask, render_template
import redis
from apscheduler.schedulers.background import BackgroundScheduler
from scraper import scrape_nifty_data
import json

app = Flask(__name__)

# Initialize Redis client
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# Function to get data from Redis
def get_nifty_data():
    data = redis_client.get("nifty_data")
    if data:
        return json.loads(data)
    return []

# Background job to scrape data every 5 minutes
def start_scraping():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=scrape_nifty_data, trigger="interval", minutes=5, args=[redis_client])
    scheduler.start()

# Route to display Nifty 50 data
@app.route('/')
def index():
    data = get_nifty_data()
    return render_template('index.html', nifty_data=data)

if __name__ == '__main__':
    start_scraping()
    app.run(debug=True)
