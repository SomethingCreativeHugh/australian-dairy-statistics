"""
Unit conversion utilities for Australian historical dairy statistics.

Key conversion events:
- 14 Feb 1966: Decimal currency (£1 = $2, 1 shilling = 10 cents, 1 penny = 5/6 cent)
- 1970s: Metric conversion (gallons -> litres, tons -> tonnes, lbs -> kg)
  Australia formally adopted metric 1970, agriculture mostly converted by mid-1970s.
"""

# Currency conversion (pre-decimal to decimal, 14 Feb 1966)
# £1 = $2.00
# 1 shilling (s) = $0.10
# 1 penny (d) = $0.00833...
# 1 guinea = £1 1s = $2.10

POUNDS_TO_DOLLARS = 2.0
SHILLINGS_TO_CENTS = 10.0
PENCE_TO_CENTS = 10.0 / 12.0  # 0.8333...

# Volume conversion
GALLONS_IMP_TO_LITRES = 4.54609
QUARTS_TO_LITRES = 1.13652
PINTS_TO_LITRES = 0.56826
FLUID_OZ_TO_ML = 28.4131

# Weight conversion
LBS_TO_KG = 0.453592
TONS_IMP_TO_TONNES = 1.01605  # Imperial (long) ton to metric tonne
TONS_SHORT_TO_TONNES = 0.907185
CWT_TO_KG = 50.8023  # Imperial hundredweight

# Area
ACRES_TO_HECTARES = 0.404686


def parse_pre_decimal_price(pounds=0, shillings=0, pence=0):
    """Convert £.s.d to decimal dollars."""
    total_pence = pounds * 240 + shillings * 12 + pence
    total_cents = total_pence * PENCE_TO_CENTS
    return round(total_cents / 100, 4)


def parse_price_string(s):
    """
    Parse various historical price string formats.

    Examples:
        '£1/2/6' -> $2.25 (1 pound, 2 shillings, 6 pence)
        '3s 6d' -> $0.35
        '42d' -> $0.35
        '15/6' -> $1.55 (15 shillings, 6 pence)
        '$1.50' -> $1.50
    """
    s = s.strip()

    # Already decimal
    if s.startswith('$'):
        return float(s.replace('$', '').replace(',', ''))

    # £/s/d format
    if '£' in s:
        parts = s.replace('£', '').split('/')
        pounds = int(parts[0]) if parts[0] else 0
        shillings = int(parts[1]) if len(parts) > 1 and parts[1] else 0
        pence = int(parts[2]) if len(parts) > 2 and parts[2] else 0
        return parse_pre_decimal_price(pounds, shillings, pence)

    # Shillings and pence: '3s 6d' or '3s6d'
    if 's' in s:
        import re
        m = re.match(r'(\d+)\s*s\s*(\d*)\s*d?', s)
        if m:
            shillings = int(m.group(1))
            pence = int(m.group(2)) if m.group(2) else 0
            return parse_pre_decimal_price(0, shillings, pence)

    # Pence only: '42d'
    if s.endswith('d'):
        pence = int(s.replace('d', ''))
        return parse_pre_decimal_price(0, 0, pence)

    # Shillings/pence: '15/6'
    if '/' in s:
        parts = s.split('/')
        shillings = int(parts[0])
        pence = int(parts[1]) if parts[1] else 0
        return parse_pre_decimal_price(0, shillings, pence)

    # Plain number - assume already in dollars/cents
    try:
        return float(s.replace(',', ''))
    except ValueError:
        return None


def convert_volume(value, from_unit, to_unit='litres'):
    """Convert volume units to standard (litres or megalitres)."""
    # Normalise to litres first
    to_litres = {
        'litres': 1.0,
        'megalitres': 1_000_000.0,
        'gallons': GALLONS_IMP_TO_LITRES,
        'imperial_gallons': GALLONS_IMP_TO_LITRES,
        'quarts': QUARTS_TO_LITRES,
        'pints': PINTS_TO_LITRES,
        'million_gallons': GALLONS_IMP_TO_LITRES * 1_000_000,
        'thousand_gallons': GALLONS_IMP_TO_LITRES * 1_000,
    }

    from_litres = {
        'litres': 1.0,
        'megalitres': 1e-6,
        'gallons': 1.0 / GALLONS_IMP_TO_LITRES,
    }

    if from_unit not in to_litres:
        raise ValueError(f"Unknown source volume unit: {from_unit}")
    if to_unit not in from_litres:
        raise ValueError(f"Unknown target volume unit: {to_unit}")

    litres = value * to_litres[from_unit]
    return round(litres * from_litres[to_unit], 6)


def convert_weight(value, from_unit, to_unit='tonnes'):
    """Convert weight units to standard (tonnes or kg)."""
    to_kg = {
        'kg': 1.0,
        'tonnes': 1000.0,
        'lbs': LBS_TO_KG,
        'pounds': LBS_TO_KG,
        'tons': TONS_IMP_TO_TONNES * 1000,
        'imperial_tons': TONS_IMP_TO_TONNES * 1000,
        'short_tons': TONS_SHORT_TO_TONNES * 1000,
        'cwt': CWT_TO_KG,
        'thousand_tons': TONS_IMP_TO_TONNES * 1_000_000,
    }

    from_kg = {
        'kg': 1.0,
        'tonnes': 0.001,
        'lbs': 1.0 / LBS_TO_KG,
    }

    if from_unit not in to_kg:
        raise ValueError(f"Unknown source weight unit: {from_unit}")
    if to_unit not in from_kg:
        raise ValueError(f"Unknown target weight unit: {to_unit}")

    kg = value * to_kg[from_unit]
    return round(kg * from_kg[to_unit], 6)


def convert_price_per_volume(value, from_price_unit, from_vol_unit,
                             to_price_unit='cents', to_vol_unit='litre'):
    """
    Convert price-per-volume units.
    E.g., pence per gallon -> cents per litre
    """
    # Convert price component
    if from_price_unit == 'pence':
        price_cents = value * PENCE_TO_CENTS
    elif from_price_unit == 'shillings':
        price_cents = value * SHILLINGS_TO_CENTS
    elif from_price_unit == 'pounds':
        price_cents = value * POUNDS_TO_DOLLARS * 100
    elif from_price_unit in ('cents', 'dollars_cents'):
        price_cents = value
    elif from_price_unit == 'dollars':
        price_cents = value * 100
    else:
        raise ValueError(f"Unknown price unit: {from_price_unit}")

    # Convert volume component (invert: price/gal -> price/litre means divide by litres_per_gallon)
    if from_vol_unit == 'gallon':
        price_per_litre = price_cents / GALLONS_IMP_TO_LITRES
    elif from_vol_unit == 'quart':
        price_per_litre = price_cents / QUARTS_TO_LITRES
    elif from_vol_unit == 'litre':
        price_per_litre = price_cents
    else:
        raise ValueError(f"Unknown volume unit: {from_vol_unit}")

    if to_price_unit == 'cents' and to_vol_unit == 'litre':
        return round(price_per_litre, 4)
    elif to_price_unit == 'dollars' and to_vol_unit == 'litre':
        return round(price_per_litre / 100, 4)

    raise ValueError(f"Unsupported target: {to_price_unit}/{to_vol_unit}")


def convert_price_per_weight(value, from_price_unit, from_wt_unit,
                             to_price_unit='cents', to_wt_unit='kg'):
    """Convert price-per-weight units. E.g., pence per lb -> cents per kg."""
    # Price to cents
    if from_price_unit == 'pence':
        price_cents = value * PENCE_TO_CENTS
    elif from_price_unit == 'shillings':
        price_cents = value * SHILLINGS_TO_CENTS
    elif from_price_unit == 'pounds':
        price_cents = value * POUNDS_TO_DOLLARS * 100
    elif from_price_unit in ('cents', 'dollars_cents'):
        price_cents = value
    elif from_price_unit == 'dollars':
        price_cents = value * 100
    else:
        raise ValueError(f"Unknown price unit: {from_price_unit}")

    # Weight conversion (invert)
    if from_wt_unit == 'lb':
        price_per_kg = price_cents / LBS_TO_KG
    elif from_wt_unit == 'cwt':
        price_per_kg = price_cents / CWT_TO_KG
    elif from_wt_unit == 'ton':
        price_per_kg = price_cents / (TONS_IMP_TO_TONNES * 1000)
    elif from_wt_unit == 'kg':
        price_per_kg = price_cents
    elif from_wt_unit == 'tonne':
        price_per_kg = price_cents / 1000
    else:
        raise ValueError(f"Unknown weight unit: {from_wt_unit}")

    if to_price_unit == 'cents' and to_wt_unit == 'kg':
        return round(price_per_kg, 4)
    elif to_price_unit == 'dollars' and to_wt_unit == 'kg':
        return round(price_per_kg / 100, 4)

    raise ValueError(f"Unsupported target: {to_price_unit}/{to_wt_unit}")


# Financial year helpers
def fy_label(year):
    """Convert year int to financial year label, e.g. 1965 -> '1965-66'."""
    return f"{year}-{str(year + 1)[-2:]}"


def parse_fy(label):
    """Parse financial year label to start year, e.g. '1965-66' -> 1965."""
    parts = label.strip().split('-')
    return int(parts[0])


if __name__ == "__main__":
    # Quick sanity checks
    assert parse_pre_decimal_price(1, 0, 0) == 2.0, "£1 should be $2"
    assert abs(parse_price_string('3s 6d') - 0.35) < 0.01
    assert abs(convert_volume(1, 'gallons', 'litres') - 4.54609) < 0.001
    assert abs(convert_weight(1, 'tons', 'tonnes') - 1.01605) < 0.001
    print("All conversion sanity checks passed.")
