# Quick Setup Guide

## Prerequisites

- Python 3.9+ with pip
- Node.js 18+ with npm
- Kaggle account (for data download)

---

## Step 1: Download Data

### Option A: Kaggle CLI (Recommended)

```bash
# Install Kaggle CLI
pip install kaggle

# Configure API key (get from kaggle.com/account)
# Place kaggle.json in ~/.kaggle/ (Linux/Mac) or C:\Users\<user>\.kaggle\ (Windows)

# Download dataset
kaggle datasets download -d nadiatriki/oasis-2-longitudinal-scan-data

# Extract
unzip oasis-2-longitudinal-scan-data.zip -d data/raw/

# Rename file (verify actual filename after extraction)
mv data/raw/oasis_longitudinal_demographics.csv data/raw/oasis_longitudinal.csv
```

### Option B: Manual Download

1. Go to https://www.kaggle.com/datasets/nadiatriki/oasis-2-longitudinal-scan-data
2. Click "Download" (requires Kaggle account)
3. Extract the CSV file
4. Place it in `data/raw/oasis_longitudinal.csv`

**Important**: Verify the CSV has these columns:
- `Subject ID`
- `MR Delay`
- `nWBV`
- `CDR`
- `Group`
- `Visit`

---

## Step 2: Run Analysis

```bash
# Install Python dependencies
cd analysis
pip install -r requirements.txt

# Run tabular analysis
python tabular_analysis.py
```

**Expected runtime**: ~10 seconds

**Output**: `web/public/data/results.json` with computed metrics

---

## Step 3: Run Dashboard

```bash
# Install Node dependencies
cd web
npm install

# Start development server
npm run dev
```

**Open**: http://localhost:3000

You should see:
- Subject selector with individual trajectories
- Cohort scatter plot (baseline vs. atrophy rate)
- Computed metrics panel (AUC, accuracy, group comparison)

---

## Step 4: Deploy (Optional)

### Deploy to Vercel

```bash
cd web

# Build static export
npm run build

# Deploy (requires Vercel CLI: npm i -g vercel)
vercel --prod
```

The `out/` directory contains the static site with embedded `data/results.json`.

**Critical**: Always run `python analysis/tabular_analysis.py` before `npm run build` to ensure metrics are current.

---

## Troubleshooting

### "Data file not found"
- Verify `data/raw/oasis_longitudinal.csv` exists
- Check file path matches (case-sensitive on Linux/Mac)

### "Insufficient subjects for analysis"
- CSV might be corrupted or wrong file
- Expected ~373 rows (sessions), 150 unique subjects

### "Module not found" (Python)
```bash
cd analysis
pip install -r requirements.txt
```

### "Module not found" (Node)
```bash
cd web
rm -rf node_modules package-lock.json
npm install
```

### Analysis runs but dashboard shows "Failed to load"
- Check `web/public/data/results.json` exists
- Verify JSON is valid: `cat web/public/data/results.json | head`

---

## Phase 1 Checkpoint

Before proceeding to Phase 2, confirm:

- [ ] Analysis script runs without errors
- [ ] `results.json` contains real computed metrics (not null/NaN)
- [ ] Dashboard loads at http://localhost:3000
- [ ] Subject selector works
- [ ] Metrics panel shows AUC, accuracy with mean ± std
- [ ] Scatter plot displays demented vs. non-demented separation
- [ ] Deployed to live URL (Vercel)

**Only proceed to Phase 2 after Phase 1 is fully working and deployed.**

---

## Next: Phase 2 (Segmentation)

See [analysis/README.md](analysis/README.md) for segmentation pipeline setup.
