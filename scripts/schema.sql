-- Australian Dairy Industry Historical Statistics Database Schema
-- Covers 1946-2000 (price control era through deregulation)

-- Master reference tables
CREATE TABLE IF NOT EXISTS states (
    state_code TEXT PRIMARY KEY,
    state_name TEXT NOT NULL
);

INSERT OR IGNORE INTO states VALUES
    ('NSW', 'New South Wales'),
    ('VIC', 'Victoria'),
    ('QLD', 'Queensland'),
    ('SA', 'South Australia'),
    ('WA', 'Western Australia'),
    ('TAS', 'Tasmania'),
    ('NT', 'Northern Territory'),
    ('ACT', 'Australian Capital Territory'),
    ('AUS', 'Australia (National)');

CREATE TABLE IF NOT EXISTS variable_definitions (
    variable_id TEXT PRIMARY KEY,
    category TEXT NOT NULL,       -- production, price, herd, consumption, trade
    variable_name TEXT NOT NULL,
    unit TEXT NOT NULL,
    description TEXT
);

INSERT OR IGNORE INTO variable_definitions VALUES
    -- Production
    ('prod_milk_total', 'production', 'Total milk production', 'megalitres', 'Total whole milk production'),
    ('prod_milk_market', 'production', 'Market milk production', 'megalitres', 'Milk sold for liquid consumption'),
    ('prod_milk_manufacturing', 'production', 'Manufacturing milk production', 'megalitres', 'Milk used for butter, cheese, etc.'),
    ('prod_butter', 'production', 'Butter production', 'tonnes', 'Factory butter production'),
    ('prod_cheese', 'production', 'Cheese production', 'tonnes', 'Factory cheese production'),
    ('prod_milk_powder', 'production', 'Milk powder production', 'tonnes', 'Whole and skim milk powder'),
    ('prod_casein', 'production', 'Casein production', 'tonnes', 'Casein and caseinates'),

    -- Prices
    ('price_farmgate_market', 'price', 'Farmgate price - market milk', 'cents_per_litre', 'Price paid to farmers for market/liquid milk'),
    ('price_farmgate_manufacturing', 'price', 'Farmgate price - manufacturing milk', 'cents_per_litre', 'Price paid to farmers for manufacturing milk'),
    ('price_farmgate_avg', 'price', 'Average farmgate price', 'cents_per_litre', 'Weighted average farmgate milk price'),
    ('price_retail_milk', 'price', 'Retail milk price', 'cents_per_litre', 'Consumer retail price for fresh milk'),
    ('price_wholesale_butter', 'price', 'Wholesale butter price', 'cents_per_kg', 'Wholesale/commercial butter price'),
    ('price_wholesale_cheese', 'price', 'Wholesale cheese price', 'cents_per_kg', 'Wholesale/commercial cheese price'),
    ('price_export_butter', 'price', 'Export butter price', 'cents_per_kg', 'Average export price for butter'),
    ('price_export_cheese', 'price', 'Export cheese price', 'cents_per_kg', 'Average export price for cheese'),

    -- Herd
    ('herd_dairy_cattle', 'herd', 'Dairy cattle numbers', 'head', 'Total dairy cattle'),
    ('herd_dairy_cows', 'herd', 'Dairy cow numbers', 'head', 'Cows in milk and dry'),
    ('herd_farms', 'herd', 'Number of dairy farms', 'count', 'Registered dairy farms/establishments'),
    ('herd_yield_per_cow', 'herd', 'Yield per cow', 'litres', 'Average annual milk yield per cow'),

    -- Consumption
    ('cons_milk_percap', 'consumption', 'Per capita milk consumption', 'litres', 'Annual per capita fluid milk consumption'),
    ('cons_butter_percap', 'consumption', 'Per capita butter consumption', 'kg', 'Annual per capita butter consumption'),
    ('cons_cheese_percap', 'consumption', 'Per capita cheese consumption', 'kg', 'Annual per capita cheese consumption'),
    ('cons_milk_total', 'consumption', 'Total domestic milk consumption', 'megalitres', 'Total domestic fluid milk sales'),

    -- Trade
    ('trade_export_butter', 'trade', 'Butter exports', 'tonnes', 'Total butter exports'),
    ('trade_export_cheese', 'trade', 'Cheese exports', 'tonnes', 'Total cheese exports'),
    ('trade_export_milk_powder', 'trade', 'Milk powder exports', 'tonnes', 'Whole and skim milk powder exports'),
    ('trade_export_value_total', 'trade', 'Total dairy export value', 'aud_thousands', 'Total value of dairy exports'),
    ('trade_import_butter', 'trade', 'Butter imports', 'tonnes', 'Total butter imports'),
    ('trade_import_cheese', 'trade', 'Cheese imports', 'tonnes', 'Total cheese imports');

-- Core data table: one row per observation
CREATE TABLE IF NOT EXISTS observations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    variable_id TEXT NOT NULL REFERENCES variable_definitions(variable_id),
    state_code TEXT NOT NULL REFERENCES states(state_code),
    year INTEGER NOT NULL,               -- calendar or financial year start (e.g., 1965 for 1965-66)
    year_type TEXT NOT NULL DEFAULT 'FY', -- 'FY' = financial year (Jul-Jun), 'CY' = calendar year
    value REAL,
    original_value REAL,                 -- value before unit conversion
    original_unit TEXT,                  -- original unit before standardisation
    confidence TEXT DEFAULT 'high',      -- high, medium, low, interpolated
    notes TEXT,
    UNIQUE(variable_id, state_code, year, year_type)
);

-- Provenance tracking: where did each data point come from?
CREATE TABLE IF NOT EXISTS provenance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    observation_id INTEGER NOT NULL REFERENCES observations(id),
    source_name TEXT NOT NULL,           -- e.g., 'ABS Yearbook 1970', 'ABARES Commodity Statistics'
    source_type TEXT NOT NULL,           -- 'abs_yearbook', 'abares', 'milk_board', 'academic', 'interpolated'
    source_url TEXT,
    source_page TEXT,                    -- page number or table reference
    extraction_method TEXT,              -- 'manual', 'ocr', 'api', 'scrape', 'calculated'
    extraction_date TEXT,
    notes TEXT
);

-- Unit conversion log
CREATE TABLE IF NOT EXISTS unit_conversions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    observation_id INTEGER NOT NULL REFERENCES observations(id),
    from_unit TEXT NOT NULL,
    to_unit TEXT NOT NULL,
    conversion_factor REAL NOT NULL,
    conversion_notes TEXT
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_obs_variable ON observations(variable_id);
CREATE INDEX IF NOT EXISTS idx_obs_state ON observations(state_code);
CREATE INDEX IF NOT EXISTS idx_obs_year ON observations(year);
CREATE INDEX IF NOT EXISTS idx_obs_lookup ON observations(variable_id, state_code, year);
CREATE INDEX IF NOT EXISTS idx_prov_obs ON provenance(observation_id);

-- View for easy querying
CREATE VIEW IF NOT EXISTS dairy_data AS
SELECT
    o.year,
    o.year_type,
    s.state_name,
    o.state_code,
    v.category,
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
ORDER BY o.year, o.state_code, v.category, v.variable_id;
