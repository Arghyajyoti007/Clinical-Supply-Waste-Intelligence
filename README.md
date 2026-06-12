# 🏥 Clinical Supply Chain Waste Intelligence Platform
### Med-Core Health Network | Microsoft Fabric + Power BI

![Platform](https://img.shields.io/badge/Platform-Microsoft%20Fabric-0A2342?style=for-the-badge)
![Language](https://img.shields.io/badge/Language-PySpark%20%7C%20SQL-1B6CA8?style=for-the-badge)
![Visualization](https://img.shields.io/badge/Visualization-Power%20BI-F39C12?style=for-the-badge)
![Architecture](https://img.shields.io/badge/Architecture-Medallion%20%28Bronze%2FSilver%2FGold%29-00C4B4?style=for-the-badge)

---

## 📌 Business Problem

A mid-size hospital network (**Med-Core Health Network**) was losing an estimated **$10.8M annually** due to pharmaceutical and medical supply waste — expired medications, overstocked wards, and poor demand forecasting across 5 hospitals and 7 ward types.

**This project delivers a data-driven waste reduction platform** to help the CFO, Supply Chain Director, and Procurement Head make faster, more informed decisions.

---

## 🎯 Business Goals

| Goal | Metric |
|---|---|
| Identify total financial waste | Total Waste Value (USD) |
| Pinpoint highest-risk locations | Hospital × Ward heatmap |
| Hold suppliers accountable | Supplier Waste Index |
| Flag items before expiry | Critical Zone Item Count (0–10 days) |
| Track waste reduction over time | Monthly trend analysis |

---

## 🏗️ Solution Architecture

```
Raw CSV Data
     ↓
┌─────────────────────────────────────┐
│         Microsoft Fabric            │
│                                     │
│  BRONZE LAYER                       │
│  └── Files/bronze/supply_chain/     │
│      clinical_supply_raw.csv        │
│                ↓                    │
│  SILVER LAYER (PySpark + SQL)       │
│  ├── silver.dim_hospital            │
│  ├── silver.dim_ward                │
│  ├── silver.dim_category            │
│  ├── silver.dim_item                │
│  ├── silver.dim_supplier            │
│  └── silver.fact_supply_inventory   │
│                ↓                    │
│  GOLD LAYER (Spark SQL)             │
│  ├── gold.kpi_waste_summary         │
│  ├── gold.kpi_waste_by_location     │
│  └── gold.kpi_supplier_item         │
│                ↓                    │
│  DATA PIPELINE                      │
│  pl_clinical_supply_chain           │
│  ├── Activity 1: Silver Notebook    │
│  └── Activity 2: Gold Notebook      │
│  Schedule: Every Sunday 10AM        │
└─────────────────────────────────────┘
     ↓
Power BI Executive Dashboard
├── Page 1: Executive Overview
├── Page 2: Location Intelligence
└── Page 3: Supplier & Item Risk
```

---

## 🛠️ Tech Stack

| Tool | Usage |
|---|---|
| **Microsoft Fabric Lakehouse** | Medallion Architecture storage |
| **PySpark (Fabric Notebook)** | Bronze → Silver transformation |
| **Spark SQL** | Silver → Gold KPI aggregation |
| **Fabric Data Pipeline** | ELT orchestration & scheduling |
| **Delta Lake** | ACID transactions, time travel |
| **Power BI Desktop** | Executive dashboard (DirectQuery) |
| **Python (local)** | Synthetic dataset generation |

---

## 📊 Dashboard Pages

### Page 1 — Executive Overview
- Total Waste Value: **$10.80M**
- Expired Stock Value: **$7.75M**
- Critical Zone Items: **59** (expiring in 0–10 days)
- Monthly waste trend (declining 85% since Aug 2024)
- Waste vs Inventory comparison
- Inventory Risk Distribution donut

### Page 2 — Location Intelligence
- Top Waste Hospital: **Valley Care Hospital ($2.5M)**
- Highest Risk Ward: **Pharmacy Store**
- Hospital × Ward waste heatmap with conditional formatting
- 170 at-risk items across network

### Page 3 — Supplier & Item Risk
- Highest Risk Supplier: **MedLine Supplies Co.**
- Top waste category: **Diagnostic Kit (55.29%)**
- 59 items in critical expiry zone
- Supplier × Category risk matrix

---

## 📁 Repository Structure

```
clinical-supply-waste-intelligence/
│
├── data/
│   └── generate_dataset.py          # Synthetic dataset generator (5000 rows)
│
├── notebooks/
│   ├── nb_silver_transformation/    # PySpark Bronze → Silver
│   └── nb_gold_kpi/                 # Spark SQL Silver → Gold
│
├── sql/
│   ├── create_schemas.sql           # Schema creation scripts
│   ├── gold_kpi_tables.sql          # Gold layer KPI queries
│   └── analytics_queries.sql        # SQL practice queries (Q1–Q10)
│
├── powerbi/
│   └── Health_Clinic_Waste_Management_Dashboard.pdf
│
├── docs/
│   └── architecture_diagram.md
│
└── README.md
```

---

## 🔑 Key Technical Decisions

**Why Medallion Architecture?**
Separates raw, cleaned, and aggregated data into distinct layers — enabling data reprocessing at any layer without affecting downstream consumers.

**Why Delta Lake over Parquet?**
Delta provides ACID transactions and automatic rollback on pipeline failure — Gold tables are always protected from corrupt Silver writes.

**Why DirectQuery in Power BI?**
Ensures dashboard always reflects latest pipeline run without manual refresh — critical for operational healthcare reporting.

**Why ELT over ETL?**
Microsoft Fabric processes transformations inside the platform using distributed Spark compute — more scalable than pre-loading transforms.

---

## 📈 Business Impact

| Finding | Action | Estimated Saving |
|---|---|---|
| Valley Care Pharmacy Store: $4.88M waste | Weekly expiry audits + FIFO protocol | $1.5–2M annually |
| Diagnostic Kits: 55% of total waste | Reduce order quantity, shorter contracts | $3M annually |
| 59 items expiring in <10 days | Immediate redistribution to high-use wards | $200K–500K |
| Waste declined 85% since Aug 2024 | Pipeline monitoring enabled early intervention | Ongoing |

---

## 🚀 How to Run

1. Clone this repository
2. Run `data/generate_dataset.py` to create `clinical_supply_raw.csv`
3. Upload CSV to Fabric Lakehouse: `Files/bronze/supply_chain/`
4. Run `nb_silver_transformation` notebook
5. Run `nb_gold_kpi` notebook
6. Connect Power BI Desktop via SQL endpoint (DirectQuery)
7. Open dashboard

---

## 👤 Author

**Arghyajyoti Samui**
Analyst @ HCLTech | Microsoft Azure AI Engineer Associate
Transitioning → Data Analytics & Analytics Engineering

🔗 [LinkedIn](https://linkedin.com/in/arghyajyoti-samui)
🐙 [GitHub](https://github.com/Arghyajyoti007)

---

> ⭐ If you found this project useful, consider giving it a star!
