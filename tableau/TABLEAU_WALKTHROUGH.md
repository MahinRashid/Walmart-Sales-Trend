# Tableau walkthrough: build the Walmart Sales Trend dashboard

This guide rebuilds the 1200×800 dashboard (`images/dashboard_walmart.png`) in **Tableau Public** (Desktop Public Edition,
2023.1 or later), step by step. Then it builds the dark version.

**Time:** about 2–3 hours the first time.
**You need:** Tableau Public (free) and `data/walmart_clean.csv` from this repo.
**Reference:** the colour codes and layout grid are in [`dashboard_rebuild_guide.md`](dashboard_rebuild_guide.md).

> **Tip:** after each sheet, compare your number with the ✅ **Check** line. If it matches, move on.

---

## Contents

- [Part 1: Connect and prepare the data](#part-1-connect-and-prepare-the-data)
- [Part 2: Calculated fields](#part-2-calculated-fields)
- [Part 3: Build the worksheets](#part-3-build-the-worksheets)
- [Part 4: Assemble the 1200×800 dashboard](#part-4-assemble-the-1200800-dashboard)
- [Part 5: Filters and interactivity](#part-5-filters-and-interactivity)
- [Part 6: The dark theme](#part-6-the-dark-theme)
- [Part 7: Publish and polish](#part-7-publish-and-polish)
- [Troubleshooting](#troubleshooting)

---

## Part 1: Connect and prepare the data

1. Open Tableau Public, then go to **Connect → To a File → Text file** and choose `data/walmart_clean.csv`.
2. In the data source preview, check the field types (click the type icon above a column to change it):

   | Field | Should be |
   |---|---|
   | Date | **Date** (not string) |
   | Store, Year, Month | Number (whole) |
   | Weekly Sales, Temperature, Fuel Price, CPI, Unemployment, Store Growth 2012 Pct, Store Xmas Multiplier | Number (decimal) |
   | Holiday Flag | Number (whole) |
   | Holiday Event, Size Tier | String |

3. Click **Sheet 1** to open the first worksheet.
4. In the **Data** pane, drag **Store**, **Year** and **Month** from Measures up into Dimensions
   (or right-click each one → **Convert to Dimension**).
   Also right-click **Year** → **Convert to Discrete**.
5. Right-click **Weekly Sales** → **Default Properties → Number Format → Currency (Custom)**, with 1 decimal place and
   Display Units **Millions (M)**.
6. Save the workbook as `Walmart Sales Trend` (**File → Save to Tableau Public As…**). Tableau Public saves to the web,
   so save early and often.

---

## Part 2: Calculated fields

Create each one with **Analysis → Create Calculated Field**. Type the name exactly as shown, paste the formula, then click **OK**.

### Core measures

```text
Avg Chain Sales per Week
SUM([Weekly Sales]) / COUNTD([Date])
```
Format: Currency, 1 decimal, Millions (M).

```text
Is Pre-Christmas
[Holiday Event] = "Pre-Christmas (not flagged)"
```

```text
Regular Week Sales
{ EXCLUDE [Holiday Event] : SUM(IF [Holiday Event] = "Regular week" THEN [Weekly Sales] END) }
```

```text
Regular Week Count
{ EXCLUDE [Holiday Event] : COUNTD(IF [Holiday Event] = "Regular week" THEN [Date] END) }
```

```text
Lift vs Regular Week
[Avg Chain Sales per Week] / ( AVG([Regular Week Sales]) / AVG([Regular Week Count]) ) - 1
```
Format: Percentage, 1 decimal.

> **Why EXCLUDE and not FIXED?** `FIXED` ignores your Store and Size filters, so the baseline would always be the whole
> chain. `EXCLUDE` respects those filters and only ignores the Holiday Event split.

### KPI measures

```text
KPI Pre-Xmas Lift
( SUM(IF [Is Pre-Christmas] THEN [Weekly Sales] END) / COUNTD(IF [Is Pre-Christmas] THEN [Date] END) )
/ ( SUM(IF [Holiday Event] = "Regular week" THEN [Weekly Sales] END) / COUNTD(IF [Holiday Event] = "Regular week" THEN [Date] END) ) - 1
```

```text
Sales Jan-Oct 2011
SUM(IF [Year] = 2011 AND [Month] <= 10 THEN [Weekly Sales] END)
```

```text
Sales Jan-Oct 2012
SUM(IF [Year] = 2012 AND [Month] <= 10 THEN [Weekly Sales] END)
```

```text
KPI Growth 2012
[Sales Jan-Oct 2012] / [Sales Jan-Oct 2011] - 1
```

```text
KPI Declining Stores
STR(COUNTD(IF [Store Growth 2012 Pct] < 0 THEN [Store] END)) + " / " + STR(COUNTD([Store]))
```

### Chart helpers

```text
Bar Colour
IF [Is Pre-Christmas] THEN "Pre-Christmas" ELSE "Regular" END
```

```text
Holiday Marker
IF MAX([Holiday Flag]) = 1 THEN 0 END
```

```text
Lift Colour
IF ATTR([Holiday Event]) = "Pre-Christmas (not flagged)" THEN "Peak"
ELSEIF [Lift vs Regular Week] < 0 THEN "Negative"
ELSE "Positive" END
```

```text
Month Index
ROUND([Avg Chain Sales per Week] / TOTAL([Avg Chain Sales per Week]) * 100, 0)
```

```text
Overall Avg Week
TOTAL([Avg Chain Sales per Week])
```

```text
Month Colour
IF [Month Index] >= 105 THEN "High" ELSEIF [Month Index] < 92 THEN "Low" ELSE "Normal" END
```

```text
Store Growth
AVG([Store Growth 2012 Pct]) / 100
```
Format: Percentage, 1 decimal.

```text
Growth Colour
IF [Store Growth] < 0 THEN "Declining" ELSE "Growing" END
```

```text
Top or Bottom 5
RANK_UNIQUE([Store Growth], 'desc') <= 5 OR RANK_UNIQUE([Store Growth], 'asc') <= 5
```

```text
r Temperature     CORR([Temperature], [Weekly Sales])
r Fuel Price      CORR([Fuel Price], [Weekly Sales])
r CPI             CORR([CPI], [Weekly Sales])
r Unemployment    CORR([Unemployment], [Weekly Sales])
```
(Create these as four separate fields.)

---

## Part 3: Build the worksheets

Rename each sheet by double-clicking its tab. For every sheet, finish with these four steps:

- **Format → Shading → Worksheet:** set the background to `#FFFFFF`.
- **Format → Lines:** set Grid Lines and Zero Lines to None (or a faint grid of `#E4EDF7` where noted), and Axis Rulers to None.
- **Format → Borders:** set Row Divider and Column Divider to None.
- Hide the sheet title (right-click the title → **Hide Title**). The dashboard adds its own titles.

### Sheet 1: `KPI Total Sales`

1. Drag **Weekly Sales** onto **Text** on the Marks card. Make sure it's `SUM`.
2. Click **Text → …** and enter:
   ```
   TOTAL SALES
   <SUM(Weekly Sales)>
   ```
   Make the first line Tableau Medium, 9pt, `#3D5476`, and the value Tableau Bold, 22pt, `#041E42`. Left-align it.
3. Format the value as Currency, 2 decimals, Billions (B).

✅ **Check:** $6.74B

### Sheet 2: `KPI Avg Week`

Do the same as Sheet 1, with **Avg Chain Sales per Week** on Text and the label `AVG WEEK`.
✅ **Check:** $47.1M

### Sheet 3: `KPI Growth 2012`

Do the same, with **KPI Growth 2012** and the label `GROWTH 2012 (JAN–OCT VS 2011)`.
✅ **Check:** +2.6%. *Set the number format to `+0.0%;-0.0%` so the plus sign shows.*

### Sheet 4: `KPI Pre-Xmas Lift`

Do the same, with **KPI Pre-Xmas Lift** and the label `PRE-XMAS LIFT (NOT FLAGGED)`.
✅ **Check:** +70.3%

### Sheet 5: `KPI Declining Stores`

Do the same, with **KPI Declining Stores** and the label `DECLINING STORES`.
✅ **Check:** 8 / 45

### Sheet 6: `Sales Barcode` (the hero chart)

1. Drag **Date** onto **Columns**. Right-click the pill → choose the **second** `Day` option (green, *exact date*),
   then choose **Continuous** if it isn't already.
2. Drag **Weekly Sales** onto **Rows** (`SUM`).
3. On the Marks card, change **Automatic** to **Bar**.
4. Drag **Bar Colour** onto **Color**. Click **Color → Edit Colors**, then set
   `Regular` = `#0071CE` and `Pre-Christmas` = `#FFC220`.
5. Click **Size** and drag the slider left until each bar is thin with a hairline gap, so it looks like a barcode.
6. **Holiday dots:** drag **Holiday Marker** onto Rows, to the right of `SUM(Weekly Sales)`.
   - On the `Holiday Marker` Marks card, set the mark type to **Circle**, the colour to `#F47321` and a small size.
   - Right-click the second axis → **Dual Axis**, then right-click again → **Synchronize Axis**.
   - Right-click the right-hand axis → untick **Show Header**.
   - Remove **Measure Names** from Color on the *All* Marks card if Tableau added it.
7. **Average line:** go to the **Analytics** pane, drag **Average Line** onto the chart and drop it on **Table**, for
   `SUM(Weekly Sales)` only. Format it as a dashed line in `#3D5476`, with the label *Value*.
8. **Peak labels:** right-click the bar for 24 Dec 2010 → **Annotate → Mark**, and type `$80.9M`.
   Repeat for 23 Dec 2011 (`$77.0M`).
9. Format the date axis: **Format → Dates → Custom: `yyyy`**. Set grid lines to `#E4EDF7` (rows only).
10. **Tooltip:** click Tooltip and enter
    `Week ending <DAY(Date)>` / `<SUM(Weekly Sales)>` / `<ATTR(Holiday Event)>`.

✅ **Check:** two tall yellow bars (about $80.9M and $77.0M) and orange dots under 10 weeks.

### Sheet 7: `Holiday Lift`

1. Drag **Holiday Event** onto **Rows** and **Lift vs Regular Week** onto **Columns**.
2. Sort descending: click the sort icon on the axis.
3. **Hide** the `Regular week` row: right-click its header → **Hide**.
   *Don't filter it out. The baseline calculation needs those rows.*
4. Drag **Lift Colour** onto Color: `Peak` = `#FFC220`, `Positive` = `#0071CE`, `Negative` = `#D6332A`.
5. Drag **Lift vs Regular Week** onto **Label**, formatted as `+0.0%;-0.0%`.
6. Right-click the row header → **Edit Alias** to shorten the names: `Pre-Xmas*`, `Thanksgiving`, `Super Bowl`, `Labor Day`, `Xmas (flag)`.
7. Fix the axis: right-click the axis → **Edit Axis → Fixed**, from −0.15 to 0.95. Set ticks to every 0.4.

✅ **Check:** Pre-Xmas +70.3%, Thanksgiving +42.8%, Super Bowl +4.7%, Labor Day +1.2%, Xmas (flag) −6.7%.

### Sheet 8: `Seasonality`

1. Drag **Date** onto Columns, right-click it → choose the **first** `Month` option (blue, discrete, month name).
2. Drag **Avg Chain Sales per Week** onto Rows. Set the mark type to **Bar**.
3. Drag **Month Colour** onto Color: `High` = `#0071CE`, `Low` = `#D6332A`, `Normal` = `#B9D6F2`.
   - Click the triangle on the Month Colour pill → **Compute Using → Table (across)**.
4. Drag **Month Index** onto Label (Compute Using → **Table (across)**). To label only Jan, Nov and Dec, right-click
   each of the other bars → **Mark Label → Never Show**. Labelling every bar also reads fine.
5. **Average line:** drag **Overall Avg Week** onto **Detail**. Then go to **Analytics → Reference Line → Table**,
   with Value = `AGG(Overall Avg Week)`, a dashed line, and the label `avg week = 100`.
6. Format the month headers as single letters: right-click the header → **Format → Dates → Custom `mmmmm`**.

✅ **Check:** Jan 88, Nov 110, Dec 122.

### Sheet 9: `Store Momentum`

1. Drag **Store** onto Rows and **Store Growth** onto Columns.
2. Sort Store by **Store Growth** descending: click the Store pill → **Sort → Field → Store Growth → Descending**.
3. Drag **Top or Bottom 5** onto **Filters** and tick **True**.
   - Click the pill → **Edit Table Calculation → Compute Using → Table (down)**.
4. Drag **Growth Colour** onto Color: `Growing` = `#0071CE`, `Declining` = `#D6332A`.
5. Drag **Store Growth** onto Label.
6. To show "Store 38" instead of "38", create a calculated field `Store Label` = `"Store " + STR([Store])`.
   Put it on Rows in front of **Store**, then right-click the **Store** pill → untick **Show Header**.
   Keep **Store** in the view, because the click-to-filter action in Part 5 uses it. Re-apply the sort from step 2 to **Store Label**.

✅ **Check:** top is Store 38 (+14.3%), bottom is Store 36 (−17.5%), 10 rows.

### Sheet 10: `External Factors`

1. Drag **r Temperature** onto Columns. Then drag **r Fuel Price**, **r CPI** and **r Unemployment** onto the *same
   axis* until the pill turns into **Measure Values**.
2. Make sure **Measure Names** is on Rows. Remove any other measures from the Measure Values card.
3. Mark type: **Bar**. Colour: `#0071CE`.
4. Fix the axis at −1 to +1: right-click the axis → **Edit Axis → Fixed**.
5. **Analytics → Reference Band → Table**, from a constant −0.3 to a constant 0.3. Set the fill to `#B9D6F2` at 50%,
   with no label. This is the "weak or no link" zone.
6. Drag **Measure Values** onto Label, formatted as `+0.00;-0.00`.
7. Edit the aliases of Measure Names to `Temperature`, `Fuel price`, `CPI`, `Unemployment`.

✅ **Check:** −0.06, +0.01, −0.07, −0.11.

---

## Part 4: Assemble the 1200×800 dashboard

### 4.1 Canvas

1. Click **New Dashboard** (the icon at the bottom) and name it `Walmart Sales Trend`.
2. In the **Dashboard** pane, go to **Size → Fixed size → Custom**, with Width **1200** and Height **800**.
3. **Format → Dashboard → Default shading:** `#EEF5FC`.
4. Leave **Show dashboard title** unticked. You'll build your own header band instead.

### 4.2 Layout skeleton (containers)

Use **Tiled** objects. Build them from the outside in:

```
Vertical container (whole canvas, outer padding 16)
├── Horizontal container: HEADER           height 68, background #0071CE
├── Horizontal container: KPI ROW          height 74
├── Horizontal container: MIDDLE ROW       height 270
│     ├── Sales Barcode                   width 784
│     └── Text: Recommendations           width 372
└── Horizontal container: BOTTOM ROW       fills the rest (~330)
      ├── Holiday Lift  ├── Seasonality  ├── Store Momentum  └── External Factors   (distribute evenly)
```

Steps:

1. Drag a **Vertical** object onto the canvas. In **Layout → Outer padding**, set 16.
2. Drag four **Horizontal** objects into it, stacked top to bottom.
   Select each one and set its exact height in **Layout → Position / Size** (use **Fixed height** in the item hierarchy).
3. Drop the sheets into their containers. Right-click each container → **Distribute Contents Evenly** where noted.
4. Set the **inner padding** of each panel object to 12 (Layout tab), and its background to `#FFFFFF`.
   This gives the white cards on the light canvas.

### 4.3 Header band

1. Select the HEADER container and set **Layout → Background** to `#0071CE`.
2. Drag a **Text** object in and type:
   ```
   Walmart Sales Trend · 2010–2012
   45 stores, flat all year until Thanksgiving and the week before Christmas.
   ```
   Line 1: Tableau Bold, 22pt, white, with `· 2010–2012` in `#FFC220`. Line 2: 10pt, `#D6E8FA`.
3. Leave space on the right for the filters (Part 5).

### 4.4 KPI cards that look like shelf labels

For each of the five KPI sheets, build the card like this:

1. Drag a **Vertical** container into the KPI ROW.
2. Put a **Blank** object at the top. Set its height to **4px** and its background to `#0071CE`
   (`#FFC220` for the Pre-Xmas card). This is the shelf-label top edge.
3. Put the KPI sheet below it, with a white background and inner padding of 8–10.
4. Right-click the KPI ROW → **Distribute Contents Evenly**, with 12px between cards
   (set outer padding 6 on each card).

### 4.5 Panel titles

Each chart panel has a small **eyebrow** line and a **takeaway title**. Add a Text object above each sheet, inside the same
vertical container:

| Sheet | Eyebrow (8pt, `#6E819C`, CAPS) | Title (12pt bold, `#041E42`) |
|---|---|---|
| Sales Barcode | THE SALES BARCODE · ONE BAR PER WEEK | Two spikes a year carry the calendar |
| Holiday Lift | AVG SALES VS A REGULAR WEEK | Only two holidays matter |
| Seasonality | AVG WEEK BY MONTH · INDEX | December peaks, January slumps |
| Store Momentum | 2012 VS 2011 · CLICK A STORE | Store momentum |
| External Factors | CORRELATION WITH WEEKLY SALES | Weather & economy barely register |

### 4.6 Recommendations panel

Drag a **Text** object into the right side of the MIDDLE ROW (width 372) and enter:

```
RECOMMENDATIONS
What to do about it

BI & FORECAST   Fix the holiday calendar. The peak is the 2 weeks before Christmas, not the flagged week.
STORE OPS       Staff and stock up for Thanksgiving–Dec 24. Treat Super Bowl as a normal week.
OPS & HR        Plan for January, 12% below average: clearance and lighter schedules.
REGIONAL        Review Store 14 (−$7.3M) and Store 36 (−17.5%). Learn from 38, 44, 39.
SUPPLY CHAIN    Allocate holiday stock per store. Peaks range from 1.0x to 2.05x.
```

Colour the owner labels `#0071CE`, bold the first sentence of each line, and use `#3D5476` for the rest.

---

## Part 5: Filters and interactivity

### 5.1 Filters in the header

1. Select the **Sales Barcode** sheet on the dashboard → click its drop-down arrow → **Filters → Year**, then repeat
   for **Size Tier** and **Store**.
2. Drag the three filter cards into the HEADER container, on the right.
3. Change each card's style (drop-down arrow on the card):
   - **Year:** *Single Value (list)*. Format it horizontally, or use *Single Value (dropdown)* if space is tight.
   - **Size Tier** and **Store:** *Single Value (dropdown)*, with "All" included.
4. Apply each filter to the right sheets (card drop-down → **Apply to Worksheets → Selected Worksheets…**):

   | Filter | Apply to |
   |---|---|
   | Year | KPI Total Sales, KPI Avg Week, KPI Pre-Xmas Lift, Sales Barcode, Holiday Lift, Seasonality, External Factors |
   | Size Tier | **All** sheets using this data source |
   | Store | All sheets **except** Store Momentum |

   > Growth KPIs and Store Momentum always compare Jan–Oct 2012 with 2011, so the Year filter must not touch them.

5. Format the filter cards: transparent background, white title text (they sit on the blue band).

### 5.2 Click a store to filter the page

1. **Dashboard → Actions → Add Action → Filter…**
2. Name: `Filter by store`. Source sheet: **Store Momentum**. Run action on: **Select**.
3. Target sheets: all sheets **except** Store Momentum.
4. Clearing the selection will: **Show all values**.
5. Target filters: **Selected fields → Store**.

### 5.3 Tooltips

Write tooltips as plain sentences. For Store Momentum, use:
`Store <Store>: <AGG(Store Growth)> Jan–Oct 2012 vs 2011`.

✅ **Check:** click Store 14. The KPI Total Sales card should show $289.0M and Declining Stores should show 1 / 1.

---

## Part 6: The dark theme

The easiest reliable method is a second dashboard in the same workbook, built from duplicated sheets.

1. Right-click each of the 10 worksheet tabs → **Duplicate**, and rename them with a ` (Dark)` suffix.
2. On each Dark sheet, change the colours:

   | Element | Walmart theme | Dark theme |
   |---|---|---|
   | Sheet background | `#FFFFFF` | `#1B1F25` |
   | Text, values | `#041E42` | `#F3F5F8` |
   | Labels, axis text | `#3D5476` | `#B3BAC5` |
   | Grid lines | `#E4EDF7` | `#232830` |
   | Data bars | `#0071CE` | `#5AA9F0` |
   | Muted months (`Normal`) | `#B9D6F2` | `#2A3F5C` |
   | Peak (`Pre-Christmas`, `Peak`) | `#FFC220` | `#FFC220` |
   | Negative / declining | `#D6332A` | `#FF6B5E` |
   | Holiday dots | `#F47321` | `#FF8A3D` |

   Set text colours under **Format → Font → Sheet** (Worksheet and Pane) for each sheet.
3. Right-click the `Walmart Sales Trend` dashboard tab → **Duplicate** → rename it `Walmart Sales Trend (Dark)`.
4. In the duplicate, swap each sheet for its Dark copy: select the sheet object → drop-down → **Swap Sheets**
   (or use the swap icon in the Dashboard pane).
5. Shading: dashboard `#121519`, panels `#1B1F25`, header container **no** blue band (same as canvas), KPI top edges
   `#4EA1F3`, and title year in `#FFC220`.
6. Update the action in Part 5.2 for the dark dashboard: point it at **Store Momentum (Dark)**.

> **Optional, advanced: one dashboard with a theme switch.** Tableau 2022.3+ supports **Dynamic Zone Visibility**.
> Create a parameter `Theme` (string list: `Walmart`, `Dark`) and two boolean calcs, `Show Walmart` = `[Theme] = "Walmart"`
> and `Show Dark` = `[Theme] = "Dark"`. Put each theme's whole layout in its own container. Select a container →
> **Layout → Control visibility using value** → choose the matching calc. Show the parameter control in the header.

---

## Part 7: Publish and polish

1. **Final checklist** (compare with [`dashboard_rebuild_guide.md`](dashboard_rebuild_guide.md)):
   - [ ] Total $6.74B · Avg week $47.1M · Growth +2.6% · Pre-Xmas +70.3% · Declining 8 / 45
   - [ ] No chart uses a line to connect stores or CPI values
   - [ ] Every title is a takeaway sentence
   - [ ] Yellow appears only on the pre-Christmas peak, and red only on negatives
   - [ ] All filters and the store click action work, and Clear restores all values
2. **File → Save to Tableau Public.** In your Tableau Public profile, open the viz → **Edit Details**. Add the title,
   a 2-line description of the key findings, and a link to the GitHub repo.
3. Set the dashboard as the **thumbnail**, and turn on **Show sheets as tabs** if you want both themes visible.
4. Download a PNG (**Download → Image**) and save it as `images/dashboard_tableau.png`. Then add it to the README.
5. Update the Tableau link in `README.md` if the URL changed.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Date shows as text or years look wrong | Change the Date field type to **Date** in the data source. The clean CSV uses `yyyy-mm-dd`, so it parses automatically. |
| Holiday Lift values are all 0% or blank | You *filtered* out "Regular week". Remove that filter and **hide** the row instead. |
| Lift numbers ignore the Store filter | You used `FIXED` instead of `EXCLUDE` in Regular Week Sales and Regular Week Count. |
| Month Index is 100 for every month | Set Compute Using → **Table (across)** on Month Index and Month Colour. |
| Top or Bottom 5 shows 1 row or 45 rows | Set the table calculation's **Compute Using → Table (down)**. |
| CORR shows null | CORR needs an extract. Tableau Public always uses one, so check that the fields are numbers, not strings. |
| Dashboard looks different on Tableau Public | Fonts fall back on the web. Use Tableau's built-in fonts (Tableau Book / Medium / Bold). |
| Bars in the barcode overlap or have big gaps | Change the Size slider, or right-click the Date axis → **Edit Axis** to remove the extra range at each end. |
