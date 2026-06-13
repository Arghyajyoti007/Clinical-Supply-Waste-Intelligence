-- ============================================================
-- Clinical Supply Chain Waste Intelligence Platform
-- Schema Creation Scripts
-- Author: Arghyajyoti Samui
-- Platform: Microsoft Fabric Lakehouse (Spark SQL)
-- ============================================================

-- ============================================================
-- STEP 1: CREATE SCHEMAS (Medallion Architecture)
-- ============================================================

CREATE SCHEMA IF NOT EXISTS clinical_supply_lakehouse.silver;
CREATE SCHEMA IF NOT EXISTS clinical_supply_lakehouse.gold;

-- ============================================================
-- STEP 2: SILVER LAYER — DIMENSION TABLES
-- ============================================================

-- dim_hospital: Unique hospitals with surrogate keys
CREATE TABLE IF NOT EXISTS silver.dim_hospital (
    hospital_id     INT,
    hospital_name   STRING
);

-- dim_ward: Unique ward types with surrogate keys
CREATE TABLE IF NOT EXISTS silver.dim_ward (
    ward_id     INT,
    ward        STRING
);

-- dim_category: Supply categories with surrogate keys
CREATE TABLE IF NOT EXISTS silver.dim_category (
    category_id     INT,
    category        STRING
);

-- dim_item: Medical/pharmaceutical items with surrogate keys
CREATE TABLE IF NOT EXISTS silver.dim_item (
    item_id     INT,
    item_name   STRING
);

-- dim_supplier: Suppliers with surrogate keys
CREATE TABLE IF NOT EXISTS silver.dim_supplier (
    supplier_id     INT,
    supplier_name   STRING
);

-- ============================================================
-- STEP 3: SILVER LAYER — FACT TABLE
-- ============================================================

-- fact_supply_inventory: Core transactional data
-- Grain: One row per supply record per hospital per ward
CREATE TABLE IF NOT EXISTS silver.fact_supply_inventory (
    record_id           STRING,         -- Natural key from source
    hospital_id         INT,            -- FK → dim_hospital
    ward_id             INT,            -- FK → dim_ward
    category_id         INT,            -- FK → dim_category
    item_id             INT,            -- FK → dim_item
    supplier_id         INT,            -- FK → dim_supplier
    received_date       DATE,           -- When item was received
    expiry_date         DATE,           -- When item expires
    shelf_life_days     INT,            -- Total usable life (days)
    days_until_expiry   INT,            -- Days remaining (negative = expired)
    is_expired          BOOLEAN,        -- True if past expiry date
    qty_received        INT,            -- Quantity received in shipment
    qty_remaining       INT,            -- Quantity still in stock
    unit_cost_usd       DOUBLE,         -- Cost per unit (USD)
    waste_value_usd     DOUBLE,         -- Financial waste value (USD)
    procurement_month   STRING          -- YYYY-MM format for trend analysis
);

-- ============================================================
-- STEP 4: GOLD LAYER — KPI TABLES
-- ============================================================

-- kpi_waste_summary: Monthly waste KPIs for Executive Overview
CREATE TABLE IF NOT EXISTS gold.kpi_waste_summary (
    procurement_month           STRING,
    total_waste_value_usd       DOUBLE,     -- Total waste this month
    expired_stock_value_usd     DOUBLE,     -- Value of expired stock
    expired_item_count          BIGINT,     -- Count of expired items
    critical_zone_count         BIGINT,     -- Items expiring in 0-10 days
    at_risk_count               BIGINT,     -- Items expiring in 11-30 days
    total_inventory_value_usd   DOUBLE      -- Total inventory value
);

-- kpi_waste_by_location: Location-level waste for heatmap
CREATE TABLE IF NOT EXISTS gold.kpi_waste_by_location (
    hospital_name       STRING,
    ward                STRING,
    total_waste_usd     DOUBLE,     -- Total waste at this location
    expired_count       BIGINT,     -- Expired items at this location
    at_risk_count       BIGINT,     -- At-risk items at this location
    total_qty_remaining BIGINT      -- Remaining quantity at this location
);

-- kpi_supplier_item: Supplier and item risk analysis
CREATE TABLE IF NOT EXISTS gold.kpi_supplier_item (
    supplier_name       STRING,
    item_name           STRING,
    category            STRING,
    total_waste_usd     DOUBLE,     -- Waste attributed to supplier+item
    expired_count       BIGINT,     -- Expired items from this supplier
    total_qty_remaining BIGINT,     -- Remaining quantity
    total_cost_usd      DOUBLE,     -- Total procurement cost
    critical_zone_count BIGINT      -- Items expiring in 0-10 days
);
