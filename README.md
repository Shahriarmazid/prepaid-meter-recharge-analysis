# Prepaid Electricity Meter Recharge Analysis

My first data analysis project in Python. I work at a prepaid smart meter company in Bangladesh, so I practised on the kind of data I see at work: customers recharging their prepaid electricity meters.

> **The data is synthetic.** It was made with `src/generate_data.py` to look like real recharge records. It has no real customer information.

## Questions
1. How does recharge spending change through the year?
2. Which payment channels do customers use most?
3. Do urban customers spend more than rural customers?
4. Are there any unusual recharges that should be checked?

## Tools
- **pandas** for loading and cleaning the data
- **matplotlib / seaborn** for charts
- **SciPy** for a t-test
- **Excel** (through pandas + openpyxl) for the summary report

## Folders
```
prepaid-meter-recharge-analysis/
├── data/
│   ├── raw/meter_recharges_raw.csv          # messy data
│   └── processed/meter_recharges_clean.csv  # cleaned data
├── notebooks/
│   └── recharge_analysis.ipynb              # the analysis
├── outputs/
│   ├── figures/                             # charts
│   └── recharge_analysis_summary.xlsx       # Excel summary
├── src/
│   └── generate_data.py                     # makes the dataset
└── requirements.txt
```

## Data cleaning
| Problem | What I did |
|---|---|
| 85 duplicate rows | Removed with `drop_duplicates()` |
| Two date formats (`2025-03-14` and `14/03/2025`) | Converted each format and combined them |
| Messy district names (extra spaces, upper/lower case, Cumilla vs Comilla) | `str.strip()`, `str.title()` and `replace()` |
| Missing, zero or negative amounts | Removed |
| Missing payment channel | Filled with "Unknown" |
| Missing units | Removed (small number of rows) |

## Results

**1. Recharges are seasonal.** Highest in May and lowest in December-January, probably because of fans and ACs in summer.

![Monthly trend](outputs/figures/01_monthly_trend.png)

**2. Mobile wallets are the main channel.** bKash (41%) and Nagad (23%) make up nearly two-thirds of recharges.

![Payment channels](outputs/figures/02_payment_channels.png)

**3. Urban customers spend more.** Urban residential customers spend about BDT 847 per month, and rural ones spend about BDT 672. The t-test gives p < 0.05, so the difference is significant.

![Urban vs rural](outputs/figures/04_urban_vs_rural.png)

**4. 45 unusual recharges.** I flagged recharges where the price per kWh is more than 50% away from the median. In these cases customers paid a lot but received few units, so they should be checked.

![Flagged recharges](outputs/figures/05_flagged_recharges.png)

## How to run
```bash
git clone https://github.com/Shahriarmazid/prepaid-meter-recharge-analysis.git
cd prepaid-meter-recharge-analysis
pip install -r requirements.txt
jupyter notebook notebooks/recharge_analysis.ipynb
```

## Next steps
- Predict next month's recharge demand with a regression model
- Try a better way of finding unusual recharges
- Use real data if possible
