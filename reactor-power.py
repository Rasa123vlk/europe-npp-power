import os
from os import getenv
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from entsoe import EntsoePandasClient
import pandas as pd
import requests
import json
from colors import *

load_dotenv()
API_TOKEN = getenv("API_TOKEN")
WEBHOOK_URL = getenv("WEBHOOK_URL")

client = EntsoePandasClient(api_key=API_TOKEN)

country_code = {"CZ", "SK"}

# Loads unit real names and nominal power

with open("unit_dictionary_new.json", "r", encoding="utf-8") as file:
    unit_dictionary = json.load(file)
def unit_dictionary_output(country: str, unit: str):
    unit_names = unit_dictionary[country][unit]["name"]
    nominal_power = unit_dictionary[country][unit]["nominal_power"]
    return unit_names, nominal_power

def fetch_newest_data():
    generation_data = {}
    for countries in country_code:
        cycle = 30 #set higher for testing
        while True:
            try:    
                now = datetime.now(timezone.utc)
                end = pd.Timestamp(now.replace(minute=0, second=0, microsecond=0) - timedelta(hours=cycle))
                start = end - timedelta(hours=1)
                # Actual generation per unit (nuclear = B14)
                gen_per_unit = client.query_generation_per_plant(countries, start=start, end=end, psr_type="B14")

                if not gen_per_unit.empty:
                    print(f"Data found: {start} -> {end}")
                    capacity_per_unit = client.query_installed_generation_capacity_per_unit(countries, psr_type="B14", start=start, end=end)
                    generation_data[countries] = {
                        "start": start,
                        "end": end,
                        "gen_per_unit": gen_per_unit,
                        "capacity_per_unit": capacity_per_unit,
                    }

                    break
                
                print(f"No data: {start} -> {end}")
                cycle += 1
            except Exception as e:
                print(f"Skipping cycle {cycle}")
                cycle += 1
                continue

    # Installed nominal capacity per unit (nuclear = B14)
    return generation_data

generation_data = fetch_newest_data()
for countries in country_code:
    start = generation_data[countries]["start"]
    gen_per_unit = generation_data[countries]["gen_per_unit"]
    capacity_per_unit = generation_data[countries]["capacity_per_unit"]

    timestamp = start

    print(gen_per_unit)
    df = gen_per_unit
    #renames all columns accodrding to dictionary
    #start of message
    date_text = start.strftime("%d.%m.%Y")
    message = f"**Reactor power for {countries} on {date_text}**\n"
    message += "```ansi\n"
    for unit in df.columns.get_level_values(0).unique():
        value = df.loc[timestamp, unit].iloc[0]

        info = unit_dictionary_output(countries, unit)

        if info:
            name = info[0]
            nominal_power = info[1]
        else:
            name = unit
            nominal_power = "Unknown"

        if int(value) > 98:
            power_color = COLOR_GREEN
        elif int(value) < 1:
            power_color = COLOR_RED
        else:
            power_color = COLOR_ORANGE

        #advanced stuff
        #bold_begin = COLOR_BOLD if changed else ""
        #bold_end = f"{COLOR_RESET} {COLOR_CYAN}[prev: {previous_day_power}]{COLOR_RESET}" if changed else ""
        
        value = df.loc[timestamp, unit].iloc[0]
        print(f"{unit}: {value} MW")
        relativ_value = round(value / nominal_power * 100)
        message += f"{COLOR_BLUE}{name}{COLOR_RESET}: {power_color}{value} MW ({relativ_value}%){COLOR_RESET}\n"

    # End of message
    message += "```"

    response = requests.post(
        WEBHOOK_URL,
        json={"content": message}
    )

    print(response.status_code)

    print(capacity_per_unit)