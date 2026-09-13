"""Download one indicator from the World Bank API and save it to data/raw/.

Run this script once, from the top folder of the repository:

    python scripts/pull_data.py

It writes two files into data/raw/:

  1. A raw .json file, exactly as the API sent it.
  2. A tidy .csv file, ready for your analysis.

Commit both files. Your report reads the saved copy, never the live API.
That is what lets the container render the same report in December.

The script is written for beginners, so it is longer and more commented
than it needs to be. Change the settings in the CONFIGURATION block and
the rest will follow.
"""

import json
from pathlib import Path

import pandas as pd
import requests

# ---------------------------------------------------------------------
# CONFIGURATION: change these three settings for your own project
# ---------------------------------------------------------------------

# The World Bank indicator code. This one is life expectancy at birth.
# Browse the codes at https://data.worldbank.org/indicator
INDICATOR = "SP.DYN.LE00.IN"

# The countries you want, as ISO three-letter codes, joined by ";".
# BRA is Brazil, IND is India, NGA is Nigeria, USA is the United States.
COUNTRIES = "BRA;IND;NGA;USA"

# The years to cover, written as "first:last".
YEARS = "2000:2023"

# A short, readable name for the output files.
OUTPUT_NAME = "life_expectancy"

# ---------------------------------------------------------------------
# The rest of the script rarely needs changing
# ---------------------------------------------------------------------

# Where the files go. Path(__file__) is this script, .parent is the
# scripts/ folder, and .parent again is the top of the repository. Building
# the path this way means the script works from any working directory.
RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

# The address of the World Bank Indicators API.
# The API needs no key and no registration.
BASE_URL = "https://api.worldbank.org/v2"


def fetch_indicator(indicator: str, countries: str, years: str) -> list:
    """Ask the API for one indicator and return the parsed JSON response."""
    url = f"{BASE_URL}/country/{countries}/indicator/{indicator}"

    # These are the query parameters, the part after "?" in a web address.
    # format=json asks for JSON instead of the API's default XML.
    # per_page=20000 asks for everything in one response, so we do not
    # have to request page after page.
    params = {
        "format": "json",
        "date": years,
        "per_page": 20000,
    }

    print(f"Requesting {url}")

    # timeout=60 stops the script from hanging forever if the API is slow.
    response = requests.get(url, params=params, timeout=60)

    # raise_for_status() turns an HTTP error, such as 404 or 500, into a
    # Python error with a clear message, instead of letting the script
    # carry on with a response that contains no data.
    response.raise_for_status()

    payload = response.json()

    # The World Bank wraps its answer in a two-item list. The first item
    # is information about the response, such as how many rows there are.
    # The second item is the actual data.
    if not isinstance(payload, list) or len(payload) < 2:
        raise RuntimeError(f"Unexpected response from the API: {payload}")

    return payload


def tidy(payload: list) -> pd.DataFrame:
    """Turn the nested API response into a flat table."""
    records = payload[1]

    if records is None:
        raise RuntimeError("The API returned no rows. Check your codes and years.")

    # Each record is a dictionary with nested pieces, for example
    # {"country": {"id": "BR", "value": "Brazil"}, "date": "2020", ...}.
    # We pull out the few fields we want and drop the rest.
    rows = [
        {
            "country_code": record["countryiso3code"],
            "country": record["country"]["value"],
            "indicator": record["indicator"]["id"],
            "year": int(record["date"]),
            "value": record["value"],
        }
        for record in records
    ]

    frame = pd.DataFrame(rows)

    # Rows with no value are years the World Bank has not measured.
    # dropna() removes them here, so that the report does not have to.
    # sort_values puts the rows in a predictable order, country first and
    # then year, and reset_index renumbers them from 0 afterwards.
    frame = frame.dropna(subset=["value"])
    frame = frame.sort_values(["country", "year"]).reset_index(drop=True)

    return frame


def main() -> None:
    # mkdir(parents=True, exist_ok=True) creates data/raw/ if it is
    # missing, and stays quiet if it already exists.
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    payload = fetch_indicator(INDICATOR, COUNTRIES, YEARS)

    # Save the untouched response first. If you later discover a mistake
    # in the tidying step, you can fix it without calling the API again.
    json_path = RAW_DIR / f"{OUTPUT_NAME}_raw.json"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Saved the raw response to {json_path}")

    frame = tidy(payload)

    # index=False keeps pandas from adding its own row-number column,
    # which is not part of the data and would confuse anyone reading the CSV.
    csv_path = RAW_DIR / f"{OUTPUT_NAME}.csv"
    frame.to_csv(csv_path, index=False)
    print(f"Saved {len(frame)} tidy rows to {csv_path}")

    print("\nFirst few rows:")
    print(frame.head())

    print("\nNow commit both files in data/raw/ to your repository.")


# This line means "only run main() when the file is executed directly".
# It stays quiet if another file imports this one.
if __name__ == "__main__":
    main()
