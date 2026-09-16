import json

INPUT_FILE = "unit_dictionary_unkown.json"
OUTPUT_FILE = "unit_dictionary_new.json"


# Names and nominal powers that you want to fill in.
# Add/edit entries here.
UNIT_INFO = {
    "EDUK_B1____": {
        "name": "Dukovany 1",
        "nominal_power": 512
    },
    "EDUK_B2____": {
        "name": "Dukovany 2",
        "nominal_power": 512
    },
    "EDUK_B3____": {
        "name": "Dukovany 3",
        "nominal_power": 512
    },
    "EDUK_B4____": {
        "name": "Dukovany 4",
        "nominal_power": 512
    },
    "ETEM_G1____": {
        "name": "Temelín 1",
        "nominal_power": 1092
    },
    "ETEM_G2____": {
        "name": "Temelín 2",
        "nominal_power": 1092
    }
}


with open(INPUT_FILE, "r", encoding="utf-8") as file:
    old_dictionary = json.load(file)


new_dictionary = {}

for country, units in old_dictionary.items():

    new_dictionary[country] = {}

    for unit in units:

        if unit in UNIT_INFO:
            new_dictionary[country][unit] = UNIT_INFO[unit]

        else:
            new_dictionary[country][unit] = {
                "name": unit,
                "nominal_power": None
            }


with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
    json.dump(
        new_dictionary,
        file,
        indent=4,
        ensure_ascii=False
    )


print(f"Saved: {OUTPUT_FILE}")