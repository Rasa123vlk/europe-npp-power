import pandas as pd
from os import getenv
from elexonapi import Client
from dotenv import load_dotenv
from datetime import datetime, date

# 1. Initialize the modern Insights API client
# Get your free API key at: https://bmrs.elexon.co.uk/
load_dotenv()
API_TOKEN = getenv("API_TOKEN_GB")
client = Client(api_key=API_TOKEN)

# 2. Known UK Nuclear BM Unit ID Mapping (Add or adjust active stations as needed)
NUCLEAR_BMU_MAP = {
    'T_SIZB-1': 'Sizewell B - Unit 1',
    'T_SIZB-2': 'Sizewell B - Unit 2',
    'T_TORN-1': 'Torness - Unit 1',
    'T_TORN-2': 'Torness - Unit 2',
    'T_HEYB1-1': 'Heysham 2 - Unit 1',
    'T_HEYB1-2': 'Heysham 2 - Unit 2',
    'T_HEYA1-1': 'Heysham 1 - Unit 1',
    'T_HEYA1-2': 'Heysham 1 - Unit 2',
    'T_HART-1': 'Hartlepool - Unit 1',
    'T_HART-2': 'Hartlepool - Unit 2',
}

def get_actual_nuclear_generation(target_date: str):
    """
    Fetches raw BMU unit outputs (B1610) for a given date string (YYYY-MM-DD)
    and filters specifically for UK Nuclear units.
    """
    print(f"Fetching B1610 generation data for {target_date}...")
    
    # Query the generation/actual/per-unit (B1610) endpoint using the wrapper
    # It returns data in a structured format that we can feed to Pandas
    raw_data = client.get_generation_actual_per_unit(
        settlementDate=target_date, 
        format="json"
    )
    
    # Load into DataFrame
    df = pd.DataFrame(raw_data)
    
    if df.empty:
        print("No data returned for this date.")
        return None
        
    # Filter for our designated nuclear plant IDs
    df_nuclear = df[df['bmUnit'].isin(NUCLEAR_BMU_MAP.keys())].copy()
    
    # Map BMU IDs to human-readable names
    df_nuclear['Plant Name'] = df_nuclear['bmUnit'].map(NUCLEAR_BMU_MAP)
    
    # Clean up column selections (Adjust depending on precise JSON output schema)
    # Typically includes: settlementDate, settlementPeriod, quantity (MWh)
    summary = df_nuclear[['Plant Name', 'bmUnit', 'settlementPeriod', 'quantity']]
    
    return summary

# Example usage (Fetch data for yesterday)
target_day = date.today().isoformat()
nuclear_df = get_actual_nuclear_generation(target_day)

if nuclear_df is not None:
    # Print the latest settlement period available in the dataset
    latest_period = nuclear_df['settlementPeriod'].max()
    print(f"\n--- Plant Output (MWh) for Settlement Period {latest_period} ---")
    
    latest_output = nuclear_df[nuclear_df['settlementPeriod'] == latest_period]
    print(latest_output.to_string(index=False))