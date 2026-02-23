"""
Download ABS (Australian Bureau of Statistics) historical data.

Key ABS sources:
1. Historical Agricultural Data Cube (1860-2022) - released April 2024
   Added to Agricultural Commodities, Australia 2021-22 edition
2. Livestock Products, Australia (cat. 7215.0) - quarterly xlsx
3. Value of Agricultural Commodities Produced (cat. 7503.0)
4. Australian Agriculture: Livestock (replaces the above from 2023-24)
"""

import requests
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "abs"

HEADERS = {
    "User-Agent": "AusDairyStats/1.0 (academic research project)"
}

# ABS data files
ABS_URLS = {
    # Livestock Products quarterly - recent editions with time series
    "livestock_products_dec2025": "https://www.abs.gov.au/statistics/industry/agriculture/livestock-products-australia/latest-release/72150DO002_202512.xlsx",
    "livestock_products_sep2025": "https://www.abs.gov.au/statistics/industry/agriculture/livestock-products-australia/sep-2025/72150DO002_202509.xlsx",

    # Agricultural Commodities 2021-22 (final edition, includes historical data cube)
    # The historical data cube URL pattern - try several possible formats
    "ag_commodities_2021_22": "https://www.abs.gov.au/statistics/industry/agriculture/agricultural-commodities-australia/2021-22/71210DO001_202122.xlsx",

    # Australian Agriculture: Livestock 2023-24
    "ag_livestock_2023_24": "https://www.abs.gov.au/statistics/industry/agriculture/australian-agriculture-livestock/2023-24/71870DO001_202324.xlsx",
}

# ABS Year Book historical data - these may be available as scanned PDFs
# We'll also try the ABS historical microfiche collection
ABS_YEARBOOK_BASE = "https://www.abs.gov.au/ausstats/abs@.nsf"


def download_file(url, dest_path, force=False):
    """Download a file if it doesn't already exist."""
    if dest_path.exists() and not force:
        print(f"  Already exists: {dest_path.name}")
        return True

    print(f"  Downloading: {url}")
    try:
        r = requests.get(url, headers=HEADERS, timeout=120, allow_redirects=True)
        r.raise_for_status()
        dest_path.write_bytes(r.content)
        size_kb = len(r.content) / 1024
        print(f"  Saved: {dest_path.name} ({size_kb:.1f} KB)")
        return True
    except requests.exceptions.RequestException as e:
        print(f"  FAILED ({r.status_code if 'r' in dir() else 'N/A'}): {e}")
        return False


def try_abs_data_api():
    """
    Try to fetch dairy-related data from the ABS SDMX Data API.
    The API is at data.api.abs.gov.au.
    """
    print("\nProbing ABS Data API for agriculture dataflows...")
    api_base = "https://data.api.abs.gov.au/rest"

    # Get list of all dataflows
    try:
        r = requests.get(
            f"{api_base}/dataflow/ABS?detail=allstubs",
            headers={**HEADERS, "Accept": "application/json"},
            timeout=30
        )
        if r.status_code == 200:
            data = r.json()
            # Look for agriculture-related dataflows
            dataflows = data.get("data", {}).get("dataflows", [])
            ag_flows = []
            for df in dataflows:
                name = df.get("name", "").lower()
                desc = df.get("description", "").lower()
                if any(kw in name + desc for kw in
                       ["agri", "livestock", "dairy", "milk", "farm", "cattle"]):
                    ag_flows.append(df)
                    print(f"  Found: {df.get('id')} - {df.get('name')}")
            if not ag_flows:
                print("  No agriculture/dairy dataflows found in API")
            return ag_flows
        else:
            print(f"  API returned {r.status_code}")
            return []
    except Exception as e:
        print(f"  API error: {e}")
        return []


def download_all(force=False):
    """Download all known ABS data files."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    print("Downloading ABS data files...")
    results = {}

    for name, url in ABS_URLS.items():
        ext = url.split('.')[-1].split('?')[0]
        dest = RAW_DIR / f"{name}.{ext}"
        results[name] = download_file(url, dest, force)

    # Also try the API
    try_abs_data_api()

    print(f"\nResults: {sum(results.values())}/{len(results)} successful")
    return results


if __name__ == "__main__":
    download_all()
