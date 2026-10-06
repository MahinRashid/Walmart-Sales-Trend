# Walmart Store Sales Analysis: what actually drives sales?

An end-to-end retail analytics case study using **SQL, Python, Excel and Tableau**: 45 Walmart stores, 143 weeks
(Feb 2010 – Oct 2012), 6,435 store-weeks and **$6.74B in sales**.

**Headline:** sales are driven by **two weeks of the calendar and a handful of stores**, not by the economy.
The biggest week of the year isn't even flagged as a holiday in the source data.

📄 **[Full report](REPORT.md)** ·
🖥️ [Interactive web dashboard](dashboard/index.html) (enable GitHub Pages to share it as a live link) ·
📊 [Tableau dashboard](https://public.tableau.com/app/profile/nishad.rashid.mahi/viz/WalmartSales_17286028604180/WalmartSalesTrend) ·
📓 [Python notebook](notebooks/walmart_sales_analysis.ipynb) ·
🗄️ [SQL queries](sql/02_business_questions.sql) ([results](sql/query_results.md)) ·
📗 [Excel summary](excel/Walmart_Store_Performance.xlsx)

![Dashboard, Walmart theme](images/dashboard_walmart.png)

<details><summary>Dark theme</summary>

![Dashboard, dark theme](images/dashboard_dark.png)

</details>

---

## What I improved from version 1

I first built this project as a single Tableau dashboard. Version 2 is a full rework: I went back to the data,
found a labelling problem that changed the main conclusion, and rebuilt every part of the project around business questions.

| Version 1 (first dashboard) | Version 2 (this repo) |
|---|---|
| ![Version 1 dashboard](Project%20finalized.png) | ![Version 2 dashboard](images/dashboard_walmart.png) |

| Area | Version 1 | Version 2 |
|---|---|---|
| **Business framing** | No stated question; README was one sentence | Three business questions, 6 findings, 6 recommendations with owners, and a [full report](REPORT.md) |
| **Data quality** | Raw holiday flag used as-is | Found that the flag **misses the biggest week of the year** (pre-Christmas, +70%) and marks the week *after* Christmas instead. Built a corrected `Holiday_Event` field |
| **Dates** | Not checked | Source uses dd-mm-yyyy; parsed explicitly so days and months aren't swapped |
| **Tools** | Tableau only | SQL (10 queries, window functions, correlation in SQL), Python notebook, formula-driven Excel, Tableau and an HTML/JS dashboard |
| **Holiday chart** | Two coloured blocks, no values | Lift by named holiday with % labels (+70%, +43%, +5%, +1%, −7%) |
| **Store chart** | Line chart across store numbers (implies a trend that doesn't exist) | Ranked diverging bars showing growth and decline, top & bottom 5 |
| **CPI chart** | Line drawn across CPI values (fake trend) | Replaced with a correlation panel showing all four external factors are weak |
| **Temperature chart** | 6,400 overlapping circles | Covered by the correlation panel; no overplotting |
| **Trend chart** | Monthly totals that mix 4- and 5-week months; unexplained second line | Weekly "sales barcode" with flagged holidays marked and peaks labelled |
| **Design** | Dark gradient, low contrast, no KPIs | Fixed 1200×800 layout, Walmart colour theme plus a dark theme, KPI cards, takeaway titles; yellow used only for the peak and red only for declines |
| **Interactivity** | None | Year, store-size and store filters; click a store to filter the whole dashboard |
| **Validation** | None | Every number cross-checked across SQL, pandas and Excel |

---

## Business problem

Regional leadership needs to plan **inventory, staffing and promotions** across 45 stores. They asked three questions:

1. **When** do sales peak, and which holidays really matter?
2. **Where** do sales come from, and which stores are gaining or losing ground?
3. **What** drives sales? Should temperature, fuel price, CPI or unemployment go into the forecast?

---

## Key findings

### 1. The biggest week of the year is mislabelled in the data
The pre-Christmas week (ending Dec 24 / Dec 23) averages **$79.0M, +70% vs a regular week**, but the dataset flags it
as a *normal* week. The week it does flag as "Christmas" (ending Dec 31) is **7% below** a normal week, because shoppers
have already bought. Any report that uses the raw holiday flag understates the holiday effect and points planners at the wrong week.

![Weekly sales trend](images/01_weekly_sales_trend.png)

### 2. Only two holidays move the needle
| Holiday week | Avg chain sales | Lift vs regular week |
|---|---|---|
| Pre-Christmas *(not flagged)* | $79.0M | **+70.3%** |
| Thanksgiving / Black Friday | $66.2M | **+42.8%** |
| Super Bowl | $48.6M | +4.7% |
| Labor Day | $46.9M | +1.2% |
| "Christmas" *(flagged week)* | $43.2M | −6.7% |

The raw holiday vs non-holiday comparison shows only **+7.8%** and hides this pattern completely.

![Holiday lift](images/02_holiday_lift.png)

### 3. Strong Q4, then a January slump
December weeks run **22% above** average and November weeks **10% above**. January is the weakest month at **12% below**.
The rest of the year is flat, within ±6% of average. Like-for-like sales were essentially flat: −0.6% in 2011
and +2.5% in 2012 (Feb–Oct).

![Seasonality](images/03_seasonality_by_month.png)

### 4. Revenue is concentrated, and one top store is losing ground fast
* The **12 largest stores generate 45% of sales**; the 11 smallest generate under 10%. The biggest store sells about 8x the smallest per week.
* **37 of 45 stores grew** in Jan–Oct 2012 vs 2011.
* **Store 14** (#3 by revenue) lost **$7.3M (−8.6%)**, about half of the $14.8M lost by all 8 declining stores.
  **Store 36** fell fastest (−17.5%).
* **Stores 38, 44 and 39** grew **11–14%**. Store 39 alone added $6.5M.

![Store growth](images/04_store_growth.png)

### 5. Holiday demand is not the same across stores
The median store sells **1.7x** its normal week in the pre-Christmas week, and Stores 15, 45 and 29 sell over **2x**.
But **8 smaller stores** (33, 36, 42, 38, 43, 37, 30, 44) show almost **no Christmas peak** (0.97–1.22x).

![Christmas peak by store](images/05_christmas_peak_by_store.png)

### 6. External factors don't explain sales
Temperature, fuel price, CPI and unemployment all show correlations between **−0.11 and +0.01** with weekly sales,
and no factor is stronger than ±0.13 within individual stores. In this data, CPI mainly identifies a store's region,
so an apparent "CPI effect" is really a store-mix effect.

![External factors](images/06_external_factors.png)

---

## Recommendations

| # | Recommendation | Based on | Who acts |
|---|---|---|---|
| 1 | **Fix the holiday calendar** used in reporting and forecasting. Treat the 2 weeks before Christmas as the peak period, and stop treating the week after Christmas as a holiday. | Finding 1 | BI / Forecasting |
| 2 | **Concentrate peak staffing, stock and promotion budget on Thanksgiving through Dec 24.** Plan Super Bowl and Labor Day as normal weeks. | Findings 1–2 | Store Ops, Merchandising |
| 3 | **Plan for the January slump**: clearance pricing, lighter staffing schedules, and use the quieter weeks for training and store resets. | Finding 3 | Store Ops, HR |
| 4 | **Run a performance review of Store 14** (−$7.3M) and **Store 36** (−17.5%): check local competition, out-of-stocks, staffing levels and customer service scores. Study **Stores 38, 44 and 39** for practices to copy. | Finding 4 | Regional Management |
| 5 | **Allocate holiday inventory per store**, using each store's own peak multiplier (1.0x–2.05x) instead of a single chain-wide uplift. This avoids over-stocking the 8 low-peak stores and running short in the 2x stores. | Finding 5 | Supply Chain |
| 6 | **Forecast from store history and calendar effects.** Don't spend modelling effort on temperature, fuel, CPI or unemployment for weekly store planning. | Finding 6 | Forecasting |

---

## Approach

| Step | Tool | What was done |
|---|---|---|
| Data validation | SQL, Python | Checked row counts, nulls, duplicates and complete store histories. Parsed the dd-mm-yyyy dates explicitly (default US parsing silently swaps day and month). |
| Feature engineering | SQL view, pandas | Added `Holiday_Event` to name each holiday and separate the unflagged pre-Christmas week. Added year/month fields, store size tiers and store growth. |
| Analysis | SQL | 10 business queries: CTEs, conditional aggregation, window functions (`RANK`, `NTILE`, `LAG`, running `SUM OVER` for Pareto), and Pearson correlation written in pure SQL. |
| Deep dive & charts | Python | pandas + matplotlib notebook: trend, holiday lift, seasonality, store momentum, store-level holiday sensitivity, correlation. |
| Manager summary | Excel | Formula-driven workbook (SUMIFS / AVERAGEIFS / RANK / SUMPRODUCT, conditional formatting, charts) that recalculates if the data changes. |
| Dashboard | Tableau, HTML/JS | Redesigned 1200×800 Tableau dashboard (LOD expressions, table calculations, filter actions) and an interactive web version with two themes. |

## Repository structure

```
├── Walmart.csv                         # raw data (Kaggle Walmart sales dataset)
├── data/
│   ├── walmart_clean.csv               # cleaned + enriched data used by Tableau
│   └── store_summary.csv               # one row per store: size, tier, growth, Christmas multiplier
├── sql/
│   ├── 01_create_and_clean.sql         # schema, cleaning view, data-quality checks
│   ├── 02_business_questions.sql       # 10 business queries
│   ├── run_sql.py                      # loads the CSV into SQLite and runs everything
│   └── query_results.md                # output of every query
├── notebooks/
│   ├── walmart_sales_analysis.ipynb    # full analysis with outputs
│   └── build_notebook.py               # regenerates the notebook and charts
├── excel/Walmart_Store_Performance.xlsx
├── REPORT.md                           # full analysis report
├── Walmart Sales.twb, *.hyper          # version 1 Tableau workbook + extract
├── dashboard/
│   ├── index.html                      # interactive web dashboard (open in a browser)
│   └── template.html, data.json, build_dashboard.py
├── images/                             # charts used in this README
└── Project finalized.png               # version 1 dashboard screenshot
```

## Reproduce

```bash
pip install pandas matplotlib openpyxl
python sql/run_sql.py               # SQL results -> sql/query_results.md
python notebooks/build_notebook.py  # notebook + charts + data/*.csv
python excel/build_excel.py         # Excel workbook (open in Excel to calculate)
python dashboard/build_dashboard.py # dashboard/index.html
```

## Limitations & next steps

* Only 2.75 years and 45 stores. There's no product, department, margin, foot-traffic or store-size data, so the analysis
  can show *where* and *when* sales change but not fully *why*.
* Correlation is not causation. The weak macro correlations apply to weekly store sales in this period only.
* **Next steps:** add store type/size and department-level sales to diagnose Store 14. Build a seasonal forecast
  (e.g. SARIMA or Prophet) using the corrected holiday calendar and measure the accuracy gain over the raw flag.

---

**Nishad Rashid Mahi**: MBA, PMP, Microsoft Certified Business Analyst · Vancouver, BC
