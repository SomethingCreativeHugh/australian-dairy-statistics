"""Database management module for Australian Dairy Statistics project."""

import duckdb
import sqlite3
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "data" / "dairy_stats.duckdb"
SCHEMA_PATH = PROJECT_ROOT / "scripts" / "schema.sql"


def get_connection():
    """Get a DuckDB connection to the project database."""
    return duckdb.connect(str(DB_PATH))


def init_db():
    """Initialise the database with the schema."""
    # DuckDB doesn't support all SQLite syntax, so we use a translation layer
    conn = get_connection()

    # Create sequences first (DuckDB requires them before table references)
    conn.execute("CREATE SEQUENCE IF NOT EXISTS obs_seq START 1")
    conn.execute("CREATE SEQUENCE IF NOT EXISTS prov_seq START 1")

    # Create tables manually for DuckDB compatibility
    conn.execute("""
        CREATE TABLE IF NOT EXISTS states (
            state_code VARCHAR PRIMARY KEY,
            state_name VARCHAR NOT NULL
        )
    """)

    # Insert states
    states = [
        ('NSW', 'New South Wales'), ('VIC', 'Victoria'), ('QLD', 'Queensland'),
        ('SA', 'South Australia'), ('WA', 'Western Australia'), ('TAS', 'Tasmania'),
        ('NT', 'Northern Territory'), ('ACT', 'Australian Capital Territory'),
        ('AUS', 'Australia (National)')
    ]
    for code, name in states:
        conn.execute(
            "INSERT INTO states VALUES (?, ?) ON CONFLICT DO NOTHING",
            [code, name]
        )

    conn.execute("""
        CREATE TABLE IF NOT EXISTS variable_definitions (
            variable_id VARCHAR PRIMARY KEY,
            category VARCHAR NOT NULL,
            variable_name VARCHAR NOT NULL,
            unit VARCHAR NOT NULL,
            description VARCHAR
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS observations (
            id INTEGER PRIMARY KEY DEFAULT nextval('obs_seq'),
            variable_id VARCHAR NOT NULL,
            state_code VARCHAR NOT NULL,
            year INTEGER NOT NULL,
            year_type VARCHAR NOT NULL DEFAULT 'FY',
            value DOUBLE,
            original_value DOUBLE,
            original_unit VARCHAR,
            confidence VARCHAR DEFAULT 'high',
            notes VARCHAR,
            UNIQUE(variable_id, state_code, year, year_type)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS provenance (
            id INTEGER PRIMARY KEY DEFAULT nextval('prov_seq'),
            observation_id INTEGER NOT NULL,
            source_name VARCHAR NOT NULL,
            source_type VARCHAR NOT NULL,
            source_url VARCHAR,
            source_page VARCHAR,
            extraction_method VARCHAR,
            extraction_date VARCHAR,
            notes VARCHAR
        )
    """)

    conn.close()
    print(f"Database initialised at {DB_PATH}")


def insert_observations(df, source_name, source_type, source_url=None,
                        extraction_method='scrape'):
    """
    Insert a DataFrame of observations into the database.

    Expected DataFrame columns:
        - variable_id: str
        - state_code: str
        - year: int
        - value: float
        - year_type: str (optional, defaults to 'FY')
        - original_value: float (optional)
        - original_unit: str (optional)
        - confidence: str (optional, defaults to 'high')
        - notes: str (optional)
    """
    conn = get_connection()

    if 'year_type' not in df.columns:
        df['year_type'] = 'FY'
    if 'confidence' not in df.columns:
        df['confidence'] = 'high'

    optional_cols = ['original_value', 'original_unit', 'notes']
    for col in optional_cols:
        if col not in df.columns:
            df[col] = None

    inserted = 0
    for _, row in df.iterrows():
        try:
            conn.execute("""
                INSERT INTO observations
                    (variable_id, state_code, year, year_type, value,
                     original_value, original_unit, confidence, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (variable_id, state_code, year, year_type)
                DO UPDATE SET value = EXCLUDED.value,
                             confidence = EXCLUDED.confidence,
                             notes = EXCLUDED.notes
            """, [
                row['variable_id'], row['state_code'], int(row['year']),
                row['year_type'], float(row['value']) if pd.notna(row['value']) else None,
                float(row['original_value']) if pd.notna(row.get('original_value')) else None,
                row.get('original_unit'),
                row.get('confidence', 'high'),
                row.get('notes')
            ])
            inserted += 1
        except Exception as e:
            print(f"Error inserting {row.get('variable_id')} {row.get('state_code')} "
                  f"{row.get('year')}: {e}")

    conn.close()
    print(f"Inserted/updated {inserted} observations from {source_name}")
    return inserted


def query(sql, params=None):
    """Run a query and return a DataFrame."""
    conn = get_connection()
    result = conn.execute(sql, params or []).fetchdf()
    conn.close()
    return result


def export_csv(output_path=None):
    """Export the full dataset to CSV."""
    if output_path is None:
        output_path = PROJECT_ROOT / "data" / "final" / "aus_dairy_stats.csv"

    conn = get_connection()
    df = conn.execute("""
        SELECT
            o.year,
            o.year_type,
            s.state_name,
            o.state_code,
            v.category,
            v.variable_id,
            v.variable_name,
            o.value,
            v.unit,
            o.confidence,
            o.original_value,
            o.original_unit,
            o.notes
        FROM observations o
        JOIN variable_definitions v ON o.variable_id = v.variable_id
        JOIN states s ON o.state_code = s.state_code
        ORDER BY o.year, o.state_code, v.category, v.variable_id
    """).fetchdf()
    conn.close()

    df.to_csv(output_path, index=False)
    print(f"Exported {len(df)} rows to {output_path}")
    return df


def summary():
    """Print a summary of what's in the database."""
    conn = get_connection()

    total = conn.execute("SELECT COUNT(*) FROM observations").fetchone()[0]
    print(f"\nTotal observations: {total}")

    if total > 0:
        print("\nBy category:")
        cats = conn.execute("""
            SELECT v.category, COUNT(*) as n,
                   MIN(o.year) as min_year, MAX(o.year) as max_year
            FROM observations o
            JOIN variable_definitions v ON o.variable_id = v.variable_id
            GROUP BY v.category ORDER BY v.category
        """).fetchdf()
        print(cats.to_string(index=False))

        print("\nBy state:")
        states = conn.execute("""
            SELECT o.state_code, COUNT(*) as n
            FROM observations o
            GROUP BY o.state_code ORDER BY o.state_code
        """).fetchdf()
        print(states.to_string(index=False))

        print("\nBy confidence:")
        conf = conn.execute("""
            SELECT confidence, COUNT(*) as n
            FROM observations
            GROUP BY confidence ORDER BY confidence
        """).fetchdf()
        print(conf.to_string(index=False))

    conn.close()


if __name__ == "__main__":
    init_db()
    summary()
