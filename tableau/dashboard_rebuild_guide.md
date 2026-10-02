# Tableau dashboard rebuild guide

A step-by-step plan for rebuilding the Tableau Public dashboard so that it tells the story from the analysis.
Use **`data/walmart_clean.csv`** as the data source. It already contains ISO dates, `Holiday_Event`, `Size_Tier`,
`Store_Growth_2012_pct` and `Store_Xmas_Multiplier`, so there's no date parsing or extra joins to do in Tableau.

## What changes from v1, and why

| v1 sheet | Problem | v2 replacement |
|---|---|---|
| Weekly Sales Over Time (monthly, 2 lines) | Monthly totals mix 4- and 5-week months, and the 2nd line isn't explained | **Weekly trend**: one line, holiday weeks marked, pre-Christmas peaks annotated |
| Sales Distribution by CPI (line) | A line across CPI values draws a fake trend; CPI here just identifies the region | Removed. Replaced by the **External factors** correlation bar |
| Holidays vs Non-Holidays (2 coloured blocks) | No values, and it relies on the mislabelled flag | **Holiday lift** bar by event, with % labels |
| Impact of Temperature (6,400 big circles) | Overplotted; shows nothing | Covered by **External factors**; optional small scatter at 20% opacity |
| Sales by Store (line) | A line across store IDs implies a sequence | **Store growth** sorted diverging bar + **store ranking** bar |
| Dark gradient background | Low contrast, hard to read | Two clean themes (Walmart colours and dark), one blue for data, Spark yellow only for the peak story, red only for negatives |

## Visual themes

The web dashboard has a **Walmart / Dark** switch in the header. In Tableau, build the Walmart theme first, then duplicate
the dashboard and re-shade it for the dark version. Tableau Public shows them as two tabs.

| Role | Walmart theme | Dark theme | Use |
|---|---|---|---|
| Outer background | `#D9E7F5` | `#08090B` | Behind the dashboard |
| Dashboard background | `#EEF5FC` | `#121519` | Main canvas |
| Header band | `#0071CE` (Walmart blue), white text | none, same as canvas | Title row |
| Panels | `#FFFFFF` | `#1B1F25` | Every chart container, 5px corners |
| Text | `#041E42` / `#3D5476` / `#6E819C` | `#F3F5F8` / `#B3BAC5` / `#7C8592` | Titles / labels / small print |
| Gridlines | `#E4EDF7` | `#232830` | Faint grid only |
| Data blue | `#0071CE` | `#5AA9F0` | All normal bars, KPI card top borders |
| Muted bars | `#B9D6F2` | `#2A3F5C` | Normal months in the seasonality chart |
| Spark yellow | `#FFC220` | `#FFC220` | **Only** the pre-Christmas peak, the active filter and the year in the title |
| Decline red | `#D6332A` | `#FF6B5E` | Only negative values |
| Holiday flag | `#F47321` (Walmart orange) | `#FF8A3D` | Holiday-flag markers |

In Tableau: Format → Workbook sets fonts and text colour, and Format → Shading sets the sheet and dashboard backgrounds.
Turn off zero lines and borders.

* **Fonts:** Archivo (wide, heavy) for titles and KPI numbers, IBM Plex Sans for text, IBM Plex Mono for axis labels and small print. In Tableau Public, use Arial Black / Arial / Courier New if the Google fonts aren't installed.
* **KPI cards look like shelf-edge price labels:** a 4px blue top border (Spark yellow on the pre-Christmas card), a big number, and a dashed rule above a small grey caption.
* **Hero:** the weekly bars form a "sales barcode": thin bars, 1px gaps, the two pre-Christmas bars in yellow, with orange dots under the flagged holiday weeks.
* Chart titles are takeaway sentences. Small uppercase mono "eyebrow" labels above them say what is measured.

## Layout (1200 x 800, fixed size)

In Tableau: **Dashboard → Size → Fixed size → 1200 x 800**. Outer padding 16px, 12px between objects.
The web dashboard (`dashboard/index.html`) uses exactly this grid, so you can use it as a pixel reference.

```
┌──────────────────────────────────────────────────────────────── 1200 ─┐
│ Walmart Sales Trend · 45 stores · Feb 2010 – Oct 2012   [Year][Size][Store] │  52px
├────────────┬────────────┬────────────┬────────────┬────────────┤
│ Total sales│ Avg week   │ Growth 2012│ Pre-Xmas   │ Declining  │  74px
│ $6.74B     │ $47.1M     │ +2.6%      │ +70.3%     │ 8 / 45     │
├────────────┴────────────┴────────────┴─┬──────────┴────────────┤
│ Sales barcode: 143 weekly bars          │ Recommendations       │  270px
│ (pre-Christmas bars yellow)             │ (5 one-line actions)  │
├───────────────┬───────────────┬────────┴──────┬────────────────┤
│ Holiday lift  │ Month index   │ Store momentum │ External factors│  ~336px
│ (bar)         │ (bar)         │ top/bottom 5   │ (r gauges)      │
└───────────────┴───────────────┴───────────────┴────────────────┘  800
```

Column widths: middle row = 784px + 372px; bottom row = 4 equal panels (~283px each).

## Calculated fields

```text
// Week-level chain sales baseline (regular weeks only)
[Regular Week Avg]
{ FIXED : AVG( { FIXED [Date] : SUM(IF [Holiday Event] = "Regular week" THEN [Weekly Sales] END) } ) }

// Lift vs regular week, used in the Holiday lift sheet (view: Holiday Event on Rows)
[Lift vs Regular]
AVG({ FIXED [Date], [Holiday Event] : SUM([Weekly Sales]) }) / MIN([Regular Week Avg]) - 1

// Growth colour (diverging bar)
[Growth Direction]
IF MIN([Store Growth 2012 Pct]) < 0 THEN "Declining" ELSE "Growing" END

// KPI: declining stores
[Declining Stores]
COUNTD(IF [Store Growth 2012 Pct] < 0 THEN [Store] END)

// Like-for-like YoY (Jan–Oct)
[Sales Jan-Oct 2011]  SUM(IF [Year] = 2011 AND [Month] <= 10 THEN [Weekly Sales] END)
[Sales Jan-Oct 2012]  SUM(IF [Year] = 2012 AND [Month] <= 10 THEN [Weekly Sales] END)
[YoY Growth]          [Sales Jan-Oct 2012] / [Sales Jan-Oct 2011] - 1
```

Expected values to check against: total $6.74B, average week $47.1M, YoY +2.6% (Jan–Oct), pre-Christmas lift +70.3%,
Thanksgiving +42.8%, Super Bowl +4.7%, Labor Day +1.2%, flagged Christmas −6.7%, 8 declining stores.

## Sheet specs

1. **KPI cards:** one sheet per KPI. Big number at 28pt, label at 10pt grey. No borders.
2. **Weekly trend:** `Date` (exact date, continuous) on Columns, `SUM(Weekly Sales)` on Rows, bars in data blue #2456C9 (thin, 1px gaps, the "sales barcode").
   Dual-mark the holiday weeks as orange #E0662E circles (same axis, synchronized). Add annotations on 2010-12-24 and
   2011-12-23: "Pre-Christmas week, not flagged as holiday". Add a reference line for the average.
3. **Holiday lift:** `Holiday Event` on Rows (exclude "Regular week"), `[Lift vs Regular]` on Columns, sorted descending.
   Colour: yellow #F4C430 for pre-Christmas, blue for other positives, red #CF3B36 if < 0. Show labels as +0.0%.
4. **Store growth:** `Store` on Rows sorted by `Store Growth 2012 Pct`, `[Growth Direction]` on Colour (blue/red).
   Label only the top 3 and bottom 3.
5. **Seasonality:** `MONTH(Date)` on Columns, `AVG` of weekly chain sales on Rows. Highlight Nov–Dec in blue, Jan in red,
   all other months light blue #C9D7F6.
6. **External factors:** hard-code the four correlations from `sql/query_results.md` (Q10) in a small table,
   or use Tableau's `CORR()` table calculation. Fix the axis to −1…+1 so the reader sees how small the values are.
7. **Findings text box:** three bullets, copied from the README's key findings.

## Interactivity

* Filters at the top: Year, Size tier, Store (multi-select), applied to all sheets that use this data source.
* Dashboard action: click a store in **Store growth** to filter the **Weekly trend** to that store.
* Tooltips: plain sentences, e.g. *"Store 14: Jan–Oct 2012 sales $77.4M, −8.6% vs 2011 (−$7.3M)"*.

## Before publishing

- [ ] All numbers match the "expected values" above
- [ ] No sheet uses a line to connect categories (stores, CPI values)
- [ ] Every chart title is a takeaway sentence, not a label
- [ ] Red is used only for negatives
- [ ] Export a PNG to `images/dashboard_v2.png` and update the README link
