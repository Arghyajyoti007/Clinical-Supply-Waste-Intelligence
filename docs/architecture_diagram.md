# 🏗️ Architecture Diagram
## Clinical Supply Chain Waste Intelligence Platform

---

## End-to-End Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     DATA SOURCES                            │
│                                                             │
│   clinical_supply_raw.csv (5,000 rows)                      │
│   Generated via Python (generate_dataset.py)                │
│   5 Hospitals | 7 Wards | 5 Suppliers | 5 Categories        │
└───────────────────────┬─────────────────────────────────────┘
                        │ Upload
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              MICROSOFT FABRIC LAKEHOUSE                     │
│              clinical_supply_lakehouse                      │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  BRONZE LAYER (Raw Storage)                          │   │
│  │  Files/bronze/supply_chain/                          │   │
│  │  └── clinical_supply_raw.csv                         │   │
│  │                                                      │   │
│  │  Purpose : Immutable raw data — audit trail          │   │
│  │  Format  : CSV                                       │   │
│  │  Schema  : None (as-is from source)                  │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │ PySpark Transformation            │
│                         │ nb_silver_transformation          │
│                         ▼                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  SILVER LAYER (Cleaned + Modelled)                   │   │
│  │                                                      │   │
│  │  DIMENSION TABLES          FACT TABLE                │   │
│  │  ├── dim_hospital     ──►  fact_supply_inventory     │   │
│  │  ├── dim_ward         ──►  ├── record_id             │   │
│  │  ├── dim_category     ──►  ├── hospital_id (FK)      │   │
│  │  ├── dim_item         ──►  ├── ward_id (FK)          │   │
│  │  └── dim_supplier     ──►  ├── category_id (FK)      │   │
│  │                            ├── item_id (FK)          │   │
│  │  Purpose : Star Schema     ├── supplier_id (FK)      │   │
│  │  Format  : Delta Lake      ├── waste_value_usd       │   │
│  │  Keys    : Surrogate IDs   ├── days_until_expiry     │   │
│  │                            └── is_expired            │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │ Spark SQL Aggregation             │
│                         │ nb_gold_kpi                       │
│                         ▼                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  GOLD LAYER (Business-Ready KPIs)                    │   │
│  │                                                      │   │
│  │  ├── kpi_waste_summary                               │   │
│  │  │   └── Monthly waste trends & counts              │   │
│  │  │                                                   │   │
│  │  ├── kpi_waste_by_location                           │   │
│  │  │   └── Hospital × Ward waste breakdown            │   │
│  │  │                                                   │   │
│  │  └── kpi_supplier_item                               │   │
│  │      └── Supplier × Item × Category risk            │   │
│  │                                                      │   │
│  │  Purpose : Power BI consumption layer                │   │
│  │  Format  : Delta Lake                                │   │
│  │  Access  : SQL Analytics Endpoint                    │   │
│  └──────────────────────────────────────────────────────┘   │
└───────────────────────┬─────────────────────────────────────┘
                        │
          ┌─────────────┴─────────────┐
          │                           │
          ▼                           ▼
┌─────────────────┐       ┌───────────────────────┐
│  DATA PIPELINE  │       │   POWER BI DESKTOP     │
│                 │       │                        │
│ pl_clinical_    │       │  Connection:           │
│ supply_chain    │       │  DirectQuery via        │
│                 │       │  SQL Analytics Endpoint │
│ Activity 1:     │       │                        │
│ Silver Notebook │       │  Page 1:               │
│       ↓ ✅      │       │  Executive Overview    │
│ Activity 2:     │       │                        │
│ Gold Notebook   │       │  Page 2:               │
│       ↓ ✅      │       │  Location Intelligence │
│                 │       │                        │
│ Schedule:       │       │  Page 3:               │
│ Every Sunday    │       │  Supplier & Item Risk  │
│ 10:00 AM IST    │       │                        │
└─────────────────┘       └───────────────────────┘
```

---

## Star Schema Design

```
                    ┌─────────────────┐
                    │  dim_hospital   │
                    │  hospital_id PK │
                    │  hospital_name  │
                    └────────┬────────┘
                             │
┌─────────────┐    ┌─────────▼──────────────────────┐    ┌──────────────┐
│  dim_ward   │    │    fact_supply_inventory        │    │ dim_supplier │
│  ward_id PK ├───►│    record_id (PK)               │◄───┤ supplier_id  │
│  ward       │    │    hospital_id (FK)             │    │ supplier_name│
└─────────────┘    │    ward_id (FK)                 │    └──────────────┘
                   │    category_id (FK)             │
┌─────────────┐    │    item_id (FK)                 │    ┌──────────────┐
│ dim_category│    │    supplier_id (FK)             │    │   dim_item   │
│ category_id ├───►│    received_date                │◄───┤  item_id PK  │
│ category    │    │    expiry_date                  │    │  item_name   │
└─────────────┘    │    shelf_life_days              │    └──────────────┘
                   │    days_until_expiry            │
                   │    is_expired                   │
                   │    qty_received                 │
                   │    qty_remaining                │
                   │    unit_cost_usd                │
                   │    waste_value_usd              │
                   │    procurement_month            │
                   └─────────────────────────────────┘
```

---

## Medallion Architecture Principles

| Layer  | Purpose | Format | Schema Type |
|--------|---------|--------|-------------|
| Bronze | Raw immutable data — audit trail | CSV | Schema on Read |
| Silver | Cleaned, modelled, Star Schema | Delta Lake | Schema on Write |
| Gold | Aggregated KPIs for BI consumption | Delta Lake | Schema on Write |

---

## Pipeline Execution Flow

```
TRIGGER: Every Sunday 10:00 AM IST
              │
              ▼
   ┌─────────────────────┐
   │  Activity 1         │
   │  nb_silver_         │
   │  transformation     │
   │  Status: ✅ Success  │
   └──────────┬──────────┘
              │ On Success
              ▼
   ┌─────────────────────┐
   │  Activity 2         │
   │  nb_gold_kpi        │
   │  Status: ✅ Success  │
   └──────────┬──────────┘
              │
              ▼
   Power BI auto-refreshes
   via DirectQuery
```

---

## Technology Decisions

| Decision | Choice | Reason |
|---|---|---|
| Storage format | Delta Lake | ACID transactions, time travel, rollback on failure |
| Transformation | ELT not ETL | Transform inside Fabric using distributed Spark compute |
| BI connection | DirectQuery | Always fresh data without manual refresh |
| Key generation | dense_rank() on distinct | Clean surrogate keys without gaps |
| Null handling | Item-level avg cost | Most accurate waste_value_usd calculation |
| Heatmap midpoint | Median not Average | Resistant to outliers in conditional formatting |
