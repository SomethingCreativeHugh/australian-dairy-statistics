"""
Parse ABS Historical Selected Agricultural Commodities (1860-2022) dairy data.

Source: ABS release "Historical Selected Agricultural Commodities, by Australia,
state and territories, 1860 to 2022" (released April 2024).

This file contains wide-format tables where each column is a year and each row
is a geographic region. We extract Table 8 (Dairy cattle numbers by state).
"""

import pandas as pd
import numpy as np
from pathlib import Path
import re

PROJECT_ROOT = Path(__file__).parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "abs"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

SOURCE_NAME = "ABS Historical Agricultural Commodities 1860-2022"
SOURCE_TYPE = "abs"

# Map region labels to our state codes
REGION_MAP = {
    'Australia': 'AUS',
    'New South Wales': 'NSW',
    'Victoria': 'VIC',
    'Queensland': 'QLD',
    'South Australia': 'SA',
    'Western Australia': 'WA',
    'Tasmania': 'TAS',
    'Northern Territory': 'NT',
    'Australian Capital Territory': 'ACT',
}


def clean_value(v):
    """Clean a cell value to float or None."""
    if v is None or v == '' or v == ' ':
        return None
    if isinstance(v, (int, float)):
        if isinstance(v, float) and np.isnan(v):
            return None
        return float(v)
    s = str(v).strip().replace(',', '').replace(' ', '')
    if s.lower() in ('na', 'n.a.', 'n.a', '..', '...', '-', '–', '', 'np',
                      'nec', 'n/a'):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def parse_wide_table(filepath, sheet_name, variable_id, unit, converter=None,
                     year_type='CY'):
    """
    Parse a wide-format ABS table where columns are years and rows are regions.

    Header row (row 5, 0-indexed) contains: 'Region label', 'Unit of measure',
    then year columns. Data starts at row 6.
    """
    if converter is None:
        converter = lambda x: x

    df = pd.read_excel(filepath, sheet_name=sheet_name, header=None)

    # Find the header row (contains 'Region label')
    header_row = None
    for i in range(min(10, len(df))):
        row_vals = [str(v).strip() for v in df.iloc[i] if pd.notna(v)]
        if any('Region label' in v for v in row_vals):
            header_row = i
            break

    if header_row is None:
        raise ValueError(f"Could not find header row in {sheet_name}")

    # Extract year columns from the header row
    year_cols = {}
    for col_idx in range(2, len(df.columns)):
        val = df.iloc[header_row, col_idx]
        if pd.notna(val):
            try:
                year = int(float(str(val).strip()))
                if 1860 <= year <= 2030:
                    year_cols[col_idx] = year
            except (ValueError, TypeError):
                continue

    # Extract data rows
    observations = []
    for row_idx in range(header_row + 1, len(df)):
        region = df.iloc[row_idx, 0]
        if pd.isna(region):
            continue
        region = str(region).strip()
        state_code = REGION_MAP.get(region)
        if state_code is None:
            continue

        for col_idx, year in year_cols.items():
            val = clean_value(df.iloc[row_idx, col_idx])
            if val is not None:
                observations.append({
                    'variable_id': variable_id,
                    'state_code': state_code,
                    'year': year,
                    'year_type': year_type,
                    'value': converter(val),
                    'original_value': val,
                    'original_unit': unit,
                    'confidence': 'high',
                })

    return pd.DataFrame(observations)


def parse_all():
    """Parse all ABS historic dairy tables."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    filepath = RAW_DIR / 'historic_ag_commodities_1860_2022.xlsx'
    if not filepath.exists():
        print(f"File not found: {filepath}")
        return pd.DataFrame()

    print(f"Parsing ABS historic data from: {filepath.name}")

    all_obs = []

    # Table 8: Dairy cattle numbers (1964-2022)
    print("  Table 8: Dairy cattle by state...")
    obs = parse_wide_table(
        filepath, 'Table 8', 'herd_dairy_cattle', 'head',
        year_type='CY'
    )
    print(f"    {len(obs)} observations")
    all_obs.append(obs)

    # Table 6: Total cattle (1860-2022) - useful for historical context
    print("  Table 6: Total cattle by state...")
    obs = parse_wide_table(
        filepath, 'Table 6', 'herd_total_cattle', 'head',
        year_type='CY'
    )
    print(f"    {len(obs)} observations")
    all_obs.append(obs)

    if not all_obs:
        return pd.DataFrame()

    combined = pd.concat(all_obs, ignore_index=True)
    combined = combined.dropna(subset=['value'])

    print(f"\nTotal ABS historic observations: {len(combined)}")
    print(f"Year range: {combined['year'].min()} - {combined['year'].max()}")
    print(f"Variables: {combined['variable_id'].nunique()}")
    print(f"States: {combined['state_code'].unique().tolist()}")

    out_path = PROCESSED_DIR / 'abs_historic_parsed.csv'
    combined.to_csv(out_path, index=False)
    print(f"Saved to: {out_path}")

    return combined


if __name__ == "__main__":
    df = parse_all()
    if len(df) > 0:
        print("\nSample data:")
        print(df.head(20).to_string(index=False))
