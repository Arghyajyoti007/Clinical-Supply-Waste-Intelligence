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



