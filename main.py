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

Client = EntsoeRawClient(api_key=API_TOKEN)

"""now = datetime.now(timezone.utc)

start = now.replace(minute=0, second=0, microsecond=0)

end = start - timedelta(hours=4)
start = end - timedelta(hours=3)

start = start.strftime('%Y%m%d%H%M')
end = end.strftime('%Y%m%d%H%M')"""


now = datetime.now(timezone.utc)
start = pd.Timestamp('20171201', tz='Europe/Brussels')
end = pd.Timestamp('20180101', tz='Europe/Brussels')
print(start)
print(end)


country_code = "CZ"

#1045.30 (VARY) Temelín nominal
#480.00 (VARY) Dukovany nominal


"""params = {
    "securityToken": API_TOKEN,
    "documentType": "A75",
    "processType": "A16",
    "in_Domain": "10YCZ-CEPS-----N", #27W-GU-EDUKB1, 27W-PU-EDUK----1 , 
    "registeredResource": "27W-GU-EDUKB1-4",
    "periodStart": start,
    "periodEnd": end
}

response = requests.get(url, params=params)"""

response = Client.query_generation_per_plant(country_code, start, end, psr_type=None)
with open('outfile.xml', 'w') as f:
    f.write(response)

print("Data downloaded")
