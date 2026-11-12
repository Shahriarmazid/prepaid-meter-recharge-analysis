"""
generate_data.py

Creates a SYNTHETIC dataset of prepaid electricity meter recharges.
No real customer data is used - the numbers are simulated so the
analysis can be shared publicly on GitHub.

The data is made a bit "messy" on purpose (duplicates, missing values,
inconsistent text, mixed date formats, some bad values) so that the
notebook has something real to clean.

Run:  python src/generate_data.py
"""

import numpy as np
import pandas as pd
from pathlib import Path

np.random.seed(42)

N_CUSTOMERS = 600
START = pd.Timestamp("2025-01-01")
END = pd.Timestamp("2025-12-31")

districts = {
    "Dhaka": ("DESCO", "Urban"),
    "Gazipur": ("DESCO", "Urban"),
    "Narayanganj": ("DPDC", "Urban"),
    "Rajshahi": ("NESCO", "Urban"),
    "Rangpur": ("NESCO", "Rural"),
    "Khulna": ("WZPDCL", "Urban"),
    "Jessore": ("WZPDCL", "Rural"),
    "Mymensingh": ("BREB", "Rural"),
    "Comilla": ("BREB", "Rural"),
    "Sylhet": ("BPDB", "Urban"),
}

channels = ["bKash", "Nagad", "Vending Point", "Bank Card", "Rocket"]
channel_p = [0.42, 0.22, 0.20, 0.06, 0.10]

# monthly seasonality - summer months use more power (AC / fans)
season = {1: 0.80, 2: 0.85, 3: 1.00, 4: 1.20, 5: 1.30, 6: 1.25,
          7: 1.15, 8: 1.15, 9: 1.10, 10: 1.00, 11: 0.85, 12: 0.80}

# ---- customers ----
cust_ids = [f"C{str(i).zfill(4)}" for i in range(1, N_CUSTOMERS + 1)]
cust = pd.DataFrame({
    "customer_id": cust_ids,
    "district": np.random.choice(list(districts.keys()), N_CUSTOMERS,
                                 p=[0.22, 0.10, 0.08, 0.08, 0.08, 0.10, 0.07, 0.10, 0.09, 0.08]),
    "tariff": np.random.choice(["Residential", "Commercial"], N_CUSTOMERS, p=[0.82, 0.18]),
})
cust["utility"] = cust["district"].map(lambda d: districts[d][0])
cust["area_type"] = cust["district"].map(lambda d: districts[d][1])

# base spending level per customer
base = np.random.lognormal(mean=6.6, sigma=0.35, size=N_CUSTOMERS)
base = np.where(cust["tariff"] == "Commercial", base * 2.2, base)
base = np.where(cust["area_type"] == "Rural", base * 0.75, base)
cust["base_amount"] = base
cust["fav_channel"] = np.random.choice(channels, N_CUSTOMERS, p=channel_p)

# ---- transactions ----
rows = []
tx = 1
for _, c in cust.iterrows():
    # number of recharges per month (2-5)
    freq = np.random.randint(2, 6)
    for month in range(1, 13):
        n = np.random.poisson(freq)
        for _ in range(max(n, 1)):
            day = np.random.randint(1, 29)
            date = pd.Timestamp(2025, month, day)
            amt = c["base_amount"] / freq * season[month] * np.random.normal(1, 0.18)
            amt = round(max(amt, 50) / 10) * 10  # recharges are usually round numbers
            ch = c["fav_channel"] if np.random.rand() < 0.7 else np.random.choice(channels, p=channel_p)
            rows.append([f"TXN{str(tx).zfill(6)}", c["customer_id"], date, c["district"],
                         c["utility"], c["area_type"], c["tariff"], ch, amt])
            tx += 1

df = pd.DataFrame(rows, columns=["transaction_id", "customer_id", "recharge_date", "district",
                                 "utility", "area_type", "tariff", "payment_channel",
                                 "recharge_amount_bdt"])

# approx units (kWh) after VAT + demand charge, roughly BDT 8 per unit
df["units_kwh"] = (df["recharge_amount_bdt"] * 0.95 / np.random.normal(8.2, 0.4, len(df))).round(1)

# ---- add some unusual recharges (possible tampering / data entry errors) ----
idx = np.random.choice(df.index, 45, replace=False)
df.loc[idx, "recharge_amount_bdt"] = df.loc[idx, "recharge_amount_bdt"] * np.random.randint(6, 15, 45)

# ---- make the data messy ----
df["recharge_date"] = df["recharge_date"].dt.strftime("%Y-%m-%d")
mix = np.random.choice(df.index, 300, replace=False)
df.loc[mix, "recharge_date"] = pd.to_datetime(df.loc[mix, "recharge_date"]).dt.strftime("%d/%m/%Y")

for col, n in [("recharge_amount_bdt", 70), ("payment_channel", 110), ("units_kwh", 90)]:
    df.loc[np.random.choice(df.index, n, replace=False), col] = np.nan

d_idx = np.random.choice(df.index, 400, replace=False)
df.loc[d_idx, "district"] = df.loc[d_idx, "district"].apply(
    lambda x: np.random.choice([x.upper(), x.lower(), x + " ", " " + x]))
df.loc[df["district"].str.strip().str.lower() == "comilla", "district"] = np.random.choice(
    ["Comilla", "Cumilla"], (df["district"].str.strip().str.lower() == "comilla").sum())

df.loc[np.random.choice(df.index, 12, replace=False), "recharge_amount_bdt"] *= -1  # refunds / errors
df.loc[np.random.choice(df.index, 8, replace=False), "recharge_amount_bdt"] = 0

df = pd.concat([df, df.sample(85, random_state=1)])  # duplicate rows
df = df.sample(frac=1, random_state=7).reset_index(drop=True)

out = Path(__file__).resolve().parents[1] / "data" / "raw" / "meter_recharges_raw.csv"
df.to_csv(out, index=False)
print(f"Saved {len(df):,} rows -> {out}")
