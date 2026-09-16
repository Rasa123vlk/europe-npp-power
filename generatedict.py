import os
import json
from datetime import datetime, timedelta, timezone

import pandas as pd
from dotenv import load_dotenv
from entsoe import EntsoePandasClient


load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")

client = EntsoePandasClient(api_key=API_TOKEN)


# ENTSO-E country/control-area codes
COUNTRIES = [
    "AL",  # Albania
    "AT",  # Austria
    "BA",  # Bosnia and Herzegovina
    "BE",  # Belgium
    "BG",  # Bulgaria
    "CH",  # Switzerland
    "CZ",  # Czechia
    "DE_LU",  # Germany/Luxembourg
    "DK_1",   # Denmark West
    "DK_2",   # Denmark East
    "EE",  # Estonia
    "ES",  # Spain
    "FI",  # Finland
    "FR",  # France
    "GB",  # Great Britain
    "GR",  # Greece
    "HR",  # Croatia
    "HU",  # Hungary
    "IE",  # Ireland
    "IT_NORTH",  # Italy North
    "IT_CNOR",   # Italy Central North
    "IT_CSUD",   # Italy Central South
    "IT_SUD",    # Italy South
    "IT_SICI",   # Sicily
    "IT_SARD",   # Sardinia
    "LT",  # Lithuania
    "LU",  # Luxembourg
    "LV",  # Latvia
    "ME",  # Montenegro
    "MK",  # North Macedonia
    "NL",  # Netherlands
    "NO_1",  # Norway
    "NO_2",
    "NO_3",
    "NO_4",
    "NO_5",
    "PL",  # Poland
    "PT",  # Portugal
    "RO",  # Romania
    "RS",  # Serbia
    "SE_1",  # Sweden
    "SE_2",
    "SE_3",
    "SE_4",
    "SI",  # Slovenia
    "SK",  # Slovakia
    "TR",  # Türkiye
    "UA",  # Ukraine
]


def get_nuclear_units(country_code):
    """
    Get all nuclear generation-unit IDs reported by ENTSO-E
    for a country/control area.
    """
    now = datetime.now(timezone.utc)
    end = pd.Timestamp(now.replace(minute=0, second=0, microsecond=0) - timedelta(days=5))
    start = end - timedelta(hours=1)


    try:
        df = client.query_generation_per_plant(
            country_code,
            start=start,
            end=end,
            psr_type="B14"
        )

        if df.empty:
            return []

        # First column level contains the ENTSO-E unit IDs
        units = df.columns.get_level_values(0).unique()

        return sorted(units.tolist())

    except Exception as e:
        print(f"{country_code}: skipped ({e})")
        return []


def main():

    unit_dictionary_unkown = {}

    for country in COUNTRIES:

        print(f"Checking {country}...")

        units = get_nuclear_units(country)

        if not units:
            continue

        unit_dictionary_unkown[country] = {}

        for unit in units:
            unit_dictionary_unkown[country][unit] = ""

            print(f"    {unit}")

    with open(
        "unit_dictionary_unkown.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            unit_dictionary_unkown,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\nSaved unit_dictionary_unkown.json")


if __name__ == "__main__":
    main()