import os
from os import getenv
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from entsoe import EntsoePandasClient
import pandas as pd
import requests
import json

# Loads unit real names
with open("unit_dictionary.json", "r", encoding="utf-8") as file:
    unit_names = json.load(file)

load_dotenv()
API_TOKEN = getenv("API_TOKEN")
WEBHOOK_URL = getenv("WEBHOOK_URL")

client = EntsoePandasClient(api_key=API_TOKEN)

country_code = "CZ"

def fetch_newest_data():
    cycle = 0
    while True:
        try:    
            now = datetime.now(timezone.utc)
            end = pd.Timestamp(now.replace(minute=0, second=0, microsecond=0) - timedelta(hours=cycle))
            start = end - timedelta(hours=1)
            # Actual generation per unit (nuclear = B14)
            gen_per_unit = client.query_generation_per_plant(country_code, start=start, end=end, psr_type="B14")

            if not gen_per_unit.empty:
                print(f"Data found: {start} -> {end}")
                break
            
            print(f"No data: {start} -> {end}")
            cycle += 1
        except Exception as e:
            print(f"Skipping cycle {cycle}")
            cycle += 1
            continue

    # Installed nominal capacity per unit (nuclear = B14)
    capacity_per_unit = client.query_installed_generation_capacity_per_unit(country_code, psr_type="B14", start=start, end=end)
    return start, gen_per_unit, capacity_per_unit
    
start, gen_per_unit, capacity_per_unit = fetch_newest_data()

timestamp = start

print(gen_per_unit)
df = gen_per_unit
df = df.rename(
    columns=lambda x: unit_names.get(x, x),
    level=0
)

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

print(capacity_per_unit)