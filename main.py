import os
from os import getenv
from dotenv import load_dotenv
import requests
import bs4
from bs4 import BeautifulSoup
import datetime
from datetime import datetime, timedelta, timezone
from entsoe import EntsoePandasClient
from entsoe import EntsoeRawClient
import pandas as pd

load_dotenv()

API_TOKEN = getenv("API_TOKEN")
WEBHOOK_URL = getenv("WEBHOOK_URL")

url = "https://web-api.tp.entsoe.eu/api"

client = EntsoePandasClient(api_key=API_TOKEN)

now = datetime.now(timezone.utc)

start = now - timedelta(hours=2)
end = now - timedelta(hours=1)

start = start.strftime("%Y%m%d%H00")
end = end.strftime("%Y%m%d%H00")

print(start)
print(end)

country_code = "CZ"

#ETEM_G1__ Temelin
#1085 / 1125 (VARY) Temelín nominal
#27W-GU-EDUKB1--4 Dukovany U1
#530.00 (VARY) Dukovany nominal


payload = {
    "securityToken": API_TOKEN,
    "documentType": "A73",
    "processType": "A16",
    "in_Domain": "10YCZ-CEPS-----N",
    "periodStart": "202605281100",
    "periodEnd": "202605281200",
}

response = requests.get(url, params=payload)

print(response.text)

with open('outfile.xml', 'w') as f:
    f.write(response.text)

print("Data downloaded")
