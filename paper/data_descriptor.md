# Australian Dairy Industry Historical Statistics: A Compiled Dataset and Long-Run Trend Analysis (1860-2022)

## Abstract

This paper presents a compiled dataset of Australian dairy industry statistics drawn from official government sources and situates the data within the broader economic and sociological literature on Australian dairy's structural transformation. The dataset contains 2,703 observations across 17 variables covering production volumes, farmgate and export prices, herd demographics, and consumption patterns. Data spans from 1860 (total cattle numbers) to 2022 (dairy cattle), with comprehensive dairy-specific variables available from 1974. Geographic coverage includes national totals and all six states plus two territories. The dataset harmonises data from the Australian Bureau of Agricultural and Resource Economics and Sciences (ABARES) Agricultural Commodity Statistics and the Australian Bureau of Statistics (ABS) Historical Selected Agricultural Commodities series. All data is provided in standardised metric/decimal units with original values preserved for verification. We use the compiled series to document five major structural trends: the contraction and geographic concentration of the national herd, a productivity revolution in per-cow yields, the collapse and partial recovery of farmgate prices through deregulation, a shift in product mix from butter to cheese and powder, and diverging per capita consumption patterns. These trends are discussed in relation to the agricultural economics and rural sociology literatures on deregulation, farm structural adjustment, and the social consequences of industry transformation.

## 1. Introduction

The Australian dairy industry has undergone profound structural transformation over the past half-century, progressing from a fragmented collection of state-regulated markets to a deregulated national industry integrated into global commodity markets. The milking herd shrank from 2.5 million cows in 1974 to 1.5 million by 2017, yet total milk production rose from 6,500 to 9,300 megalitres over the same period -- a paradox explained by a 127% increase in average yield per cow. Farm numbers declined approximately 71% between the early 2000s and 2024 (Dairy Australia 2024), while production concentrated overwhelmingly in Victoria's three major dairying regions. The full deregulation of farmgate milk pricing on 1 July 2000, following the phased dismantling of the two-price system through the Kerin Plan (1986) and Crean Plan (1992), was the single most consequential policy event. Its effects rippled through farm economics, rural communities, and industry structure in ways that continue to shape the sector (Edwards 2003; Cocklin and Dibden 2002).

Understanding this transformation requires long-run statistical series that are currently scattered across multiple government publications and data formats. Official Australian dairy statistics are published by two principal agencies: the Australian Bureau of Statistics (ABS), which collects census and survey data on livestock numbers and agricultural production; and the Australian Bureau of Agricultural and Resource Economics and Sciences (ABARES), which publishes commodity-level production, price, and trade data in its Agricultural Commodity Statistics series. While both agencies maintain comprehensive datasets, the data is published in different formats, time granularities, and unit conventions, making longitudinal analysis cumbersome.

This paper makes two contributions. First, it documents a compiled dataset that harmonises ABS and ABARES sources into a single tidy-format dataset suitable for time series analysis (Sections 2-6). Second, it uses the compiled series to describe long-run trends in the Australian dairy industry, situating these trends within the agricultural economics and rural sociology literatures on deregulation, structural adjustment, productivity, trade, and the social consequences of industry transformation (Section 7).

## 2. Data Sources

### 2.1 ABARES Agricultural Commodity Statistics (2018 edition)

The ABARES Agricultural Commodity Statistics (ACS) was an annual publication providing comprehensive commodity-level data for Australian agriculture. The 2018 edition (the most recent available in spreadsheet form) contains 16 dairy tables (Tables 6.1-6.16) covering the period from 1974-75 to 2017-18.

We extracted data from the following tables:

| Table | Content | Variables Extracted | Period |
|-------|---------|-------------------|--------|
| 6.1 | National summary | Cow numbers, yield, milk production, butter, cheese, export prices | 1974-2017 |
| 6.4 | Dairy cow numbers by state | Milking herd by state | 1974-2017 |
| 6.5 | Milk production by state | Total milk production by state | 1974-2017 |
| 6.6 | Manufacture of dairy products | Butter, cheese, milk powder production | 1990-2017 |
| 6.7 | Consumption of dairy products | Per capita and total consumption | 1990-2017 |
| 6.8 | Milk prices and gross value | Farmgate prices (manufacturing, market, weighted average) | 1974-2017 |
| 6.9 | Export unit values | Average export prices for butter and cheese | 1974-2017 |

**Source file:** `ACS2018_DairyTables_v1.1.0.xlsx` from https://data.gov.au/data/dataset/agricultural-commodity-statistics-2017

All ABARES data uses Australian financial year (FY) timing: a year labelled 1974 corresponds to the period July 1974 to June 1975.

### 2.2 ABS Historical Selected Agricultural Commodities (1860-2022)

The ABS released a historical data cube in April 2024 covering selected agricultural commodities from 1860 to 2022, broken down by state and territory. We extracted two tables:

| Table | Content | Period |
|-------|---------|--------|
| 6 | Total cattle numbers by state | 1860-2022 |
| 8 | Dairy cattle numbers by state | 1964-2022 |

**Source file:** `historic_ag_commodities_1860_2022.xlsx` from the ABS "Agricultural Commodities, Australia 2021-22" release.

ABS data uses calendar year (CY) timing and reports livestock numbers as at a census date (typically 31 March or 30 June, varying by period).

**Important note on dairy cattle vs dairy cows:** The ABS "dairy cattle" count (Table 8) includes all animals in dairy herds -- cows in milk, dry cows, calves, heifers, and bulls. The ABARES "dairy cow" count (Table 6.1/6.4) covers only cows in milk and dry cows (the milking herd). In the year 2000, for example, ABS records 3.14 million dairy cattle while ABARES records 2.18 million dairy cows nationally.

## 3. Dataset Structure

The dataset follows a tidy (long) format with one observation per row. Each observation records a single value for a specific variable, geographic unit, and time period.

### 3.1 Schema

| Column | Type | Description |
|--------|------|-------------|
| `year` | integer | Start year of the period (e.g., 1974 for FY 1974-75 or CY 1974) |
| `year_type` | string | `FY` (financial year, Jul-Jun) or `CY` (calendar year) |
| `state_name` | string | Full state/territory name |
| `state_code` | string | Standard abbreviation (NSW, VIC, QLD, SA, WA, TAS, NT, ACT, AUS) |
| `category` | string | Variable category: production, price, herd, or consumption |
| `variable_id` | string | Machine-readable variable identifier |
| `variable_name` | string | Human-readable variable name |
| `value` | float | Observation value in standardised units |
| `unit` | string | Unit of the standardised value |
| `confidence` | string | Data quality flag (high/medium/low/interpolated) |
| `original_value` | float | Value as published in the source |
| `original_unit` | string | Original unit before standardisation |
| `notes` | string | Additional context or caveats |

### 3.2 Variables

The dataset contains 17 variables across four categories:

**Herd (4 variables)**

| Variable | Unit | Coverage | States |
|----------|------|----------|--------|
| `herd_total_cattle` | head | 1860-2022 (CY) | All 9 |
| `herd_dairy_cattle` | head | 1964-2022 (CY) | All 9 |
| `herd_dairy_cows` | head | 1974-2017 (FY) | 7 (6 states + AUS) |
| `herd_yield_per_cow` | litres | 1974-2017 (FY) | AUS only |

**Production (4 variables)**

| Variable | Unit | Coverage | States |
|----------|------|----------|--------|
| `prod_milk_total` | megalitres | 1974-2017 (FY) | 7 (6 states + AUS) |
| `prod_butter` | tonnes | 1974-2017 (FY) | AUS only |
| `prod_cheese` | tonnes | 1974-2017 (FY) | AUS only |
| `prod_milk_powder` | tonnes | 1990-2017 (FY) | AUS only |

**Price (5 variables)**

| Variable | Unit | Coverage | States |
|----------|------|----------|--------|
| `price_farmgate_avg` | cents/litre | 1974-2017 (FY) | AUS only |
| `price_farmgate_manufacturing` | cents/litre | 1974-1999 (FY) | AUS only |
| `price_farmgate_market` | cents/litre | 1974-1999 (FY) | AUS only |
| `price_export_butter` | cents/kg | 1974-2017 (FY) | AUS only |
| `price_export_cheese` | cents/kg | 1974-2017 (FY) | AUS only |

**Consumption (4 variables)**

| Variable | Unit | Coverage | States |
|----------|------|----------|--------|
| `cons_milk_total` | megalitres | 1990-2017 (FY) | AUS only |
| `cons_milk_percap` | litres | 1990-2017 (FY) | AUS only |
| `cons_butter_percap` | kg | 1990-2017 (FY) | AUS only |
| `cons_cheese_percap` | kg | 1990-2017 (FY) | AUS only |

### 3.3 Geographic Coverage

Nine geographic units: the six states (NSW, VIC, QLD, SA, WA, TAS), two territories (NT, ACT), and the national aggregate (AUS). Note that NT and ACT have negligible dairy industries; their data appears only in the ABS cattle series.

### 3.4 Unit Standardisation

All values are expressed in metric/decimal units:

| Original Unit | Standardised Unit | Conversion |
|--------------|-------------------|------------|
| '000 head | head | multiply by 1,000 |
| kt (kilotonnes) | tonnes | multiply by 1,000 |
| $/tonne | cents/kg | divide by 10 |

Original values and units are preserved in the `original_value` and `original_unit` columns.

## 4. Data Quality

### 4.1 Validation Checks

The following validation checks were performed:

1. **No missing values**: All 2,703 observations have non-null values.
2. **No negative values**: All values are zero or positive.
3. **State-national consistency**: State-level totals sum exactly to the reported national figure (verified for milk production and cattle numbers).
4. **No duplicate records**: The combination of (variable_id, state_code, year, year_type) is unique.
5. **Continuous time series**: Within each variable's range, there are no gaps in annual coverage.

### 4.2 Known Limitations

1. **Pre-1964 dairy data gap**: Dairy-specific statistics (separate from total cattle) are unavailable before 1964 in our digital sources. Earlier data exists in printed ABS Year Books and Bureau of Agricultural Economics publications but has not been digitised.

2. **Pre-1974 production and price gap**: Comprehensive dairy production volumes, prices, and trade data from ABARES begins only in 1974-75. Earlier production data would need to be sourced from historical BAE publications.

3. **Financial year vs calendar year**: ABARES and ABS use different reporting periods. Users should be aware that `year=1990, year_type=FY` represents July 1990 to June 1991, while `year=1990, year_type=CY` represents January to December 1990.

4. **Dairy cattle vs dairy cows**: The ABS "dairy cattle" and ABARES "dairy cows" variables measure different populations. See Section 2.2 for details.

5. **1964-1982 cattle classification discrepancy**: The ABS notes that from 1964 to 1982, the sum of meat and dairy cattle may not equal total cattle due to differing treatment of bulls and house cows in historical series.

6. **Post-2012 survey estimates**: ABS cattle numbers from approximately 2013 onwards are survey-based statistical estimates (with decimal precision) rather than census counts, and carry relative standard errors of 10-50% for smaller states.

7. **Manufacturing/market milk price split ends 1999**: The separate farmgate prices for manufacturing and market milk (`price_farmgate_manufacturing`, `price_farmgate_market`) end at 1999, coinciding with deregulation of the market milk system on 1 July 2000.

## 5. Potential Extensions

Several additional data sources could extend this dataset:

- **Dairy Australia "In Focus" reports** (annual): Contain state-level farm numbers, yield per cow, milk prices, and product manufacture data, extending coverage to 2023-24. Data is published in PDF format.
- **ABS Livestock Products** (quarterly, cat. 7215.0): Contains dairy-related datacubes in some editions with quarterly milk production by state.
- **ABARES Agricultural Outlook** (quarterly): Contains recent and forecast dairy data, published as Excel tables.
- **Historical digitisation**: ABS Year Books (1901 onwards) and BAE/ABARE annual reports contain dairy statistics that could fill the pre-1974 gap through manual digitisation or OCR.

## 6. Access and Reproducibility

The dataset is available as:
- **CSV**: `data/final/aus_dairy_stats.csv` (tidy long format, 2,703 rows)
- **DuckDB**: `data/dairy_stats.duckdb` (relational database with full schema)

The complete data pipeline is reproducible via:
```bash
python scripts/download_abares.py   # Download ABARES source files
python scripts/download_abs.py      # Download ABS source files
python scripts/ingest.py            # Parse all sources and load database
```

All source code is in the `scripts/` directory. Raw source files are preserved in `data/raw/` for verification.

## 7. Long-Run Trends in the Australian Dairy Industry

The compiled dataset reveals five major structural trends that together constitute the transformation of Australian dairy from a regulated, domestically oriented, extensive grazing industry into a deregulated, export-exposed, intensive production system. We discuss each trend in turn, drawing on the agricultural economics and rural sociology literatures to contextualise the statistical patterns.

### 7.1 Herd contraction and geographic concentration

The most striking trend in the dataset is the sustained contraction of the Australian dairy herd alongside its geographic concentration into southeastern Australia. ABS data records 4.84 million dairy cattle in 1964; by 2022, this had fallen 56% to 2.15 million. The ABARES milking herd series tells a similar story: 2.48 million cows in 1974, falling to a trough of 1.52 million in 2016 before a partial recovery.

The contraction was not evenly distributed. Victoria's share of national dairy cattle rose from 37.8% in 1964 to 60.1% in 2022. Queensland experienced the most dramatic decline, falling from 22.6% of the national herd in 1964 to just 4.0% in 2022 -- a collapse from 1.09 million to 85,000 head. New South Wales halved its share from 24.9% to 13.6%. Tasmania moved against the trend, increasing from 4.8% to 13.9% of the national herd. In milk production terms, Victoria's dominance is even more pronounced: by 2017, the state produced 64.2% of national milk output (5,965 of 9,289 ML), up from 57.6% in 1974.

This geographic concentration reflects the competitive advantages of southeastern Australia's temperate climate, reliable rainfall, and established processing infrastructure (Productivity Commission 2014). It also reflects the differential impact of deregulation across states. Under the two-price system, states with larger proportions of market (liquid) milk production -- particularly Queensland and New South Wales -- received higher average farmgate prices than Victoria, where the industry was predominantly manufacturing-oriented. Deregulation eliminated this price premium. Edwards (2003) estimated that Queensland farmers lost approximately 22 cents per litre in effective farmgate price upon deregulation, while Victorian farmers faced smaller adjustments because their prices were already closer to manufacturing milk values.

The regional dimension of herd contraction connects to a substantial rural sociology literature on peri-urban agricultural decline. Rowley, Hu, and Muller (2022) document how dairy farms in the Illawarra region of New South Wales declined from approximately 1,080 in 1978 to 110 by 2016-17, driven not only by milk price pressures but by rising land values from residential development, the amenity-driven transformation of coastal hinterlands, and deregulated planning systems that facilitated urban encroachment. Hu (2021) shows how family farming culture shaped Illawarra dairy farmers' responses to these pressures, with many persisting in dairying despite poor economic returns because of deep attachments to place, identity, and intergenerational continuity.

### 7.2 The productivity revolution: yield per cow

While the herd contracted, per-cow productivity underwent a remarkable transformation. Average annual yield rose from 2,623 litres per cow in 1974 to 5,951 litres in 2017 -- a 127% increase, averaging 1.9% compound growth per year. This increase was not smooth: yield growth accelerated sharply in the early 1990s, with annual yield jumping from 3,807 litres in 1990 to 4,997 litres in 1999 (a 31% increase in nine years), before plateauing after 2000.

Several factors drove this productivity revolution. Genetic improvement through selective breeding and, more recently, genomic selection contributed an estimated 0.5% per year in commercial herds (DataGene 2024; Haile-Mariam, Bowman, and Goddard 2003). The shift from production-only breeding objectives to balanced indices incorporating fertility, health, and longevity (the Australian Balanced Performance Index, or BPI) improved the sustainability of genetic gains. Feeding system intensification was equally important: Wales and Kolver (2017) report that by the mid-2010s, over 64% of Australian dairy farmers were feeding more than one tonne of concentrate dry matter per cow per year, a substantial shift from the extensive grazing systems that predominated in the 1970s and 1980s. Chapman et al. (2008) review the move towards complementary forage systems -- including maize silage, annual ryegrass, and lucerne -- that can sustain higher stocking rates and per-cow output than traditional perennial pastures.

Nossal and Sheng (2010) decompose dairy total factor productivity (TFP) growth using ABARES survey data from 1978-79 onwards, finding average TFP growth of approximately 1.2% per year. Sheng et al. (2020) extend this analysis through 2013, showing that deregulation corrected resource misallocation between farms and across formerly segmented state markets. After 2000, market share shifted from less productive to more productive farms, generating aggregate productivity gains through reallocation even as within-farm technological progress slowed. This "multi-speed" industry pattern -- where high-performing farms pull away from the mean while low performers exit -- has become a defining feature of post-deregulation dairy (ABARES dairy survey data).

The yield plateau after 2000 visible in our data coincides with the Millennium Drought (2001-2009), which severely affected irrigated dairying in northern Victoria. Van Dijk et al. (2013) show that irrigation water use in the Murray-Darling Basin fell to roughly one-third of pre-drought levels by 2007-08. Dairy farmers adapted by substituting bought-in feed for irrigated pasture, demonstrating significant adaptive capacity -- dairy showed the greatest productivity increase per unit of water of any irrigated sector during the drought -- but at higher cost and with limits to further intensification.

### 7.3 Prices: regulation, deregulation, and global exposure

The farmgate price series captures the transition from regulated to market-determined pricing. The dataset records two distinct farmgate prices -- for manufacturing milk and market (liquid) milk -- from 1974 to 1999, and a single weighted average from 1974 to 2017. The manufacturing/market split ended with deregulation on 1 July 2000.

Under the two-price system, market milk consistently commanded a premium over manufacturing milk. In 1974, market milk was priced at 14.2 cents per litre versus 5.5 cents for manufacturing milk -- a 158% premium. By 1999, the premium had narrowed to 52.3 versus 20.1 cents per litre (160% premium). This price differential reflected the regulatory architecture: state milk boards guaranteed higher returns for liquid consumption milk, while manufacturing milk was priced closer to export parity.

The weighted average farmgate price shows a distinctive pattern: steady nominal increases from 8.0 cents per litre in 1974 to 28.6 cents in 1989, followed by a decade of relative stagnation (23.5-31.1 cents, 1990-2000), then sharp volatility in the deregulated era (27.1-51.2 cents, 2001-2017). The 2007 spike to 49.6 cents per litre reflected the global dairy commodity price boom; the subsequent fall to 37.3 cents by 2009 demonstrated the new exposure to international price cycles.

Edwards (2003) provides the definitive economic analysis of deregulation, arguing it was primarily precipitated by the threat of New Zealand imports following the 1995 Uruguay Round, which made the existing two-price system unsustainable. The $1.63 billion Dairy Structural Adjustment Program (DSAP), funded by an 11-cent-per-litre consumer levy on liquid milk over eight years, partially compensated affected farmers, but the adjustment was uneven across states and farm types (ANAO 2004). The 2021 Senate inquiry into dairy industry performance found that national milk production had trended down since 2002, declining over 22% in the subsequent sixteen years, raising questions about whether deregulation had undermined the industry's productive base (Senate RRAT Committee 2021).

Export prices for butter and cheese show even greater volatility, reflecting Australia's integration into global commodity markets. Butter export prices ranged from 84 cents per kilogram (1975) to 713 cents (2017); cheese from 101 cents (1974) to 554 cents (2017). The long-run upward trend in export prices, particularly from 2006 onwards, reflects both global supply tightening and the structural decline of the Australian dollar. Australia typically accounts for approximately 5% of global dairy trade, with around 30% of production exported by value (Dairy Australia 2024).

The ACCC Dairy Inquiry (2018) found significant bargaining power imbalances in the supply chain, with all but the largest farmers lacking meaningful countervailing power against processors. The Murray Goulburn crisis of April 2016 -- when Australia's largest dairy cooperative announced a mid-season retrospective farmgate price cut -- exposed the fragility of the farmer-processor relationship and precipitated the sale of Murray Goulburn to Saputo Inc. (Canada) in 2018 and the introduction of a mandatory Dairy Industry Code of Conduct from January 2020.

### 7.4 Product mix: from butter to cheese and powder

The dataset documents a fundamental shift in Australian dairy manufacturing. Butter production peaked at 189,000 tonnes in 1998 and declined to 93,000 tonnes by 2017 -- a 51% fall. Cheese production followed the opposite trajectory, rising from 99,000 tonnes in 1974 to a peak of 412,000 tonnes in 2001 (a 316% increase), before declining modestly to 378,000 tonnes by 2017. Milk powder production, available from 1990, fluctuated between 58,000 and 239,000 tonnes without a clear trend, reflecting the commodity's role as a residual output absorbing surplus milk.

This product mix shift reflects both changing domestic consumption patterns and export market opportunities. Butter had been the foundation of Australian dairy exports since the nineteenth century, when the industry was built around the "imperial preference" for Australian butter in the British market. The loss of preferential access upon Britain's entry into the European Economic Community in 1973 forced a long-term reorientation towards cheese and powder exports to Asian markets. By the 2010s, Australia's top dairy export destinations were China, Japan, Indonesia, and Singapore -- a complete reversal from the British-dominated trade of the pre-1970s era.

Domestically, per capita butter consumption reversed its long decline, rising from 2.6 kg in 1990 to 4.7 kg in 2017, driven partly by shifting nutritional advice that rehabilitated saturated fat and partly by the rise of artisanal food culture. Per capita cheese consumption grew more steadily, from 8.7 kg (1990) to 13.6 kg (2017), reflecting the increasing prominence of cheese in Australian cuisine. Per capita fluid milk consumption was remarkably stable at 100-106 litres throughout the 1990-2017 period, showing neither the decline seen in some developed countries nor significant growth.

### 7.5 Structural adjustment and its social consequences

The aggregate trends documented above -- fewer cows, fewer farms, more milk per cow, volatile prices, shifting product mix -- translate at the farm and community level into a decades-long process of structural adjustment that has been extensively studied by rural sociologists.

The dominant dynamic is farm consolidation: farms that remain in dairy have grown substantially in scale, while smaller and less productive operations have exited. Jensen, Paul, and Azariadis (2024), surveying 147 Australian dairy farmers, find that contemporary challenges include rising operational costs, chronic labour shortages, unstable milk prices, and long working hours, with industry consolidation favouring both large-scale operations and specialised boutique producers while squeezing conventional mid-sized farms. Sheng, Zhao, and Nossal (2015) provide evidence on returns to scale that helps explain this pattern: larger farms achieve lower per-unit costs, and deregulation removed the price supports that had previously insulated smaller producers from competitive pressure.

The social toll of this adjustment has been significant. Cocklin and Dibden (2002), drawing on interviews with dairy farmers in the immediate aftermath of deregulation, document widespread anger, a sense of betrayal by government, and acute financial stress particularly among farmers who had invested heavily in expansion on the assumption that the regulated price regime would continue. Alston (2004) situates dairy adjustment within the broader pattern of Australian rural decline, documenting falling farm populations, withdrawal of rural services, and the erosion of community institutions. Kunde et al. (2018) link the transformation of rural communities and declining social cohesion to elevated farmer suicide risk, while Page and Fragar (2002) document a 60% higher suicide rate among Australian farmers compared to non-farmers during 1988-1997.

Gender dynamics in dairy structural adjustment have received sustained attention. Alston (1995, 2000) demonstrates that farm women contribute substantially to dairy operations -- including "men's work" such as milking, stock management, and machinery operation -- yet their labour is systematically rendered invisible by commodity-based definitions of farm work and patriarchal organisational structures. Alston (2012) finds that climate-related stress in northern Victorian dairy, particularly during the Millennium Drought, increased women's on- and off-farm workloads while reinforcing rather than challenging gendered divisions of labour.

Intergenerational succession presents a critical challenge for industry continuity. Leonard et al. (2017) report that only 14% of Victorian dairy farmers had finalised a transition plan, while Kennedy et al. (2021) find that farm size strongly predicts intrafamily succession, with smaller farms less likely to be transferred to the next generation. The cultural dimension of this challenge is explored by Hu (2021), who shows how dairy farmers' identities in the Illawarra are deeply bound up with family farming culture, creating tensions between economic rationality (which may counsel exit) and the social and psychological meaning of continuing the family farm.

### 7.6 The regulatory and policy arc

The trends documented above must be understood within the regulatory framework that shaped the industry for most of the twentieth century. The Commonwealth Dairy Produce Equalisation Committee (CDPEC), incorporated in 1934, determined butter and cheese prices and equalised returns between domestic and export sales for manufacturers. State milk boards controlled the production, distribution, and pricing of liquid milk in each state, creating segmented markets with different price structures and restrictions on interstate trade. The combined effect was a regulatory architecture that insulated farmers from international market signals, supported the survival of smaller and less productive farms, and maintained dairying in regions (particularly subtropical Queensland and coastal New South Wales) where it might otherwise have been uncompetitive (Industry Commission 1991).

Reform came in stages. The Kerin Plan (1986), named after Labor Primary Industries Minister John Kerin, introduced market signals into dairy manufacturing support and imposed penalty levies on above-quota production. The Crean Plan (1992) established a timeline for phasing out all remaining domestic and export support for manufacturing milk products by 30 June 2000. Full deregulation of farmgate pricing for market milk occurred simultaneously across all states on 1 July 2000, enacted through the Dairy Industry Adjustment Act 2000 (Cth).

Botterill and Cockfield (2006) place dairy deregulation within the broader evolution of Australian rural adjustment policy, tracing a shift from protecting the "family farm" to promoting the "farm business" -- a discursive transformation that reframed farm exit as economically rational adjustment rather than social failure. Pritchard (2005) analyses the implementation and maintenance of neoliberal agriculture in Australia, arguing that dairy deregulation was embedded within a broader policy paradigm that emphasised comparative advantage, trade liberalisation, and minimal government intervention in commodity markets. Gray and Lawrence (2001) offer a more critical assessment, documenting how neoliberal reforms and globalisation exacerbated inequality between regions and accelerated the decline of rural communities.

### 7.7 Environmental pressures and adaptation

The environmental dimensions of dairy intensification, though not directly captured in production statistics, are integral to the industry's trajectory. Gollnow et al. (2014) calculate the carbon footprint of average Australian milk at 1.11 kg CO2-equivalents per kilogram of fat-and-protein-corrected milk, while Eckard et al. (2025) review mitigation options suggesting 40-50% reductions in enteric methane are theoretically achievable. Dairy contributes approximately 1.6% of Australia's total greenhouse gas emissions (Dairy Australia Sustainability Framework).

Water is arguably the more binding constraint. The Millennium Drought (2001-2009) forced a fundamental restructuring of northern Victorian dairy, as water allocations plummeted and prices on temporary water markets rose to levels that made irrigated pasture uneconomic. The Murray-Darling Basin Plan (2012) subsequently transferred over 2,700 gigalitres per year of water entitlements from irrigators to environmental use, permanently reducing the water available for irrigated dairying. Wheeler et al. (2014) document the rapid expansion of water trading, with dairy farmers as significant participants, and note that inter-regional trade increased from tens of gigalitres per year pre-2006 to over 500 gigalitres by 2008-09.

The dataset captures the production consequences of these environmental pressures indirectly. National milk output peaked at 11,271 megalitres in 2001 and never recovered to that level, declining to approximately 9,000-9,800 megalitres from 2009 onwards. The geographic redistribution visible in the state-level data -- with production shifting from irrigated northern Victoria towards higher-rainfall regions in Gippsland, southwest Victoria, and Tasmania -- partly reflects adaptation to water scarcity.

## 8. Conclusion

The compiled dataset documents an industry in structural transformation. The Australian dairy industry of 2022 bears little resemblance to that of 1964, let alone 1860: the herd has contracted and concentrated, productivity has roughly doubled, regulatory protections have been dismantled, and the industry has been integrated into volatile global commodity markets. These aggregate trends, captured in the production, price, herd, and consumption series presented here, are the statistical expression of deeper changes in farm structure, rural communities, environmental pressures, and policy settings that have been extensively studied across agricultural economics and rural sociology.

The dataset's principal value lies in providing harmonised, machine-readable time series that enable quantitative analysis of these transformations. Key analytical opportunities include: time-series modelling of the farmgate price response to deregulation; spatial analysis of the geographic concentration of production; decomposition of output growth into herd size and yield components; and cross-variable analysis linking price signals to production and herd adjustment decisions.

The principal limitation is the pre-1974 gap in dairy-specific variables. Extending the dataset backwards through digitisation of historical ABS Year Books and Bureau of Agricultural Economics publications would enable analysis of the entire post-war period, including the dismantling of imperial preference, the introduction of metric units and decimal currency, and the early stages of state milk board regulation. Such an extension would be a valuable contribution to Australian agricultural history.

## References

ACCC (Australian Competition and Consumer Commission). 2018. *Dairy Inquiry Final Report*. Canberra: ACCC.

Alston, M. 1995. "Women and Their Work on Australian Farms." *Rural Sociology* 60(3): 521-532.

Alston, M. 2000. *Breaking Through the Grass Ceiling: Women, Power and Leadership in Agricultural Organisations*. London: Routledge.

Alston, M. 2004. "Who Is Down on the Farm? Social Aspects of Australian Agriculture in the 21st Century." *Agriculture and Human Values* 21(1): 37-46.

Alston, M. 2012. "Does Climatic Crisis in Australia's Food Bowl Create a Basis for Change in Agricultural Gender Relations?" *Agriculture and Human Values* 29(4): 477-488.

ANAO (Australian National Audit Office). 2004. *The Commonwealth's Administration of the Dairy Industry Adjustment Package*. Audit Report No. 36, 2003-04. Canberra: ANAO.

Australian Bureau of Agricultural and Resource Economics and Sciences (ABARES). 2018. *Agricultural Commodity Statistics 2018*. Canberra: Department of Agriculture.

Australian Bureau of Statistics (ABS). 2024. *Historical Selected Agricultural Commodities, by Australia, State and Territories, 1860 to 2022*. Cat. no. 7124.0. Canberra: ABS.

Botterill, L.C. and G. Cockfield. 2006. "Rural Adjustment Schemes: Juggling Politics, Welfare and Markets." *Australian Journal of Public Administration* 65(2): 66-77.

Chapman, D.F., S.N. Kenny, D. Beca, and I.R. Johnson. 2008. "Opportunities for Future Australian Dairy Systems: A Review." *Australian Journal of Experimental Agriculture* 48(2): 153-164.

Cocklin, C. and J. Dibden. 2002. "Taking Stock: Farmers' Reflections on the Deregulation of Australian Dairying." *Australian Geographer* 33(1): 29-42.

Cocklin, C. and J. Dibden, eds. 2005. *Sustainability and Change in Rural Australia*. Sydney: UNSW Press.

Dairy Australia. 2024. *Australian Dairy Industry In Focus 2024*. Melbourne: Dairy Australia.

DataGene. 2024. *Australian Dairy Herd Improvement Report 2024*. Melbourne: DataGene.

Eckard, R.J., et al. 2025. "Greenhouse-Gas Abatement on Australian Dairy Farms: What Are the Options?" *Animal Production Science*.

Edwards, G. 2003. "The Story of Deregulation in the Dairy Industry." *Australian Journal of Agricultural and Resource Economics* 47(1): 75-98.

Gollnow, S., V. Lundie, A.D. Moore, J. McLaren, N. van de Velde, et al. 2014. "Carbon Footprint of Milk Production from Dairy Cows in Australia." *International Dairy Journal* 37(1): 31-38.

Gray, I. and G. Lawrence. 2001. *A Future for Regional Australia: Escaping Global Misfortune*. Cambridge: Cambridge University Press.

Haile-Mariam, M., P.J. Bowman, and M.E. Goddard. 2003. "New Breeding Objectives and Selection Indices for the Australian Dairy Industry." *Journal of Dairy Science* 86(5): 1742-1752.

Hu, R. 2021. "The Family Farming Culture of Dairy Farmers: A Case-Study of the Illawarra Region, New South Wales." *Sociologia Ruralis* 61(2): 478-497.

Industry Commission. 1991. *Australian Dairy Industry*. Report No. 14. Canberra: Australian Government Publishing Service.

Jensen, R., N. Paul, and C. Azariadis. 2024. "A Survey of Australian Dairy Farmers' Attitudes to Their Business, Its Challenges and Transitioning to Alternative Enterprises." *Scientific Reports* 14: 28742.

Kennedy, A., et al. 2021. "Intergenerational Farm Succession: How Does Gender Fit?" *Land Use Policy* 109: 105612.

Kunde, L., et al. 2018. "Social Factors and Australian Farmer Suicide: A Qualitative Study." *BMC Public Health* 18: 1367.

Leonard, R., et al. 2017. "Working with Stuckness: Lessons from an Intervention to Support Intergenerational Transitions on Australian Dairy Farms." *Journal of Rural Studies* 52: 81-91.

Nossal, K. and Y. Sheng. 2010. "Productivity Growth: Trends, Drivers and Opportunities for Broadacre and Dairy Industries." *Australian Commodities* 17(1): 216-230.

Page, A. and L. Fragar. 2002. "Suicide in Australian Farming, 1988-1997." *Australian and New Zealand Journal of Psychiatry* 36(1): 81-85.

Pritchard, B. 2005. "Implementing and Maintaining Neoliberal Agriculture in Australia." *International Journal of Sociology of Agriculture and Food* 12: 1-12 and 13: 1-14.

Productivity Commission. 2014. *Relative Costs of Doing Business in Australia: Dairy Product Manufacturing*. Research Report. Canberra: Productivity Commission.

Rowley, H., R. Hu, and R. Muller. 2022. "Neoliberal Peri-Urban Economies and the Predicament of Dairy Farmers: A Case Study of the Illawarra Region, New South Wales." *Agriculture and Human Values* 40: 617-635.

Senate Rural and Regional Affairs and Transport References Committee. 2021. *Performance of Australia's Dairy Industry and the Profitability of Australian Dairy Farmers Since Deregulation in 2000*. Canberra: Commonwealth of Australia.

Sheng, Y., S. Zhao, and K. Nossal. 2015. "Productivity and Farm Size in Australian Agriculture: Reinvestigating the Returns to Scale." *Australian Journal of Agricultural and Resource Economics* 59(1): 16-38.

Sheng, Y., S. Zhao, K. Nossal, and D. Zhang. 2020. "Deregulation Reforms, Resource Reallocation and Aggregate Productivity Growth in the Australian Dairy Industry." *Australian Journal of Agricultural and Resource Economics* 64(4): 1050-1076.

van Dijk, A.I.J.M., et al. 2013. "The Millennium Drought in Southeast Australia (2001-2009): Natural and Human Causes and Implications for Water Resources, Ecosystems, Economy, and Society." *Water Resources Research* 49(2): 1040-1057.

Wales, W.J. and E.S. Kolver. 2017. "Challenges of Feeding Dairy Cows in Australia and New Zealand." *Animal Production Science* 57(7): 1366-1383.

Wheeler, S.A., et al. 2014. "Reviewing the Adoption and Impact of Water Markets in the Murray-Darling Basin and Implications for Sustainable Water Resources Management." *Ecology and Society* 19(1): 29.
