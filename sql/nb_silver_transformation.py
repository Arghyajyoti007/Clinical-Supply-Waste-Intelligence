#!/usr/bin/env python
# coding: utf-8

# ## nb_silver_transformation
# 
# null

# In[15]:


import pandas as pd

wrangler_sample_df = pd.read_csv("https://aka.ms/wrangler/titanic.csv")
display(wrangler_sample_df)


# In[3]:


# Welcome to your new notebook
# Type here in the cell editor to add code!
# Read raw CSV from Bronze layer
df_raw = spark.read.format("csv").options(header = True, inferSchema="True").load("Files/bronze/supply_chain/clinical_supply_raw.csv")

print(f"Total rows: {df_raw.count()}")
print(f"Columns: {df_raw.columns}")
df_raw.printSchema()


# In[4]:


from pyspark.sql.functions import col, sum as spark_sum

# Check nulls in every column
null_counts = df_raw.select([
    spark_sum(col(c).isNull().cast("int")).alias(c) 
    for c in df_raw.columns
])
null_counts.show()


# In[5]:


from pyspark.sql.functions import monotonically_increasing_id, dense_rank
from pyspark.sql.window import Window
from pyspark.sql import functions as F

# dim_hospital
dim_hospital = df_raw.select("hospital_name").distinct()\
    .withColumn("hospital_id", dense_rank().over(Window.orderBy("hospital_name")))\
    .select("hospital_id", "hospital_name")

# dim_ward
dim_ward = df_raw.select("ward").distinct()\
    .withColumn("ward_id", dense_rank().over(Window.orderBy("ward")))\
    .select("ward_id", "ward")

# dim_category
dim_category = df_raw.select("category").distinct()\
    .withColumn("category_id", dense_rank().over(Window.orderBy("category")))\
    .select("category_id", "category")

# dim_item
dim_item = df_raw.select("item_name").distinct()\
    .withColumn("item_id", dense_rank().over(Window.orderBy("item_name")))\
    .select("item_id", "item_name")

# dim_supplier
dim_supplier = df_raw.select("supplier_name").distinct()\
    .withColumn("supplier_id", dense_rank().over(Window.orderBy("supplier_name")))\
    .select("supplier_id", "supplier_name")

dim_hospital.show()
dim_supplier.show()


# In[6]:


# Join dimensions to get surrogate keys into fact table
fact = df_raw\
    .join(dim_hospital, "hospital_name")\
    .join(dim_ward, "ward")\
    .join(dim_category, "category")\
    .join(dim_item, "item_name")\
    .join(dim_supplier, "supplier_name")\
    .select(
        "record_id",
        "hospital_id", "ward_id", "category_id", "item_id", "supplier_id",
        "received_date", "expiry_date",
        "shelf_life_days", "days_until_expiry", "is_expired",
        "qty_received", "qty_remaining",
        "unit_cost_usd", "waste_value_usd",
        "procurement_month"
    )

print(f"Fact table rows: {fact.count()}")
fact.show(5)


# In[8]:


# Create schemas explicitly
spark.sql("CREATE SCHEMA IF NOT EXISTS clinical_supply_lakehouse.silver")
spark.sql("CREATE SCHEMA IF NOT EXISTS clinical_supply_lakehouse.gold")
print("✅ Schemas created successfully")


# In[9]:


# Save as Delta tables in Silver schema
dim_hospital.write.format("delta").mode("overwrite")\
    .saveAsTable("silver.dim_hospital")

dim_ward.write.format("delta").mode("overwrite")\
    .saveAsTable("silver.dim_ward")

dim_category.write.format("delta").mode("overwrite")\
    .saveAsTable("silver.dim_category")

dim_item.write.format("delta").mode("overwrite")\
    .saveAsTable("silver.dim_item")

dim_supplier.write.format("delta").mode("overwrite")\
    .saveAsTable("silver.dim_supplier")

fact.write.format("delta").mode("overwrite")\
    .saveAsTable("silver.fact_supply_inventory")

print("✅ All Silver tables written successfully!")


# In[1]:


# The command is not a standard IPython magic command. It is designed for use within Fabric notebooks only.
# %%sql
# select * from silver.dim_category;

# select * from silver.dim_hospital;

# select * from silver.dim_item;

# select * from silver.dim_supplier;

# select * from silver.dim_ward;

# select * from silver.fact_supply_inventory;


# In[5]:


# The command is not a standard IPython magic command. It is designed for use within Fabric notebooks only.
# %%sql
# -- Level 1 — Warm Up
# -- Q1: Count total number of records in the fact table.
# select count(*) from silver.fact_supply_inventory;

# -- Q2: Show all distinct hospitals and how many records each has. Order by record count descending.
# select distinct dh.hospital_name, count(fsi.record_id) as total_records 
# from silver.fact_supply_inventory fsi
# left join silver.dim_hospital dh
# on fsi.hospital_id = dh.hospital_id
# group by dh.hospital_name
# order by total_records desc;

# -- Q3: How many items are currently expired vs not expired? Show as two rows with a label.
# SELECT
#     CASE WHEN is_expired = true THEN 'Expired' ELSE 'Not Expired' END AS label,
#     COUNT(*) AS total_count
# FROM silver.fact_supply_inventory
# GROUP BY CASE WHEN is_expired = true THEN 'Expired' ELSE 'Not Expired' END;
# ;



# In[1]:


# The command is not a standard IPython magic command. It is designed for use within Fabric notebooks only.
# %%sql
# -- Q4: Calculate total waste_value_usd per category. Round to 2 decimals. Order highest waste first.
# select 
#     dc.category,
#     round(sum(fsi.waste_value_usd),2) total_waste
    
# from silver.fact_supply_inventory fsi
# left JOIN silver.dim_category dc
# on dc.category_id = fsi.category_id
# group by dc.category
# order by total_waste desc;

# -- Q5: Find the top 5 suppliers by total waste value. Show supplier name and total waste.
# -- select supplier_name from fact_supply_inventory
# select 
#     ds.supplier_name supplier, round(sum(fsi.waste_value_usd),2) total_waste
# from silver.fact_supply_inventory fsi
# left JOIN silver.dim_supplier ds
# on ds.supplier_id = fsi.supplier_id
# group by ds.supplier_name
# order by total_waste desc
# limit 5;

# -- Q6: Which hospital has the highest number of critical zone items (0-10 days until expiry)?
# select 
#     dh.hospital_name,
#     count(*) as count_critical_zone_items
# from silver.fact_supply_inventory fsi
# left JOIN silver.dim_hospital dh
# on dh.hospital_id = fsi.hospital_id
# where days_until_expiry between 0 and 10
# group by dh.hospital_name
# order by count_critical_zone_items desc
# limit 1
# ;


# In[26]:


# The command is not a standard IPython magic command. It is designed for use within Fabric notebooks only.
# %%sql
# -- Q7: Write a query joining fact + dim_hospital + dim_ward showing:
# -- hospital_name
# -- ward
# -- total_waste_usd
# -- expired_count
# -- Only show rows where total_waste_usd > 0. Order by total_waste_usd descending.
# select 
#     dh.hospital_name hospital,
#     dw.ward ward,
#     sum(fact.waste_value_usd) as total_waste_usd,
#     count(CASE WHEN fact.is_expired = true THEN 1 END) as expired_count 
# from silver.fact_supply_inventory fact
# INNER JOIN silver.dim_hospital dh
# ON dh.hospital_id = fact.hospital_id
# INNER JOIN silver.dim_ward dw
# ON dw.ward_id = fact.ward_id
# GROUP BY dh.hospital_name, dw.ward
# HAVING sum(fact.waste_value_usd) > 0
# ORDER BY total_waste_usd DESC
# ;


# -- Q8: Find the top 3 most wasteful items per category. Show category, item_name, total_waste_usd.
# WITH ranked AS(
#     SELECT 
#         dc.category category, 
#         di.item_name item, 
#         sum(fact.waste_value_usd) total_waste_usd,
#         dense_rank() OVER (PARTITION BY category ORDER BY sum(fact.waste_value_usd) DESC) AS rank_category
#     FROM silver.fact_supply_inventory fact
#     INNER JOIN silver.dim_item di
#     ON di.item_id = fact.item_id
#     INNER JOIN silver.dim_category dc
#     ON dc.category_id = fact.category_id
#     GROUP BY dc.category , di.item_name
#     ORDER BY total_waste_usd DESC
# )
# SELECT category, item, total_waste_usd FROM ranked
# WHERE rank_category <= 3
# ORDER BY category, rank_category
# ;


# In[12]:


# The command is not a standard IPython magic command. It is designed for use within Fabric notebooks only.
# %%sql
# -- Q9: Rank suppliers by total waste value using RANK(). Show rank, supplier_name, total_waste_usd.

# SELECT 
#     ds.supplier_name as supplier,
#     SUM(fact.waste_value_usd) as total_waste_value,
#     RANK() OVER (ORDER BY SUM(fact.waste_value_usd) DESC) AS supplier_rank
# FROM silver.fact_supply_inventory fact 
# INNER JOIN silver.dim_supplier ds
# ON ds.supplier_id = fact.supplier_id
# GROUP BY ds.supplier_name
# ;

# -- Q10: Calculate cumulative waste value by month using a window function. 
# -- Show procurement_month and running_total_waste.
# -- Step 1 inside CTE: get monthly totals
# -- Step 2 outside CTE: apply SUM() OVER (ORDER BY month)
# WITH monthly AS (
#     SELECT
#         procurement_month,
#         ROUND(SUM(waste_value_usd), 2) AS monthly_waste
#     FROM silver.fact_supply_inventory
#     GROUP BY procurement_month
# )
# SELECT
#     procurement_month,
#     monthly_waste,
#     SUM(monthly_waste) OVER (ORDER BY procurement_month) AS running_total_waste
# FROM monthly;

