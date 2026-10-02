/* =====================================================================
   Walmart Sales Analysis — 02: Business questions
   Every query runs against the cleaned `sales` view from 01_create_and_clean.sql.
   Results for each query are saved in sql/query_results.md by run_sql.py.
   Techniques used: CTEs, CASE, conditional aggregation, window functions
   (RANK, NTILE, SUM OVER, running totals), and Pearson correlation in pure SQL.
   ===================================================================== */


-- @Q1 Headline KPIs: how big is the business in this dataset?
SELECT
    COUNT(DISTINCT Store)                                   AS stores,
    COUNT(DISTINCT week_date)                               AS weeks,
    MIN(week_date)                                          AS first_week,
    MAX(week_date)                                          AS last_week,
    ROUND(SUM(weekly_sales) / 1e9, 2)                       AS total_sales_bn,
    ROUND(SUM(weekly_sales) / COUNT(DISTINCT week_date) / 1e6, 1) AS avg_chain_sales_per_week_m,
    ROUND(AVG(weekly_sales) / 1e6, 2)                       AS avg_store_sales_per_week_m
FROM sales;


-- @Q2 Is the chain growing? Like-for-like Feb–Oct comparison
-- (2010 starts in February and 2012 ends in October, so full years are not comparable)
WITH yearly AS (
    SELECT yr, SUM(weekly_sales) AS sales_feb_oct
    FROM sales
    WHERE mon BETWEEN 2 AND 10
    GROUP BY yr
)
SELECT
    yr,
    ROUND(sales_feb_oct / 1e9, 3)                                        AS sales_feb_oct_bn,
    ROUND(100.0 * (sales_feb_oct / LAG(sales_feb_oct) OVER (ORDER BY yr) - 1), 1) AS yoy_growth_pct
FROM yearly
ORDER BY yr;


-- @Q3 Which holidays actually lift sales? (chain sales per week vs. regular-week baseline)
WITH weekly AS (
    SELECT week_date, holiday_event, SUM(weekly_sales) AS chain_sales
    FROM sales
    GROUP BY week_date, holiday_event
),
baseline AS (
    SELECT AVG(chain_sales) AS base FROM weekly WHERE holiday_event = 'Regular week'
)
SELECT
    w.holiday_event,
    COUNT(*)                                        AS weeks,
    ROUND(AVG(w.chain_sales) / 1e6, 1)              AS avg_chain_sales_m,
    ROUND(100.0 * (AVG(w.chain_sales) / b.base - 1), 1) AS lift_vs_regular_pct
FROM weekly w CROSS JOIN baseline b
GROUP BY w.holiday_event, b.base
ORDER BY lift_vs_regular_pct DESC;


-- @Q4 The 10 biggest weeks — and whether the source data flags them as holidays
SELECT
    week_date,
    ROUND(SUM(weekly_sales) / 1e6, 1) AS chain_sales_m,
    MAX(holiday_flag)                 AS holiday_flag,
    MAX(holiday_event)                AS holiday_event
FROM sales
GROUP BY week_date
ORDER BY chain_sales_m DESC
LIMIT 10;


-- @Q5 Seasonality: average chain sales per week by month, indexed to the overall average (100)
WITH weekly AS (
    SELECT week_date, mon, SUM(weekly_sales) AS chain_sales
    FROM sales GROUP BY week_date, mon
)
SELECT
    mon                                                              AS month,
    COUNT(*)                                                         AS weeks,
    ROUND(AVG(chain_sales) / 1e6, 1)                                 AS avg_weekly_sales_m,
    ROUND(100.0 * AVG(chain_sales) / (SELECT AVG(chain_sales) FROM weekly), 0) AS index_vs_avg
FROM weekly
GROUP BY mon
ORDER BY mon;


-- @Q6 Store league table: rank, share of chain sales and cumulative share (Pareto)
WITH store_totals AS (
    SELECT Store, SUM(weekly_sales) AS total_sales
    FROM sales GROUP BY Store
)
SELECT
    RANK() OVER (ORDER BY total_sales DESC)                         AS sales_rank,
    Store,
    ROUND(total_sales / 1e6, 1)                                     AS total_sales_m,
    ROUND(100.0 * total_sales / SUM(total_sales) OVER (), 2)        AS share_pct,
    ROUND(100.0 * SUM(total_sales) OVER (ORDER BY total_sales DESC
          ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
          / SUM(total_sales) OVER (), 1)                            AS cumulative_share_pct
FROM store_totals
ORDER BY sales_rank;


-- @Q7 Store momentum: Jan–Oct 2012 vs Jan–Oct 2011 (growth % and dollar change)
WITH ytd AS (
    SELECT
        Store,
        SUM(CASE WHEN yr = 2011 AND mon <= 10 THEN weekly_sales END) AS ytd_2011,
        SUM(CASE WHEN yr = 2012 AND mon <= 10 THEN weekly_sales END) AS ytd_2012
    FROM sales GROUP BY Store
)
SELECT
    Store,
    ROUND(ytd_2011 / 1e6, 1)                         AS ytd_2011_m,
    ROUND(ytd_2012 / 1e6, 1)                         AS ytd_2012_m,
    ROUND((ytd_2012 - ytd_2011) / 1e6, 1)            AS change_m,
    ROUND(100.0 * (ytd_2012 / ytd_2011 - 1), 1)      AS growth_pct,
    CASE WHEN ytd_2012 < ytd_2011 THEN 'Declining' ELSE 'Growing' END AS status
FROM ytd
ORDER BY growth_pct;


-- @Q8 Store size tiers (quartiles by average weekly sales): how concentrated is revenue?
WITH store_avg AS (
    SELECT Store, AVG(weekly_sales) AS avg_week, SUM(weekly_sales) AS total_sales
    FROM sales GROUP BY Store
),
tiered AS (
    SELECT *, NTILE(4) OVER (ORDER BY avg_week DESC) AS tier
    FROM store_avg
)
SELECT
    CASE tier WHEN 1 THEN '1 - Large' WHEN 2 THEN '2 - Upper-mid'
              WHEN 3 THEN '3 - Lower-mid' ELSE '4 - Small' END        AS size_tier,
    COUNT(*)                                                          AS stores,
    ROUND(AVG(avg_week) / 1e6, 2)                                     AS avg_weekly_sales_m,
    ROUND(100.0 * SUM(total_sales) / (SELECT SUM(total_sales) FROM store_avg), 1) AS share_of_sales_pct
FROM tiered
GROUP BY tier
ORDER BY tier;


-- @Q9 Holiday sensitivity by store: pre-Christmas week sales vs. the store's own average week
--     (>1.8 = needs heavy seasonal stock/staff; ~1.0 = barely any Christmas peak)
WITH store_avg AS (
    SELECT Store, AVG(weekly_sales) AS avg_week FROM sales GROUP BY Store
),
pre_xmas AS (
    SELECT Store, AVG(weekly_sales) AS pre_xmas_week
    FROM sales WHERE holiday_event = 'Pre-Christmas (not flagged)'
    GROUP BY Store
)
SELECT
    p.Store,
    ROUND(a.avg_week / 1e6, 2)               AS avg_week_m,
    ROUND(p.pre_xmas_week / 1e6, 2)          AS pre_xmas_week_m,
    ROUND(p.pre_xmas_week / a.avg_week, 2)   AS peak_multiplier
FROM pre_xmas p JOIN store_avg a USING (Store)
ORDER BY peak_multiplier DESC;


-- @Q10 Do external factors drive sales? Pearson correlation computed in SQL
--      r = (n*Sxy - Sx*Sy) / sqrt((n*Sxx - Sx^2) * (n*Syy - Sy^2))
WITH f AS (
    SELECT 'Temperature' AS factor, temperature  AS x, weekly_sales AS y FROM sales UNION ALL
    SELECT 'Fuel price',             fuel_price,       weekly_sales      FROM sales UNION ALL
    SELECT 'CPI',                    cpi,              weekly_sales      FROM sales UNION ALL
    SELECT 'Unemployment',           unemployment,     weekly_sales      FROM sales
)
SELECT
    factor,
    ROUND( (COUNT(*) * SUM(x*y) - SUM(x) * SUM(y))
         / SQRT( (COUNT(*) * SUM(x*x) - SUM(x) * SUM(x))
               * (COUNT(*) * SUM(y*y) - SUM(y) * SUM(y)) ), 3) AS pearson_r
FROM f
GROUP BY factor
ORDER BY ABS(pearson_r) DESC;
