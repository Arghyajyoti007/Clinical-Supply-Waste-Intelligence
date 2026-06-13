import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

random.seed(42)
np.random.seed(42)

# --- Config ---
n = 5000  # rows

hospitals = ['City General Hospital', 'North Medical Center',
             'Sunrise Clinic', 'Metro Health Hub', 'Valley Care Hospital']

wards = ['ICU', 'Emergency', 'Oncology', 'Cardiology',
         'Orthopedics', 'Pharmacy Store', 'General Ward']

categories = ['Pharmaceutical', 'Surgical Supply',
              'Diagnostic Kit', 'IV Fluid', 'PPE']

items = {
    'Pharmaceutical': ['Amoxicillin 500mg', 'Metformin 850mg', 'Amlodipine 5mg',
                       'Omeprazole 20mg', 'Paracetamol 500mg', 'Insulin Glargine'],
    'Surgical Supply': ['Surgical Gloves L', 'Suture Kit 3-0', 'Sterile Drape',
                        'Scalpel Blade 22', 'Wound Dressing Pack'],
    'Diagnostic Kit': ['COVID Rapid Test', 'Blood Glucose Strip',
                       'Urine Dipstick', 'Pregnancy Test Kit'],
    'IV Fluid': ['Normal Saline 500ml', 'Dextrose 5% 1L',
                 'Ringer Lactate 1L', 'Mannitol 20%'],
    'PPE': ['N95 Mask', 'Surgical Mask Box',
            'Face Shield', 'Disposable Gown']
}

suppliers = ['MedLine Supplies Co.', 'PharmaDirect Ltd.', 'GlobalMed Imports',
             'CarePlus Distributors', 'NovaMed Solutions']

today = datetime(2025, 6, 1)

rows = []
for i in range(n):
    cat = random.choice(categories)
    item = random.choice(items[cat])
    received = today - timedelta(days=random.randint(10, 400))

    # Shelf life varies by category
    shelf_days = {
        'Pharmaceutical': random.randint(180, 730),
        'Surgical Supply': random.randint(365, 1095),
        'Diagnostic Kit': random.randint(90, 365),
        'IV Fluid': random.randint(180, 540),
        'PPE': random.randint(365, 730)
    }[cat]

    expiry = received + timedelta(days=shelf_days)
    days_until_expiry = (expiry - today).days

    qty_received = random.randint(50, 500)
    # Simulate some wastage — items close to expiry have more leftover
    if days_until_expiry < 0:
        qty_remaining = random.randint(5, 80)  # expired with stock left
    elif days_until_expiry < 30:
        qty_remaining = random.randint(10, int(qty_received * 0.6))
    else:
        qty_remaining = random.randint(0, int(qty_received * 0.3))

    unit_cost = round(random.uniform(2.5, 450.0), 2)
    waste_value = round(qty_remaining * unit_cost, 2) if days_until_expiry < 30 else 0.0

    rows.append({
        'record_id': f'REC{i + 1:05d}',
        'hospital_name': random.choice(hospitals),
        'ward': random.choice(wards),
        'supplier_name': random.choice(suppliers),
        'category': cat,
        'item_name': item,
        'received_date': received.date(),
        'expiry_date': expiry.date(),
        'shelf_life_days': shelf_days,
        'days_until_expiry': days_until_expiry,
        'is_expired': days_until_expiry < 0,
        'qty_received': qty_received,
        'qty_remaining': qty_remaining,
        'unit_cost_usd': unit_cost,
        'waste_value_usd': waste_value,
        'procurement_month': received.strftime('%Y-%m')
    })

df = pd.DataFrame(rows)
df.to_csv('clinical_supply_raw.csv', index=False)
print(f"Dataset created: {df.shape}")
print(df.head())