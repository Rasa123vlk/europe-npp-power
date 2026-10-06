import requests
import pandas as pd

url = "https://data.elexon.co.uk/bmrs/api/v1/datasets/PN"

params = {
    "from": "2026-09-10T00:00:00Z",
    "to": "2026-09-11T00:00:00Z",
    "format": "json",
}

response = requests.get(url, params=params)

print("Status:", response.status_code)
print("URL:", response.url)
print("Content-Type:", response.headers.get("Content-Type"))

print(response.text[:2000])

response.raise_for_status()

data = response.json()

print(type(data))

if isinstance(data, dict):
    print(data.keys())

df = pd.DataFrame(data.get("data", data))

print(df.head())
print(df.columns.tolist())