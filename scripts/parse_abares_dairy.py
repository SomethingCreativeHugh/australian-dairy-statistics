"""
Parse ABARES Agricultural Commodity Statistics dairy tables into structured data.

The ACS 2017 dairy tables (and 2018 update) contain tables 6.1-6.16 covering
Australian dairy statistics from 1973-74 onwards, with state breakdowns.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import re

PROJECT_ROOT = Path(__file__).parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "abares"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

SOURCE_NAME = "ABARES Agricultural Commodity Statistics 2017"
SOURCE_TYPE = "abares"
SOURCE_URL = "https://data.gov.au/data/dataset/agricultural-commodity-statistics-2017"


def get_sheet_name(filepath, base_name):
    """Get the correct sheet name, handling spacing differences between 2017/2018 files."""
    import openpyxl
    wb = openpyxl.load_workbook(filepath, read_only=True)
    sheets = wb.sheetnames
    wb.close()
    # Try exact match first
    if base_name in sheets:
        return base_name
    # Try with space (2018 format: "Table 6.1")
    spaced = base_name.replace('Table', 'Table ')
    if spaced in sheets:
        return spaced
    # Try without space (2017 format: "Table6.1")
    unspaced = base_name.replace('Table ', 'Table')
    if unspaced in sheets:
        return unspaced
    raise ValueError(f"Sheet '{base_name}' not found in {filepath.name}. Available: {sheets}")


def parse_fy_year(label):
    """Parse financial year label like '1973–74' or '1973-74' to start year 1973."""
    if label is None:
        return None
    s = str(label).strip()
    # Match patterns like 1973–74, 1973-74
    m = re.match(r'(\d{4})\s*[–\-]\s*\d{2,4}', s)
    if m:
        return int(m.group(1))
    # Plain year
    m = re.match(r'^(\d{4})$', s)
    if m:
        return int(m.group(1))
    return None


def clean_value(v):
    """Clean a cell value to float or None."""
    if v is None or v == '' or v == ' ':
        return None
    if isinstance(v, (int, float)):
        if np.isnan(v) if isinstance(v, float) else False:
            return None
        return float(v)
    s = str(v).strip().replace(',', '').replace(' ', '')
    # Handle 'na', 'n.a.', '..', etc.
    if s.lower() in ('na', 'n.a.', 'n.a', '..', '...', '-', '–', '', 'nec', 'np'):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def read_table_6_1(filepath):
    """
    Table 6.1: Summary of Australian statistics for dairy products.
    Columns: Year, Dairy cow numbers ('000), Yield per cow (L), Milk production (ML),
             Butter production (kt), Cheese production (kt), Export price butter ($/t),
             Export price cheese ($/t)
    National only, from 1973-74.
    """
    sheet = get_sheet_name(filepath, 'Table6.1')
    df = pd.read_excel(filepath, sheet_name=sheet, header=None)

    # Find the data start - look for the first row with a year-like value in col 1
    data_rows = []
    for idx, row in df.iterrows():
        year = parse_fy_year(row.iloc[1])
        if year and year >= 1970:
            data_rows.append({
                'year': year,
                'herd_dairy_cows': clean_value(row.iloc[2]),      # '000
                'herd_yield_per_cow': clean_value(row.iloc[3]),    # L
                'prod_milk_total': clean_value(row.iloc[4]),       # ML
                'prod_butter': clean_value(row.iloc[5]),           # kt
                'prod_cheese': clean_value(row.iloc[6]),           # kt
                'price_export_butter': clean_value(row.iloc[7]),   # $/t
                'price_export_cheese': clean_value(row.iloc[8]),   # $/t
            })

    result = pd.DataFrame(data_rows)

    # Convert units to match our schema
    observations = []
    unit_map = {
        'herd_dairy_cows': ('head', lambda x: x * 1000),            # '000 -> head
        'herd_yield_per_cow': ('litres', lambda x: x),               # L -> litres
        'prod_milk_total': ('megalitres', lambda x: x),              # ML -> megalitres
        'prod_butter': ('tonnes', lambda x: x * 1000),              # kt -> tonnes
        'prod_cheese': ('tonnes', lambda x: x * 1000),              # kt -> tonnes
        'price_export_butter': ('cents_per_kg', lambda x: x / 10),  # $/t -> $/kg -> c/kg * 100 / 1000
        'price_export_cheese': ('cents_per_kg', lambda x: x / 10),  # $/t -> c/kg
    }

    for _, row in result.iterrows():
        for var_id, (orig_unit, converter) in unit_map.items():
            val = row.get(var_id)
            if val is not None:
                observations.append({
                    'variable_id': var_id,
                    'state_code': 'AUS',
                    'year': int(row['year']),
                    'year_type': 'FY',
                    'value': converter(val),
                    'original_value': val,
                    'original_unit': orig_unit,
                    'confidence': 'high',
                })

    return pd.DataFrame(observations)


def read_state_table(filepath, sheet_name, variable_id, unit, converter=None,
                     year_type='FY'):
    """
    Generic reader for state-level tables (6.4, 6.5, etc.).
    These have columns: Year, NSW, VIC, QLD, SA, WA, TAS, AUS
    """
    if converter is None:
        converter = lambda x: x

    sheet = get_sheet_name(filepath, sheet_name)
    df = pd.read_excel(filepath, sheet_name=sheet, header=None)

    state_cols = {
        2: 'NSW', 3: 'VIC', 4: 'QLD', 5: 'SA', 6: 'WA', 7: 'TAS', 8: 'AUS'
    }

    observations = []
    for idx, row in df.iterrows():
        year = parse_fy_year(row.iloc[1])
        if year and year >= 1970:
            for col_idx, state_code in state_cols.items():
                val = clean_value(row.iloc[col_idx])
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


def read_table_6_8(filepath):
    """
    Table 6.8: Australian milk prices and gross value of production.
    Cols: Year, Mfg milk price (c/L), Market milk price (c/L), Weighted avg (c/L),
          Mfg milk value ($m), Market milk value ($m), Total value ($m)
    """
    sheet = get_sheet_name(filepath, 'Table6.8')
    df = pd.read_excel(filepath, sheet_name=sheet, header=None)

    observations = []
    for idx, row in df.iterrows():
        year = parse_fy_year(row.iloc[1])
        if year and year >= 1970:
            # Manufacturing milk price (c/L)
            val = clean_value(row.iloc[2])
            if val is not None:
                observations.append({
                    'variable_id': 'price_farmgate_manufacturing',
                    'state_code': 'AUS', 'year': year, 'year_type': 'FY',
                    'value': val, 'original_value': val,
                    'original_unit': 'cents_per_litre', 'confidence': 'high',
                })
            # Market milk price (c/L)
            val = clean_value(row.iloc[3])
            if val is not None:
                observations.append({
                    'variable_id': 'price_farmgate_market',
                    'state_code': 'AUS', 'year': year, 'year_type': 'FY',
                    'value': val, 'original_value': val,
                    'original_unit': 'cents_per_litre', 'confidence': 'high',
                })
            # Weighted average price (c/L)
            val = clean_value(row.iloc[4])
            if val is not None:
                observations.append({
                    'variable_id': 'price_farmgate_avg',
                    'state_code': 'AUS', 'year': year, 'year_type': 'FY',
                    'value': val, 'original_value': val,
                    'original_unit': 'cents_per_litre', 'confidence': 'high',
                })

    return pd.DataFrame(observations)


def read_table_6_9(filepath):
    """
    Table 6.9: Average export unit values.
    Cols: Year, Butter ($/t), Cheese ($/t), SMP ($/t), WMP ($/t), Casein ($/t)
    """
    sheet = get_sheet_name(filepath, 'Table6.9')
    df = pd.read_excel(filepath, sheet_name=sheet, header=None)

    var_map = {
        2: ('price_export_butter', 'dollars_per_tonne'),
        3: ('price_export_cheese', 'dollars_per_tonne'),
    }

    observations = []
    for idx, row in df.iterrows():
        year = parse_fy_year(row.iloc[1])
        if year and year >= 1970:
            for col_idx, (var_id, unit) in var_map.items():
                val = clean_value(row.iloc[col_idx])
                if val is not None:
                    # Convert $/t to c/kg: $/t * 100 / 1000 = c/kg / 10
                    c_per_kg = val / 10
                    observations.append({
                        'variable_id': var_id,
                        'state_code': 'AUS', 'year': year, 'year_type': 'FY',
                        'value': c_per_kg, 'original_value': val,
                        'original_unit': unit, 'confidence': 'high',
                    })

    return pd.DataFrame(observations)


def read_table_6_6(filepath):
    """
    Table 6.6: Australian manufacture of dairy products.
    Wide format: years as columns (1990-91 to 2017-18).
    Rows: Butter (kt), Cheese (kt), WMP (kt), SMP (kt), Buttermilk powder (kt).
    """
    sheet = get_sheet_name(filepath, 'Table6.6')
    df = pd.read_excel(filepath, sheet_name=sheet, header=None)

    # Row 7 has headers with year labels; data rows start at 8
    year_labels = df.iloc[7, 3:].tolist()
    years = [parse_fy_year(y) for y in year_labels]

    # Map data rows to variable IDs (row index -> (var_id, unit_in_file))
    row_map = {
        8: ('prod_butter', 'kt'),
        9: ('prod_cheese', 'kt'),
        12: ('prod_milk_powder', 'kt'),  # WMP
    }

    observations = []
    for row_idx, (var_id, unit) in row_map.items():
        for col_offset, year in enumerate(years):
            if year is None or year < 1970:
                continue
            val = clean_value(df.iloc[row_idx, 3 + col_offset])
            if val is not None:
                observations.append({
                    'variable_id': var_id,
                    'state_code': 'AUS',
                    'year': year,
                    'year_type': 'FY',
                    'value': val * 1000,  # kt -> tonnes
                    'original_value': val,
                    'original_unit': unit,
                    'confidence': 'high',
                })

    return pd.DataFrame(observations)


def read_table_6_7(filepath):
    """
    Table 6.7: Australian consumption of dairy products.
    Wide format: years as columns (1990-91 to 2017-18).
    Total consumption: Butter (kt), Cheese (kt), Market milk (ML).
    Per capita: Butter (kg), Cheese (kg), Market milk (L).
    """
    sheet = get_sheet_name(filepath, 'Table6.7')
    df = pd.read_excel(filepath, sheet_name=sheet, header=None)

    year_labels = df.iloc[7, 3:].tolist()
    years = [parse_fy_year(y) for y in year_labels]

    # Per capita consumption rows
    row_map = {
        15: ('cons_butter_percap', 'kg', lambda x: x),
        16: ('cons_cheese_percap', 'kg', lambda x: x),
        19: ('cons_milk_percap', 'litres', lambda x: x),
    }
    # Total consumption
    total_map = {
        13: ('cons_milk_total', 'ML', lambda x: x),  # Market milk ML
    }

    observations = []
    for mapping in [row_map, total_map]:
        for row_idx, (var_id, unit, converter) in mapping.items():
            for col_offset, year in enumerate(years):
                if year is None or year < 1970:
                    continue
                val = clean_value(df.iloc[row_idx, 3 + col_offset])
                if val is not None:
                    observations.append({
                        'variable_id': var_id,
                        'state_code': 'AUS',
                        'year': year,
                        'year_type': 'FY',
                        'value': converter(val),
                        'original_value': val,
                        'original_unit': unit,
                        'confidence': 'high',
                    })

    return pd.DataFrame(observations)


def parse_all():
    """Parse all ABARES dairy tables and return combined observations DataFrame."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # Try 2018 first (more recent), fall back to 2017
    filepath = RAW_DIR / 'acs2018_dairy.xlsx'
    if not filepath.exists():
        filepath = RAW_DIR / 'acs2017_dairy.xlsx'

    print(f"Parsing ABARES dairy tables from: {filepath.name}")

    all_obs = []

    # Table 6.1: National summary
    print("  Table 6.1: National summary...")
    obs = read_table_6_1(filepath)
    print(f"    {len(obs)} observations")
    all_obs.append(obs)

    # Table 6.4: Dairy cow numbers by state
    print("  Table 6.4: Dairy cow numbers by state...")
    obs = read_state_table(
        filepath, 'Table 6.4', 'herd_dairy_cows', "'000",
        converter=lambda x: x * 1000  # '000 -> head
    )
    print(f"    {len(obs)} observations")
    all_obs.append(obs)

    # Table 6.5: Whole milk production by state
    print("  Table 6.5: Milk production by state...")
    obs = read_state_table(
        filepath, 'Table 6.5', 'prod_milk_total', 'ML'
    )
    print(f"    {len(obs)} observations")
    all_obs.append(obs)

    # Table 6.6: Manufacture of dairy products
    print("  Table 6.6: Manufacture...")
    obs = read_table_6_6(filepath)
    print(f"    {len(obs)} observations")
    all_obs.append(obs)

    # Table 6.7: Consumption of dairy products
    print("  Table 6.7: Consumption...")
    obs = read_table_6_7(filepath)
    print(f"    {len(obs)} observations")
    all_obs.append(obs)

    # Table 6.8: Prices and gross value
    print("  Table 6.8: Milk prices...")
    obs = read_table_6_8(filepath)
    print(f"    {len(obs)} observations")
    all_obs.append(obs)

    # Table 6.9: Export unit values
    print("  Table 6.9: Export prices...")
    obs = read_table_6_9(filepath)
    print(f"    {len(obs)} observations")
    all_obs.append(obs)

    combined = pd.concat(all_obs, ignore_index=True)
    combined = combined.dropna(subset=['value'])

    print(f"\nTotal ABARES observations: {len(combined)}")
    print(f"Year range: {combined['year'].min()} - {combined['year'].max()}")
    print(f"Variables: {combined['variable_id'].nunique()}")
    print(f"States: {combined['state_code'].unique().tolist()}")

    # Save intermediate
    out_path = PROCESSED_DIR / 'abares_dairy_parsed.csv'
    combined.to_csv(out_path, index=False)
    print(f"Saved to: {out_path}")

    return combined


if __name__ == "__main__":
    df = parse_all()
    print("\nSample data:")
    print(df.head(20).to_string(index=False))
