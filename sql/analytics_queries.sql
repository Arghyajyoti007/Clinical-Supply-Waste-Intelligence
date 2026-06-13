-- Q1: Count total number of records in the fact table.
select count(*) from silver.fact_supply_inventory;

-- Q2: Show all distinct hospitals and how many records each has. Order by record count descending.
select distinct dh.hospital_name, count(fsi.record_id) as total_records 
from silver.fact_supply_inventory fsi
left join silver.dim_hospital dh
on fsi.hospital_id = dh.hospital_id
group by dh.hospital_name
order by total_records desc;

-- Q3: How many items are currently expired vs not expired? Show as two rows with a label.
SELECT
    CASE WHEN is_expired = true THEN 'Expired' ELSE 'Not Expired' END AS label,
    COUNT(*) AS total_count
FROM silver.fact_supply_inventory
GROUP BY CASE WHEN is_expired = true THEN 'Expired' ELSE 'Not Expired' END;

-- Q4: Calculate total waste_value_usd per category. Round to 2 decimals. Order highest waste first.
select 
    dc.category,
    round(sum(fsi.waste_value_usd),2) total_waste
    
from silver.fact_supply_inventory fsi
left JOIN silver.dim_category dc
on dc.category_id = fsi.category_id
group by dc.category
order by total_waste desc;

-- Q5: Find the top 5 suppliers by total waste value. Show supplier name and total waste.
-- select supplier_name from fact_supply_inventory
select 
    ds.supplier_name supplier, round(sum(fsi.waste_value_usd),2) total_waste
from silver.fact_supply_inventory fsi
left JOIN silver.dim_supplier ds
on ds.supplier_id = fsi.supplier_id
group by ds.supplier_name
order by total_waste desc
limit 5;

-- Q6: Which hospital has the highest number of critical zone items (0-10 days until expiry)?
select 
    dh.hospital_name,
    count(*) as count_critical_zone_items
from silver.fact_supply_inventory fsi
left JOIN silver.dim_hospital dh
on dh.hospital_id = fsi.hospital_id
where days_until_expiry between 0 and 10
group by dh.hospital_name
order by count_critical_zone_items desc
limit 1
;

-- Q7: Write a query joining fact + dim_hospital + dim_ward showing:
-- hospital_name
-- ward
-- total_waste_usd
-- expired_count
-- Only show rows where total_waste_usd > 0. Order by total_waste_usd descending.
select 
    dh.hospital_name hospital,
    dw.ward ward,
    sum(fact.waste_value_usd) as total_waste_usd,
    count(CASE WHEN fact.is_expired = true THEN 1 END) as expired_count 
from silver.fact_supply_inventory fact
INNER JOIN silver.dim_hospital dh
ON dh.hospital_id = fact.hospital_id
INNER JOIN silver.dim_ward dw
ON dw.ward_id = fact.ward_id
GROUP BY dh.hospital_name, dw.ward
HAVING sum(fact.waste_value_usd) > 0
ORDER BY total_waste_usd DESC
;

-- Q8: Find the top 3 most wasteful items per category. Show category, item_name, total_waste_usd.
WITH ranked AS(
    SELECT 
        dc.category category, 
        di.item_name item, 
        sum(fact.waste_value_usd) total_waste_usd,
        dense_rank() OVER (PARTITION BY category ORDER BY sum(fact.waste_value_usd) DESC) AS rank_category
    FROM silver.fact_supply_inventory fact
    INNER JOIN silver.dim_item di
    ON di.item_id = fact.item_id
    INNER JOIN silver.dim_category dc
    ON dc.category_id = fact.category_id
    GROUP BY dc.category , di.item_name
    ORDER BY total_waste_usd DESC
)
SELECT category, item, total_waste_usd FROM ranked
WHERE rank_category <= 3
ORDER BY category, rank_category
;

-- Q9: Rank suppliers by total waste value using RANK(). Show rank, supplier_name, total_waste_usd.

SELECT 
    ds.supplier_name as supplier,
    SUM(fact.waste_value_usd) as total_waste_value,
    RANK() OVER (ORDER BY SUM(fact.waste_value_usd) DESC) AS supplier_rank
FROM silver.fact_supply_inventory fact 
INNER JOIN silver.dim_supplier ds
ON ds.supplier_id = fact.supplier_id
GROUP BY ds.supplier_name
;

-- Q10: Calculate cumulative waste value by month using a window function. 
-- Show procurement_month and running_total_waste.
-- Step 1 inside CTE: get monthly totals
-- Step 2 outside CTE: apply SUM() OVER (ORDER BY month)
WITH monthly AS (
    SELECT
        procurement_month,
        ROUND(SUM(waste_value_usd), 2) AS monthly_waste
    FROM silver.fact_supply_inventory
    GROUP BY procurement_month
)
SELECT
    procurement_month,
    monthly_waste,
    SUM(monthly_waste) OVER (ORDER BY procurement_month) AS running_total_waste
FROM monthly;
