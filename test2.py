import os
from os import getenv
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from entsoe import EntsoePandasClient
import pandas as pd
import requests

load_dotenv()
API_TOKEN = getenv("API_TOKEN")
WEBHOOK_URL = getenv("WEBHOOK_URL")

client = EntsoePandasClient(api_key=API_TOKEN)

now = datetime.now(timezone.utc)
end = pd.Timestamp(now.replace(minute=0, second=0, microsecond=0) - timedelta(days=5))
start = end - timedelta(hours=1)

country_code = "CZ"

# Actual generation per unit (nuclear = B14)
gen_per_unit = client.query_generation_per_plant(
    country_code, start=start, end=end, psr_type="B14"
)

# Installed nominal capacity per unit (nuclear = B14)
capacity_per_unit = client.query_installed_generation_capacity_per_unit(
    country_code, psr_type="B14", start=start, end=end
)

timestamp = start

print(gen_per_unit)
df = gen_per_unit

message = f"**Reactor production — {timestamp}**\n\n"

for unit in df.columns.get_level_values(0).unique():
    value = df.loc[timestamp, unit].iloc[0]
    print(f"{unit}: {value} MW")
    message += f"`{unit}`: **{value} MW**\n"


response = requests.post(
    WEBHOOK_URL,
    json={"content": message}
)

print(response.status_code)

#print(capacity_per_unit)