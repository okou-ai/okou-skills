---
name: sql-cookbook
description: Craft and optimize SQL for any warehouse dialect — Snowflake, BigQuery, Databricks, Redshift, PostgreSQL. Covers window functions, CTEs, aggregations, joins, funnel queries, cohort retention, deduplication, dialect translation, slow query tuning, and cross-platform syntax differences.
---

## Platform-Specific Syntax Guide

### PostgreSQL (Aurora, RDS, Supabase, Neon)

**Working with dates and times:**
```sql
-- Today and now
CURRENT_DATE, CURRENT_TIMESTAMP, NOW()

-- Adding and subtracting intervals
some_date + INTERVAL '7 days'
some_date - INTERVAL '1 month'

-- Round down to a time boundary
DATE_TRUNC('month', event_ts)

-- Pull out individual components
EXTRACT(YEAR FROM event_ts)
EXTRACT(DOW FROM event_ts)  -- Sunday = 0

-- Render as formatted text
TO_CHAR(event_ts, 'YYYY-MM-DD')
```

**Text operations:**
```sql
-- Joining strings together
first_name || ' ' || last_name
CONCAT(first_name, ' ', last_name)

-- Flexible matching
col ILIKE '%term%'  -- ignores case
col ~ '^regex$'     -- POSIX regex

-- Splitting and extracting
LEFT(str, n), RIGHT(str, n)
SPLIT_PART(str, delimiter, part_num)
REGEXP_REPLACE(str, pattern, replacement)
```

**JSON and array handling:**
```sql
-- Accessing JSON fields
payload->>'key'             -- returns text
payload->'nested'->'field'  -- returns json object
payload#>>'{a,b,c}'        -- deep path as text

-- Array utilities
ARRAY_AGG(col)
ANY(arr_col)
arr_col @> ARRAY['val']
```

**Tuning guidance:**
- Run `EXPLAIN ANALYZE` to inspect actual execution plans
- Add indexes on columns used in WHERE and JOIN conditions
- Prefer `EXISTS` over `IN` for correlated lookups
- Consider partial indexes for frequently used filter predicates
- Deploy connection pooling when handling concurrent workloads

### Snowflake

**Date and time functions:**
```sql
-- Getting current moments
CURRENT_DATE(), CURRENT_TIMESTAMP(), SYSDATE()

-- Shifting dates
DATEADD(day, 7, some_date)
DATEDIFF(day, start_dt, end_dt)

-- Truncation
DATE_TRUNC('month', event_ts)

-- Component extraction
YEAR(event_ts), MONTH(event_ts), DAY(event_ts)
DAYOFWEEK(event_ts)

-- Formatting
TO_CHAR(event_ts, 'YYYY-MM-DD')
```

**Text and pattern matching:**
```sql
-- Case-insensitive matching (default collation dependent)
col ILIKE '%term%'
REGEXP_LIKE(col, 'pattern')

-- Working with VARIANT / semi-structured data
col:key::string
PARSE_JSON('{"a": 1}')
GET_PATH(variant_col, 'path.to.field')

-- Expanding nested arrays
SELECT f.value FROM tbl, LATERAL FLATTEN(input => arr_col) f
```

**Navigating semi-structured columns:**
```sql
-- Dot-path access on VARIANT
payload:customer:name::STRING
payload:items[0]:price::NUMBER

-- Exploding nested arrays into rows
SELECT
    t.id,
    elem.value:name::STRING AS item_name,
    elem.value:qty::NUMBER AS item_qty
FROM my_table t,
LATERAL FLATTEN(input => t.payload:items) elem
```

**Tuning guidance:**
- Rely on clustering keys rather than traditional indexes for large tables
- Target clustering key columns in filters to maximize partition pruning
- Size the virtual warehouse appropriately for query complexity
- Reuse results via `RESULT_SCAN(LAST_QUERY_ID())` to skip re-execution
- Use transient tables for ephemeral staging data

### BigQuery

**Date and time functions:**
```sql
-- Current moments
CURRENT_DATE(), CURRENT_TIMESTAMP()

-- Shifting dates forward and backward
DATE_ADD(some_date, INTERVAL 7 DAY)
DATE_SUB(some_date, INTERVAL 1 MONTH)
DATE_DIFF(end_dt, start_dt, DAY)
TIMESTAMP_DIFF(end_ts, start_ts, HOUR)

-- Truncation
DATE_TRUNC(event_ts, MONTH)
TIMESTAMP_TRUNC(event_ts, HOUR)

-- Component extraction
EXTRACT(YEAR FROM event_ts)
EXTRACT(DAYOFWEEK FROM event_ts)  -- Sunday = 1

-- Display formatting
FORMAT_DATE('%Y-%m-%d', date_col)
FORMAT_TIMESTAMP('%Y-%m-%d %H:%M:%S', ts_col)
```

**Text operations:**
```sql
-- No native ILIKE; lowercase first
LOWER(col) LIKE '%term%'
REGEXP_CONTAINS(col, r'pattern')
REGEXP_EXTRACT(col, r'pattern')

-- Splitting and reassembling
SPLIT(str, delimiter)  -- produces an ARRAY
ARRAY_TO_STRING(arr, delimiter)
```

**Arrays and structs:**
```sql
-- Array utilities
ARRAY_AGG(col)
UNNEST(arr_col)
ARRAY_LENGTH(arr_col)
val IN UNNEST(arr_col)

-- Struct field access
struct_col.field_name
```

**Tuning guidance:**
- Always apply filters on partition columns (typically date) to minimize bytes scanned
- Add clustering on columns that appear frequently in WHERE clauses
- Swap `COUNT(DISTINCT ...)` for `APPROX_COUNT_DISTINCT()` on high-cardinality data
- Avoid `SELECT *` since billing scales with bytes read
- Use `DECLARE` / `SET` for parameterized script logic
- Run a dry-run estimate before executing expensive queries

### Redshift

**Date and time functions:**
```sql
-- Current moments
CURRENT_DATE, GETDATE(), SYSDATE

-- Shifting dates
DATEADD(day, 7, some_date)
DATEDIFF(day, start_dt, end_dt)

-- Truncation
DATE_TRUNC('month', event_ts)

-- Component extraction
EXTRACT(YEAR FROM event_ts)
DATE_PART('dow', event_ts)
```

**Text operations:**
```sql
-- Case-insensitive matching
col ILIKE '%term%'
REGEXP_INSTR(col, 'pattern') > 0

-- Splitting and concatenation
SPLIT_PART(str, delimiter, part_num)
LISTAGG(col, ', ') WITHIN GROUP (ORDER BY col)
```

**Tuning guidance:**
- Assign distribution keys (DISTKEY) so joined tables are co-located on the same nodes
- Define sort keys (SORTKEY) on columns commonly used for filtering
- Review query plans with `EXPLAIN`
- Watch for DS_BCAST and DS_DIST in plans (signs of costly cross-node shuffles)
- Run `ANALYZE` and `VACUUM` on a regular cadence
- Use late-binding views for flexibility when schemas evolve

### Databricks SQL

**Date and time functions:**
```sql
-- Current moments
CURRENT_DATE(), CURRENT_TIMESTAMP()

-- Shifting dates
DATE_ADD(some_date, 7)
DATEDIFF(end_dt, start_dt)
ADD_MONTHS(some_date, 1)

-- Truncation
DATE_TRUNC('MONTH', event_ts)
TRUNC(date_col, 'MM')

-- Component extraction
YEAR(event_ts), MONTH(event_ts)
DAYOFWEEK(event_ts)
```

**Delta Lake capabilities:**
```sql
-- Query historical snapshots
SELECT * FROM tbl TIMESTAMP AS OF '2024-01-15'
SELECT * FROM tbl VERSION AS OF 42

-- Inspect table history
DESCRIBE HISTORY tbl

-- Upsert with MERGE
MERGE INTO target USING source
ON target.id = source.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
```

**Tuning guidance:**
- Run `OPTIMIZE` with `ZORDER` on frequently queried columns
- Enable the Photon engine for compute-heavy workloads
- Apply `CACHE TABLE` on datasets that are read repeatedly
- Partition by low-cardinality date columns for efficient pruning

## Reusable Analytical Patterns

### Window Function Recipes

```sql
-- Assign sequential position within groups
ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY event_ts DESC)
RANK() OVER (PARTITION BY category ORDER BY revenue DESC)
DENSE_RANK() OVER (ORDER BY score DESC)

-- Cumulative sums and rolling averages
SUM(amount) OVER (ORDER BY dt ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_total
AVG(amount) OVER (ORDER BY dt ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_7d_avg

-- Accessing adjacent rows
LAG(val, 1) OVER (PARTITION BY entity ORDER BY dt) AS prior_val
LEAD(val, 1) OVER (PARTITION BY entity ORDER BY dt) AS next_val

-- Boundary values within a partition
FIRST_VALUE(status) OVER (PARTITION BY user_id ORDER BY event_ts ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
LAST_VALUE(status) OVER (PARTITION BY user_id ORDER BY event_ts ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)

-- Proportional share
revenue / SUM(revenue) OVER () AS share_of_total
revenue / SUM(revenue) OVER (PARTITION BY category) AS share_within_category
```

### Structured Queries with CTEs

```sql
WITH
-- Stage 1: Narrow down to the target population
eligible_users AS (
    SELECT user_id, signup_date, tier
    FROM users
    WHERE signup_date >= DATE '2024-01-01'
      AND account_status = 'active'
),

-- Stage 2: Derive per-user measures
per_user AS (
    SELECT
        u.user_id,
        u.tier,
        COUNT(DISTINCT e.session_id) AS sessions,
        SUM(e.revenue) AS revenue
    FROM eligible_users u
    LEFT JOIN events e ON u.user_id = e.user_id
    GROUP BY u.user_id, u.tier
),

-- Stage 3: Roll up to tier-level summary
tier_summary AS (
    SELECT
        tier,
        COUNT(*) AS users,
        AVG(sessions) AS avg_sessions,
        SUM(revenue) AS total_revenue
    FROM per_user
    GROUP BY tier
)

SELECT * FROM tier_summary ORDER BY total_revenue DESC;
```

### Cohort Retention Tracking

```sql
WITH signup_cohorts AS (
    SELECT
        user_id,
        DATE_TRUNC('month', first_seen) AS cohort
    FROM users
),
monthly_activity AS (
    SELECT
        user_id,
        DATE_TRUNC('month', activity_date) AS active_month
    FROM user_events
)
SELECT
    s.cohort,
    COUNT(DISTINCT s.user_id) AS cohort_size,
    COUNT(DISTINCT CASE
        WHEN a.active_month = s.cohort THEN a.user_id
    END) AS m0,
    COUNT(DISTINCT CASE
        WHEN a.active_month = s.cohort + INTERVAL '1 month' THEN a.user_id
    END) AS m1,
    COUNT(DISTINCT CASE
        WHEN a.active_month = s.cohort + INTERVAL '3 months' THEN a.user_id
    END) AS m3
FROM signup_cohorts s
LEFT JOIN monthly_activity a ON s.user_id = a.user_id
GROUP BY s.cohort
ORDER BY s.cohort;
```

### Conversion Funnel Measurement

```sql
WITH step_flags AS (
    SELECT
        user_id,
        MAX(CASE WHEN event_name = 'page_view' THEN 1 ELSE 0 END) AS saw_page,
        MAX(CASE WHEN event_name = 'signup_start' THEN 1 ELSE 0 END) AS began_signup,
        MAX(CASE WHEN event_name = 'signup_complete' THEN 1 ELSE 0 END) AS finished_signup,
        MAX(CASE WHEN event_name = 'first_purchase' THEN 1 ELSE 0 END) AS made_purchase
    FROM events
    WHERE event_date >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY user_id
)
SELECT
    COUNT(*) AS total_users,
    SUM(saw_page) AS viewers,
    SUM(began_signup) AS signup_starts,
    SUM(finished_signup) AS signup_completions,
    SUM(made_purchase) AS purchasers,
    ROUND(100.0 * SUM(began_signup) / NULLIF(SUM(saw_page), 0), 1) AS view_to_start_rate,
    ROUND(100.0 * SUM(finished_signup) / NULLIF(SUM(began_signup), 0), 1) AS start_to_finish_rate,
    ROUND(100.0 * SUM(made_purchase) / NULLIF(SUM(finished_signup), 0), 1) AS finish_to_purchase_rate
FROM step_flags;
```

### Removing Duplicate Records

```sql
-- Retain only the latest version of each entity
WITH ordered AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY entity_id
            ORDER BY modified_at DESC
        ) AS seq
    FROM raw_table
)
SELECT * FROM ordered WHERE seq = 1;
```

## Troubleshooting Query Failures

When a query produces an error, work through these checks:

1. **Syntax issues**: Verify dialect compatibility (e.g., BigQuery lacks `ILIKE`; only BigQuery has `SAFE_DIVIDE`)
2. **Missing columns**: Confirm column names against the actual schema; watch for case sensitivity with quoted identifiers in PostgreSQL
3. **Type conflicts**: Add explicit casts when comparing mismatched types (`CAST(col AS DATE)` or `col::DATE`)
4. **Divide-by-zero**: Wrap denominators with `NULLIF(denominator, 0)` or use platform-specific safe division
5. **Column ambiguity**: Alias every table in JOINs and always prefix column references
6. **GROUP BY violations**: Every selected column that is not inside an aggregate must appear in GROUP BY (BigQuery permits alias references as an exception)
