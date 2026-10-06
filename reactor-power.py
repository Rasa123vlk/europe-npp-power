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

country_code = {"CZ", "SK", "FR",}

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
        cycle = 0 #set higher for testing
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
    country = countries.lower()
    date_text = start.strftime("%d.%m.%Y")
    message = f"**Reactor power for {countries} :flag_{country}: on {date_text}**\n"
    message += "```ansi\n"
    for unit in df.columns.get_level_values(0).unique():
        value = df.loc[timestamp, unit].iloc[0]
            
        try:
            info = unit_dictionary_output(countries, unit)
            name = info[0]
            nominal_power = info[1]

            if nominal_power is not None:
                relativ_value = round(value / nominal_power * 100)

                if relativ_value > 80:
                    power_color = COLOR_GREEN
                elif relativ_value < 5:
                    power_color = COLOR_RED
                else:
                    power_color = COLOR_ORANGE

                message += (
                    f"{COLOR_BLUE}{name}{COLOR_RESET}: "
                    f"{power_color}{value} MW ({relativ_value}%){COLOR_RESET}\n"
                )

            else:
                print(f"{unit}: nominal power is not defined")
                message += (
                    f"{COLOR_BLUE}{name}{COLOR_RESET}: "
                    f"{value} MW\n"
                )

        except Exception as e:
            print(f"{unit} not found in dictionary: {e}")
            message += (
                f"{COLOR_BLUE}{unit}{COLOR_RESET}: "
                f"{value} MW\n"
            )
            
    # End of message
    message += "```"

    response = requests.post(
        WEBHOOK_URL,
        json={"content": message}
    )

    print(response.status_code)

    print(capacity_per_unit)