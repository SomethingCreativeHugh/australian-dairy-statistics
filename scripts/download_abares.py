"""
Download ABARES Agricultural Commodity Statistics dairy tables.

ABARES publishes comprehensive commodity statistics including dairy data
going back decades. The 2017 edition was the last standalone ACS publication;
more recent data is in the Agricultural Outlook tables.

Key download sources:
- data.gov.au: ACS 2017 dairy tables (Excel)
- agriculture.gov.au/abares: Agricultural commodities and trade data
"""

import requests
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "abares"

# Known ABARES data file URLs
ABARES_URLS = {
    # ACS 2017 dairy tables from data.gov.au
    "acs2017_dairy": "http://data.daff.gov.au/data/warehouse/agcstd9abcc002/agcstd9abcc0022017_IugZg/ACS2017_DairyTables_v1.0.0.xlsx",

    # Agricultural outlook data tables (most recent)
    # These are updated quarterly by ABARES
    "outlook_data_2024": "https://www.agriculture.gov.au/sites/default/files/documents/agricultural-outlook-march-2024-data-tables.xlsx",
    "outlook_data_2025": "https://www.agriculture.gov.au/sites/default/files/documents/agricultural-outlook-march-2025-data-tables.xlsx",
}

# Additional ABARES data.gov.au datasets
DATAGOV_URLS = {
    "acs2017_meat_general": "http://data.daff.gov.au/data/warehouse/agcstd9abcc002/agcstd9abcc0022017_IugZg/ACS2017_Meat-GeneralTables_v1.0.0.xlsx",
}

HEADERS = {
    "User-Agent": "AusDairyStats/1.0 (academic research project)"
}


def download_file(url, dest_path, force=False):
    """Download a file if it doesn't already exist."""
    if dest_path.exists() and not force:
        print(f"  Already exists: {dest_path.name}")
        return True

    print(f"  Downloading: {url}")
    try:
        r = requests.get(url, headers=HEADERS, timeout=60, allow_redirects=True)
        r.raise_for_status()
        dest_path.write_bytes(r.content)
        size_kb = len(r.content) / 1024
        print(f"  Saved: {dest_path.name} ({size_kb:.1f} KB)")
        return True
    except requests.exceptions.RequestException as e:
        print(f"  FAILED: {e}")
        return False


def download_all(force=False):
    """Download all known ABARES data files."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    print("Downloading ABARES data files...")
    results = {}

    for name, url in ABARES_URLS.items():
        ext = url.split('.')[-1].split('?')[0]
        dest = RAW_DIR / f"{name}.{ext}"
        results[name] = download_file(url, dest, force)

    print(f"\nResults: {sum(results.values())}/{len(results)} successful")
    return results


if __name__ == "__main__":
    download_all()
