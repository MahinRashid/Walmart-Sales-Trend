/* =====================================================================
   Walmart Sales Analysis — 01: Schema & cleaning
   Dialect: SQLite (ANSI-style; ports to PostgreSQL / SQL Server with
            minor date-function changes)
   Source : Walmart.csv — 6,435 rows, 45 stores x 143 weeks
            (week-ending dates 2010-02-05 to 2012-10-26)
   ===================================================================== */

-- 1. Raw table, loaded 1:1 from the CSV (done by run_sql.py)
DROP TABLE IF EXISTS walmart_raw;
CREATE TABLE walmart_raw (
    Store         INTEGER,
    Date          TEXT,      -- dd-mm-yyyy in the source file
    Weekly_Sales  REAL,
    Holiday_Flag  INTEGER,   -- 1 = week contains a major US holiday
    Temperature   REAL,      -- deg F
    Fuel_Price    REAL,      -- USD / gallon
    CPI           REAL,
    Unemployment  REAL       -- %
);

-- 2. Clean, analysis-ready view
--    * converts dd-mm-yyyy text to ISO dates so they sort and filter correctly
--    * adds calendar fields
--    * adds Holiday_Event: names the holiday behind each flagged week, and
--      separates the PRE-CHRISTMAS week (week ending Dec 18-24), which the
--      source flag does NOT mark as a holiday
DROP VIEW IF EXISTS sales;
CREATE VIEW sales AS
SELECT
    Store,
    DATE(SUBSTR(Date, 7, 4) || '-' || SUBSTR(Date, 4, 2) || '-' || SUBSTR(Date, 1, 2)) AS week_date,
    CAST(SUBSTR(Date, 7, 4) AS INTEGER) AS yr,
    CAST(SUBSTR(Date, 4, 2) AS INTEGER) AS mon,
    CAST(SUBSTR(Date, 1, 2) AS INTEGER) AS dy,
    Weekly_Sales  AS weekly_sales,
    Holiday_Flag  AS holiday_flag,
    Temperature   AS temperature,
    Fuel_Price    AS fuel_price,
    CPI           AS cpi,
    Unemployment  AS unemployment,
    CASE
        WHEN Holiday_Flag = 1 AND CAST(SUBSTR(Date, 4, 2) AS INTEGER) = 2  THEN 'Super Bowl'
        WHEN Holiday_Flag = 1 AND CAST(SUBSTR(Date, 4, 2) AS INTEGER) = 9  THEN 'Labor Day'
        WHEN Holiday_Flag = 1 AND CAST(SUBSTR(Date, 4, 2) AS INTEGER) = 11 THEN 'Thanksgiving'
        WHEN Holiday_Flag = 1 AND CAST(SUBSTR(Date, 4, 2) AS INTEGER) = 12 THEN 'Christmas (flagged week)'
        WHEN CAST(SUBSTR(Date, 4, 2) AS INTEGER) = 12
         AND CAST(SUBSTR(Date, 1, 2) AS INTEGER) BETWEEN 18 AND 24          THEN 'Pre-Christmas (not flagged)'
        ELSE 'Regular week'
    END AS holiday_event
FROM walmart_raw;

-- 3. Data-quality checks (expected: 6435 rows, 0 nulls, 0 duplicates,
--    45 stores, 143 weeks, every store reports every week)
SELECT 'row_count'        AS check_name, COUNT(*) AS result FROM sales
UNION ALL
SELECT 'null_sales',       COUNT(*) FROM sales WHERE weekly_sales IS NULL
UNION ALL
SELECT 'duplicate_store_weeks', COUNT(*) FROM (
    SELECT Store, week_date FROM sales GROUP BY Store, week_date HAVING COUNT(*) > 1)
UNION ALL
SELECT 'distinct_stores',  COUNT(DISTINCT Store) FROM sales
UNION ALL
SELECT 'distinct_weeks',   COUNT(DISTINCT week_date) FROM sales
UNION ALL
SELECT 'stores_missing_weeks', COUNT(*) FROM (
    SELECT Store FROM sales GROUP BY Store HAVING COUNT(*) <> 143);
