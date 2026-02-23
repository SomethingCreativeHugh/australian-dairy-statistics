"""
Generate charts for the Australian Dairy Statistics paper.
"""

import duckdb
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "data" / "dairy_stats.duckdb"
FIG_DIR = PROJECT_ROOT / "paper" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# Style
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.labelsize': 12,
    'legend.fontsize': 9.5,
    'figure.dpi': 180,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.15,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.linewidth': 0.5,
})

COLOURS = {
    'VIC': '#1b5e20',
    'NSW': '#0d47a1',
    'QLD': '#b71c1c',
    'SA': '#e65100',
    'WA': '#4a148c',
    'TAS': '#006064',
    'AUS': '#212121',
}


def q(sql, params=None):
    conn = duckdb.connect(str(DB_PATH), read_only=True)
    df = conn.execute(sql, params or []).fetchdf()
    conn.close()
    return df


# ── Figure 1: Milk production and herd size (dual axis) ────────────────────

def fig1_production_and_herd():
    milk = q("""
        SELECT year, value FROM observations
        WHERE variable_id='prod_milk_total' AND state_code='AUS'
        ORDER BY year
    """)
    cows = q("""
        SELECT year, value/1000 as value FROM observations
        WHERE variable_id='herd_dairy_cows' AND state_code='AUS'
        ORDER BY year
    """)

    fig, ax1 = plt.subplots(figsize=(10, 5.5))
    ax2 = ax1.twinx()

    ax1.fill_between(milk.year, milk.value, alpha=0.15, color='#1565c0')
    l1, = ax1.plot(milk.year, milk.value, color='#1565c0', lw=2.2, label='Milk production (ML)')
    l2, = ax2.plot(cows.year, cows.value, color='#c62828', lw=2.2, ls='--', label="Dairy cows ('000)")

    ax1.set_xlabel('Financial year starting')
    ax1.set_ylabel('Milk production (megalitres)', color='#1565c0')
    ax2.set_ylabel("Dairy cows ('000 head)", color='#c62828')
    ax1.tick_params(axis='y', colors='#1565c0')
    ax2.tick_params(axis='y', colors='#c62828')
    ax2.spines['right'].set_visible(True)
    ax2.spines['right'].set_color('#c62828')
    ax2.spines['right'].set_alpha(0.5)

    ax1.set_title('Australian milk production rose 43% while the milking herd shrank 37%\n(1974-2017)')

    lines = [l1, l2]
    ax1.legend(lines, [l.get_label() for l in lines], loc='upper left', framealpha=0.9)

    # Annotate deregulation
    ax1.axvline(2000, color='grey', ls=':', lw=1, alpha=0.7)
    ax1.text(2000.5, 11000, 'Deregulation\n(Jul 2000)', fontsize=8.5, color='grey', va='top')

    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))

    fig.savefig(FIG_DIR / 'fig1_production_herd.png')
    plt.close(fig)
    print('  fig1_production_herd.png')


# ── Figure 2: Yield per cow ────────────────────────────────────────────────

def fig2_yield_per_cow():
    yld = q("""
        SELECT year, value FROM observations
        WHERE variable_id='herd_yield_per_cow' AND state_code='AUS'
        ORDER BY year
    """)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(yld.year, yld.value, color='#2e7d32', lw=2.5, marker='o', ms=4, mfc='white', mew=1.5)

    ax.set_xlabel('Financial year starting')
    ax.set_ylabel('Litres per cow per year')
    ax.set_title('Average milk yield per cow more than doubled (1974-2017)')

    # Annotate key values
    for yr in [1974, 1990, 2000, 2017]:
        row = yld[yld.year == yr].iloc[0]
        ax.annotate(f'{row.value:,.0f} L', (row.year, row.value),
                    textcoords='offset points', xytext=(0, 14),
                    fontsize=9, ha='center', color='#2e7d32', fontweight='bold')

    ax.axvline(2000, color='grey', ls=':', lw=1, alpha=0.7)
    ax.text(2000.5, 2800, 'Deregulation', fontsize=8.5, color='grey')

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
    fig.savefig(FIG_DIR / 'fig2_yield_per_cow.png')
    plt.close(fig)
    print('  fig2_yield_per_cow.png')


# ── Figure 3: Farmgate prices ──────────────────────────────────────────────

def fig3_farmgate_prices():
    avg = q("SELECT year, value FROM observations WHERE variable_id='price_farmgate_avg' AND state_code='AUS' ORDER BY year")
    mfg = q("SELECT year, value FROM observations WHERE variable_id='price_farmgate_manufacturing' AND state_code='AUS' ORDER BY year")
    mkt = q("SELECT year, value FROM observations WHERE variable_id='price_farmgate_market' AND state_code='AUS' ORDER BY year")

    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.plot(mkt.year, mkt.value, color='#1565c0', lw=2, label='Market milk (liquid)')
    ax.plot(mfg.year, mfg.value, color='#e65100', lw=2, label='Manufacturing milk')
    ax.plot(avg.year, avg.value, color='#212121', lw=2.5, label='Weighted average')

    ax.fill_between(mkt.year, mkt.value, mfg.value, alpha=0.08, color='#1565c0')

    ax.set_xlabel('Financial year starting')
    ax.set_ylabel('Cents per litre (nominal)')
    ax.set_title('Farmgate milk prices: the two-price system and deregulation')

    ax.axvline(2000, color='grey', ls=':', lw=1, alpha=0.7)
    ax.annotate('Deregulation\n(Jul 2000)', xy=(2000, 53), fontsize=8.5, color='grey',
                ha='right', va='top')

    # Annotate the premium
    ax.annotate('Market milk\npremium', xy=(1986, 38), fontsize=8.5, color='#1565c0',
                fontstyle='italic', ha='center')

    ax.legend(loc='upper left', framealpha=0.9)
    fig.savefig(FIG_DIR / 'fig3_farmgate_prices.png')
    plt.close(fig)
    print('  fig3_farmgate_prices.png')


# ── Figure 4: State milk production shares ─────────────────────────────────

def fig4_state_shares():
    states = ['VIC', 'NSW', 'QLD', 'TAS', 'SA', 'WA']
    data = {}
    for st in states:
        df = q("""
            SELECT year, value FROM observations
            WHERE variable_id='prod_milk_total' AND state_code=?
            ORDER BY year
        """, [st])
        data[st] = df.set_index('year')['value']

    aus = q("""
        SELECT year, value FROM observations
        WHERE variable_id='prod_milk_total' AND state_code='AUS'
        ORDER BY year
    """).set_index('year')['value']

    fig, ax = plt.subplots(figsize=(10, 5.5))

    # Stacked area
    years = sorted(aus.index)
    bottom = np.zeros(len(years))
    for st in states:
        vals = [data[st].get(y, 0) / aus[y] * 100 for y in years]
        ax.fill_between(years, bottom, bottom + np.array(vals),
                        alpha=0.7, color=COLOURS[st], label=st)
        bottom += np.array(vals)

    ax.set_xlabel('Financial year starting')
    ax.set_ylabel('Share of national milk production (%)')
    ax.set_title('Victoria\'s dominance of Australian milk production grew steadily (1974-2017)')
    ax.set_ylim(0, 100)
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), framealpha=0.9)

    ax.axvline(2000, color='white', ls=':', lw=1.2, alpha=0.8)

    fig.savefig(FIG_DIR / 'fig4_state_shares.png')
    plt.close(fig)
    print('  fig4_state_shares.png')


# ── Figure 5: Dairy cattle by state (ABS long run) ────────────────────────

def fig5_dairy_cattle_states():
    states = ['VIC', 'NSW', 'QLD', 'TAS', 'SA', 'WA']

    fig, ax = plt.subplots(figsize=(10, 5.5))

    for st in states:
        df = q("""
            SELECT year, value/1000 as value FROM observations
            WHERE variable_id='herd_dairy_cattle' AND state_code=?
            ORDER BY year
        """, [st])
        ax.plot(df.year, df.value, color=COLOURS[st], lw=2, label=st)

    ax.set_xlabel('Calendar year')
    ax.set_ylabel("Dairy cattle ('000 head)")
    ax.set_title('Dairy cattle numbers by state (1964-2022)')
    ax.legend(loc='upper right', framealpha=0.9)

    ax.axvline(2000, color='grey', ls=':', lw=1, alpha=0.7)
    ax.text(2001, 1850, 'Deregulation', fontsize=8.5, color='grey')

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
    fig.savefig(FIG_DIR / 'fig5_dairy_cattle_states.png')
    plt.close(fig)
    print('  fig5_dairy_cattle_states.png')


# ── Figure 6: Butter vs cheese production ──────────────────────────────────

def fig6_butter_cheese():
    butter = q("SELECT year, value/1000 as value FROM observations WHERE variable_id='prod_butter' AND state_code='AUS' ORDER BY year")
    cheese = q("SELECT year, value/1000 as value FROM observations WHERE variable_id='prod_cheese' AND state_code='AUS' ORDER BY year")

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(butter.year, butter.value, color='#f9a825', lw=2.5, label='Butter', marker='o', ms=3, mfc='white', mew=1.2)
    ax.plot(cheese.year, cheese.value, color='#5d4037', lw=2.5, label='Cheese', marker='s', ms=3, mfc='white', mew=1.2)

    ax.set_xlabel('Financial year starting')
    ax.set_ylabel("Production ('000 tonnes)")
    ax.set_title('The great product shift: butter declined as cheese production quadrupled (1974-2017)')
    ax.legend(loc='center right', framealpha=0.9)

    # Annotate crossover
    ax.axvline(2000, color='grey', ls=':', lw=1, alpha=0.7)

    fig.savefig(FIG_DIR / 'fig6_butter_cheese.png')
    plt.close(fig)
    print('  fig6_butter_cheese.png')


# ── Figure 7: Per capita consumption ───────────────────────────────────────

def fig7_consumption():
    milk = q("SELECT year, value FROM observations WHERE variable_id='cons_milk_percap' ORDER BY year")
    cheese = q("SELECT year, value FROM observations WHERE variable_id='cons_cheese_percap' ORDER BY year")
    butter = q("SELECT year, value FROM observations WHERE variable_id='cons_butter_percap' ORDER BY year")

    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax2 = ax1.twinx()

    l1, = ax1.plot(milk.year, milk.value, color='#1565c0', lw=2.5, label='Fluid milk (L, left axis)')
    l2, = ax2.plot(cheese.year, cheese.value, color='#5d4037', lw=2, label='Cheese (kg, right axis)')
    l3, = ax2.plot(butter.year, butter.value, color='#f9a825', lw=2, label='Butter (kg, right axis)')

    ax1.set_xlabel('Financial year starting')
    ax1.set_ylabel('Litres per person', color='#1565c0')
    ax2.set_ylabel('Kilograms per person')
    ax1.tick_params(axis='y', colors='#1565c0')
    ax2.spines['right'].set_visible(True)

    ax1.set_title('Per capita consumption: stable milk, rising cheese and butter (1990-2017)')

    lines = [l1, l2, l3]
    ax1.legend(lines, [l.get_label() for l in lines], loc='center left', framealpha=0.9)

    fig.savefig(FIG_DIR / 'fig7_consumption.png')
    plt.close(fig)
    print('  fig7_consumption.png')


# ── Figure 8: Export prices ────────────────────────────────────────────────

def fig8_export_prices():
    butter = q("SELECT year, value FROM observations WHERE variable_id='price_export_butter' AND state_code='AUS' ORDER BY year")
    cheese = q("SELECT year, value FROM observations WHERE variable_id='price_export_cheese' AND state_code='AUS' ORDER BY year")

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(butter.year, butter.value, color='#f9a825', lw=2.5, label='Butter export price')
    ax.plot(cheese.year, cheese.value, color='#5d4037', lw=2.5, label='Cheese export price')

    ax.set_xlabel('Financial year starting')
    ax.set_ylabel('Cents per kilogram (nominal)')
    ax.set_title('Export prices: increasing volatility and long-run appreciation (1974-2017)')
    ax.legend(loc='upper left', framealpha=0.9)

    ax.axvline(2000, color='grey', ls=':', lw=1, alpha=0.7)
    ax.text(2001, 100, 'Deregulation', fontsize=8.5, color='grey')

    fig.savefig(FIG_DIR / 'fig8_export_prices.png')
    plt.close(fig)
    print('  fig8_export_prices.png')


# ── Figure 9: Total cattle long run (1860-2022) ───────────────────────────

def fig9_total_cattle_longrun():
    aus = q("""
        SELECT year, value/1e6 as value FROM observations
        WHERE variable_id='herd_total_cattle' AND state_code='AUS'
        ORDER BY year
    """)
    dairy = q("""
        SELECT year, value/1e6 as value FROM observations
        WHERE variable_id='herd_dairy_cattle' AND state_code='AUS'
        ORDER BY year
    """)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(aus.year, aus.value, color='#212121', lw=2.5, label='Total cattle')
    ax.plot(dairy.year, dairy.value, color='#c62828', lw=2.5, label='Dairy cattle')

    ax.set_xlabel('Year')
    ax.set_ylabel('Millions of head')
    ax.set_title('Australian cattle numbers: 160 years of data (1860-2022)')
    ax.legend(loc='upper left', framealpha=0.9)

    # Key events
    events = [
        (1901, 'Federation'),
        (1942, 'WWII peak'),
        (1973, 'UK joins EEC'),
        (2000, 'Deregulation'),
    ]
    for yr, label in events:
        ax.axvline(yr, color='grey', ls=':', lw=0.8, alpha=0.5)
        ax.text(yr + 1, ax.get_ylim()[1] * 0.95, label, fontsize=7.5, color='grey',
                va='top', rotation=0)

    fig.savefig(FIG_DIR / 'fig9_total_cattle_longrun.png')
    plt.close(fig)
    print('  fig9_total_cattle_longrun.png')


if __name__ == '__main__':
    print('Generating charts...')
    fig1_production_and_herd()
    fig2_yield_per_cow()
    fig3_farmgate_prices()
    fig4_state_shares()
    fig5_dairy_cattle_states()
    fig6_butter_cheese()
    fig7_consumption()
    fig8_export_prices()
    fig9_total_cattle_longrun()
    print(f'\nAll charts saved to {FIG_DIR}/')
