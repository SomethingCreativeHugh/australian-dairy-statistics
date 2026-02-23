"""
Master ingest pipeline: parse all sources and load into DuckDB.

Runs all parsers and inserts the combined observations into the database,
along with variable definitions and provenance tracking.
"""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from db import init_db, get_connection, insert_observations
from parse_abares_dairy import parse_all as parse_abares
from parse_abs_historic import parse_all as parse_abs_historic

PROJECT_ROOT = Path(__file__).parent.parent


def register_variable_definitions(conn):
    """Insert variable definitions that parsers may produce."""
    variables = [
        # Production
        ('prod_milk_total', 'production', 'Total milk production', 'megalitres',
         'Total whole milk production'),
        ('prod_butter', 'production', 'Butter production', 'tonnes',
         'Factory butter production'),
        ('prod_cheese', 'production', 'Cheese production', 'tonnes',
         'Factory cheese production'),
        ('prod_milk_powder', 'production', 'Milk powder production', 'tonnes',
         'Whole milk powder production'),

        # Prices
        ('price_farmgate_market', 'price', 'Farmgate price - market milk',
         'cents_per_litre', 'Price paid to farmers for market/liquid milk'),
        ('price_farmgate_manufacturing', 'price',
         'Farmgate price - manufacturing milk', 'cents_per_litre',
         'Price paid to farmers for manufacturing milk'),
        ('price_farmgate_avg', 'price', 'Average farmgate price',
         'cents_per_litre', 'Weighted average farmgate milk price'),
        ('price_export_butter', 'price', 'Export butter price',
         'cents_per_kg', 'Average export price for butter'),
        ('price_export_cheese', 'price', 'Export cheese price',
         'cents_per_kg', 'Average export price for cheese'),

        # Herd
        ('herd_dairy_cows', 'herd', 'Dairy cow numbers', 'head',
         'Cows in milk and dry'),
        ('herd_dairy_cattle', 'herd', 'Dairy cattle numbers', 'head',
         'Total dairy cattle'),
        ('herd_total_cattle', 'herd', 'Total cattle numbers', 'head',
         'Total cattle (meat + dairy)'),
        ('herd_yield_per_cow', 'herd', 'Yield per cow', 'litres',
         'Average annual milk yield per cow'),

        # Consumption
        ('cons_butter_percap', 'consumption', 'Per capita butter consumption',
         'kg', 'Annual per capita butter consumption'),
        ('cons_cheese_percap', 'consumption', 'Per capita cheese consumption',
         'kg', 'Annual per capita cheese consumption'),
        ('cons_milk_percap', 'consumption', 'Per capita milk consumption',
         'litres', 'Annual per capita fluid milk consumption'),
        ('cons_milk_total', 'consumption', 'Total domestic milk consumption',
         'megalitres', 'Total domestic fluid/market milk sales'),
    ]

    for var in variables:
        conn.execute("""
            INSERT INTO variable_definitions
                (variable_id, category, variable_name, unit, description)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT (variable_id) DO UPDATE SET
                category = EXCLUDED.category,
                variable_name = EXCLUDED.variable_name,
                unit = EXCLUDED.unit,
                description = EXCLUDED.description
        """, list(var))


def run_ingest():
    """Run the full ingest pipeline."""
    print("=" * 60)
    print("Australian Dairy Statistics - Data Ingest Pipeline")
    print("=" * 60)

    # Initialize database
    print("\n1. Initialising database...")
    init_db()
    conn = get_connection()

    # Create sequences if they don't exist
    try:
        conn.execute("CREATE SEQUENCE IF NOT EXISTS obs_seq START 1")
        conn.execute("CREATE SEQUENCE IF NOT EXISTS prov_seq START 1")
    except Exception:
        pass  # Sequences may already exist

    # Register variable definitions
    print("   Registering variable definitions...")
    register_variable_definitions(conn)
    conn.close()

    # Parse ABARES data
    print("\n2. Parsing ABARES Agricultural Commodity Statistics...")
    try:
        abares_df = parse_abares()
        if len(abares_df) > 0:
            n = insert_observations(
                abares_df,
                source_name='ABARES Agricultural Commodity Statistics 2018',
                source_type='abares',
                source_url='https://data.gov.au/data/dataset/agricultural-commodity-statistics-2017',
                extraction_method='scrape'
            )
            print(f"   ABARES: {n} observations loaded")
    except Exception as e:
        print(f"   ABARES parsing failed: {e}")

    # Parse ABS historic data
    print("\n3. Parsing ABS Historic Agricultural Commodities...")
    try:
        abs_df = parse_abs_historic()
        if len(abs_df) > 0:
            n = insert_observations(
                abs_df,
                source_name='ABS Historical Agricultural Commodities 1860-2022',
                source_type='abs',
                source_url='https://www.abs.gov.au/statistics/industry/agriculture/agricultural-commodities-australia/latest-release',
                extraction_method='scrape'
            )
            print(f"   ABS Historic: {n} observations loaded")
    except Exception as e:
        print(f"   ABS parsing failed: {e}")

    # Print summary
    print("\n" + "=" * 60)
    print("Ingest complete. Database summary:")
    print("=" * 60)

    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM observations").fetchone()[0]
    print(f"\nTotal observations: {total}")

    if total > 0:
        print("\nBy variable:")
        vars_df = conn.execute("""
            SELECT v.variable_id, v.category, COUNT(*) as n,
                   MIN(o.year) as min_year, MAX(o.year) as max_year
            FROM observations o
            JOIN variable_definitions v ON o.variable_id = v.variable_id
            GROUP BY v.variable_id, v.category
            ORDER BY v.category, v.variable_id
        """).fetchdf()
        print(vars_df.to_string(index=False))

        print("\nBy state:")
        states_df = conn.execute("""
            SELECT state_code, COUNT(*) as n,
                   MIN(year) as min_year, MAX(year) as max_year
            FROM observations
            GROUP BY state_code ORDER BY state_code
        """).fetchdf()
        print(states_df.to_string(index=False))

    conn.close()


if __name__ == "__main__":
    run_ingest()
