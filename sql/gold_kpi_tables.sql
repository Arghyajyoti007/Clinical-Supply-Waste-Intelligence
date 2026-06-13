-- creating GOLD tables for PowerBi visualization

-- creating kpi_waste_summary table
CREATE OR REPLACE TABLE gold.kpi_waste_summary AS
SELECT
    procurement_month,
    ROUND(SUM(waste_value_usd), 2)                              AS total_waste_value_usd,
    ROUND(SUM(CASE WHEN is_expired = true 
              THEN unit_cost_usd * qty_remaining ELSE 0 END), 2) AS expired_stock_value_usd,
    COUNT(CASE WHEN is_expired = true THEN 1 END)               AS expired_item_count,
    COUNT(CASE WHEN days_until_expiry BETWEEN 0 AND 10 
               THEN 1 END)                                      AS critical_zone_count,
    COUNT(CASE WHEN days_until_expiry BETWEEN 11 AND 30 
               THEN 1 END)                                      AS at_risk_count,
    ROUND(SUM(unit_cost_usd), 2)                                AS total_inventory_value_usd
FROM silver.fact_supply_inventory
GROUP BY procurement_month
ORDER BY procurement_month;


-- creating kpi_waste_by_location table
CREATE OR REPLACE TABLE gold.kpi_waste_by_location AS
SELECT
    h.hospital_name,
    w.ward,
    ROUND(SUM(f.waste_value_usd), 2)                        AS total_waste_usd,
    COUNT(CASE WHEN f.is_expired = true THEN 1 END)         AS expired_count,
    COUNT(CASE WHEN f.days_until_expiry BETWEEN 0 
               AND 30 THEN 1 END)                           AS at_risk_count,
    SUM(f.qty_remaining)                                    AS total_qty_remaining
FROM silver.fact_supply_inventory f
JOIN silver.dim_hospital h ON f.hospital_id = h.hospital_id
JOIN silver.dim_ward w     ON f.ward_id = w.ward_id
GROUP BY h.hospital_name, w.ward
ORDER BY total_waste_usd DESC;


-- creating kpi_supplier_item table
CREATE OR REPLACE TABLE gold.kpi_supplier_item AS
SELECT
    s.supplier_name,
    i.item_name,
    c.category,
    ROUND(SUM(f.waste_value_usd), 2)                        AS total_waste_usd,
    COUNT(CASE WHEN f.is_expired = true THEN 1 END)         AS expired_count,
    SUM(f.qty_remaining)                                    AS total_qty_remaining,
    ROUND(SUM(f.unit_cost_usd), 2)                          AS total_cost_usd,
    COUNT(CASE WHEN f.days_until_expiry 
               BETWEEN 0 AND 10 THEN 1 END)                 AS critical_zone_count
FROM silver.fact_supply_inventory f
JOIN silver.dim_supplier s  ON f.supplier_id = s.supplier_id
JOIN silver.dim_item i      ON f.item_id = i.item_id
JOIN silver.dim_category c  ON f.category_id = c.category_id
GROUP BY s.supplier_name, i.item_name, c.category
ORDER BY total_waste_usd DESC;


-- Validating all the tables in GOLD layer
SELECT 'kpi_waste_summary'     AS table_name, COUNT(*) AS row_count 
FROM gold.kpi_waste_summary
UNION ALL
SELECT 'kpi_waste_by_location', COUNT(*) 
FROM gold.kpi_waste_by_location
UNION ALL
SELECT 'kpi_supplier_item',     COUNT(*) 
FROM gold.kpi_supplier_item;
