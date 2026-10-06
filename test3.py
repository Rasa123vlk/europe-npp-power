import csv
import requests


CSV_FILE = "dictionary.csv"

SETTLEMENT_DATE = "2026-10-03"
SETTLEMENT_PERIOD = 21

PN_URL = "https://data.elexon.co.uk/bmrs/api/v1/datasets/PN"


# ============================================================
# LOAD DICTIONARY
# ============================================================

with open(CSV_FILE, "r", encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Loaded {len(rows)} rows")


# ============================================================
# FIND NUCLEAR BMUs
# ============================================================

# dictionary_id -> BMUs
nuclear_bmus = {}


for row in rows:

    attribute = str(row.get("attribute", "")).strip()
    value_id = str(row.get("id", "")).strip()
    value = str(row.get("value", "")).strip()
    dictionary_id = str(row.get("dictionary_id", "")).strip()
    id_type = str(row.get("id_type", "")).strip()

    # We only care about:
    #
    # Fuel Type | HINB-7 | NUCLEAR | ... | ngc_bmu_id | 10133
    #
    if attribute.lower() != "fuel type":
        continue

    if value.upper() != "NUCLEAR":
        continue

    if id_type != "ngc_bmu_id":
        continue

    if not value_id:
        continue

    nuclear_bmus.setdefault(dictionary_id, []).append(value_id)


print()
print("Nuclear BMUs:")
print("=" * 50)

for dictionary_id, bmus in nuclear_bmus.items():
    print(dictionary_id, bmus)


# ============================================================
# GET PLANT INFORMATION
# ============================================================

# dictionary_id -> information
plants = {}


for row in rows:

    dictionary_id = str(
        row.get("dictionary_id", "")
    ).strip()

    if dictionary_id not in nuclear_bmus:
        continue

    attribute = str(
        row.get("attribute", "")
    ).strip()

    value = str(
        row.get("value", "")
    ).strip()

    plants.setdefault(dictionary_id, {})

    plants[dictionary_id][attribute] = value


# ============================================================
# GET PN DATA
# ============================================================

params = {
    "SettlementDate": SETTLEMENT_DATE,
    "SettlementPeriod": SETTLEMENT_PERIOD,
    "format": "json",
}

response = requests.get(
    PN_URL,
    params=params,
    timeout=30
)

print()
print("PN status:", response.status_code)
print("PN URL:", response.url)

response.raise_for_status()

data = response.json()


# ============================================================
# EXTRACT RECORDS
# ============================================================

if isinstance(data, list):

    records = data

elif isinstance(data, dict):

    records = None

    for key in ("data", "results", "items"):

        if isinstance(data.get(key), list):
            records = data[key]
            break

    if records is None:
        raise RuntimeError(
            "Could not find PN records in response"
        )

else:

    raise RuntimeError(
        f"Unexpected response type: {type(data)}"
    )


# ============================================================
# CREATE BMU -> PN MAPPING
# ============================================================

pn_by_bmu = {}

for item in records:

    if not isinstance(item, dict):
        continue

    national_grid_bmu = item.get(
        "nationalGridBmUnit"
    )

    if not national_grid_bmu:
        continue

    pn_by_bmu[national_grid_bmu] = item


# ============================================================
# MATCH NUCLEAR PLANTS
# ============================================================

print()
print("NUCLEAR GENERATION")
print("=" * 60)


for dictionary_id, bmus in nuclear_bmus.items():

    plant = plants.get(dictionary_id, {})

    # Try to find a useful plant name.
    name = (
        plant.get("Name")
        or plant.get("name")
        or f"Dictionary ID {dictionary_id}"
    )

    total_power = 0
    found = False

    for bmu in bmus:

        item = pn_by_bmu.get(bmu)

        if item is None:
            continue

        power = item.get("levelFrom")

        if power is None:
            power = item.get("levelTo")

        if power is None:
            continue

        total_power += float(power)
        found = True

    if found:

        print(
            f"{name}: {total_power:.0f} MW"
        )

    else:

        print(
            f"{name}: NO PN DATA"
        )