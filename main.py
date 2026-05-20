import os
from os import getenv
from dotenv import load_dotenv
import requests
import bs4
from bs4 import BeautifulSoup
import datetime
from datetime import datetime, timedelta, timezone

load_dotenv()

API_TOKEN = getenv("API_TOKEN")
WEBHOOK_URL = getenv("WEBHOOK_URL")

url = "https://web-api.tp.entsoe.eu/api"

now = datetime.now(timezone.utc)

start = now.replace(minute=0, second=0, microsecond=0)

end = start - timedelta(hours=2)
start = end - timedelta(hours=1)

start = start.strftime('%Y%m%d%H%M')
end = end.strftime('%Y%m%d%H%M')

params = {
    "securityToken": API_TOKEN,
    "documentType": "A73",
    "processType": "A16",
    "in_Domain": "10YCZ-CEPS-----N", #27W-GU-EDUKB1, 27W-PU-EDUK----1 , 
    "registeredResource": "27W-GU-EDUKB1-4",
    "periodStart": start,
    "periodEnd": end
}

response = requests.get(url, params=params)

print(response.text)
