# Quick Reference Card

## Essential Commands

### Setup
```bash
# Validate setup
python validate_setup.py

# Install Python dependencies
cd analysis && pip install -r requirements.txt

# Install Node dependencies
cd web && npm install
```

### Run Analysis
```bash
# From project root
python analysis/tabular_analysis.py

# Output: web/public/data/results.json
```

### Development
```bash
# Start dev server
cd web && npm run dev
# → http://localhost:3000

# Build for production
cd web && npm run build

# Test production build locally
cd web && npm start
```

### Deployment
```bash
# Deploy to Vercel
cd web && vercel --prod
```

---

## File Locations

| File | Purpose |
|------|---------|
| `data/raw/oasis_longitudinal.csv` | OASIS-2 dataset (download from Kaggle) |
| `analysis/tabular_analysis.py` | Phase 1 analysis script |
| `web/public/data/results.json` | Generated metrics (served to frontend) |
| `web/src/app/page.tsx` | Main dashboard page |
| `web/src/components/` | React components |

---

## Key Metrics (Computed by Analysis Script)

| Metric | Description | Method |
|--------|-------------|--------|
| **AUC (mean ± std)** | Atrophy rate → dementia classification | Stratified 5-fold CV |
| **Accuracy (mean ± std)** | Classification accuracy | Stratified 5-fold CV |
| **Cohen's d** | Effect size (group difference) | Mann-Whitney U test |
| **p-value** | Statistical significance | Mann-Whitney U test |

---

## Phase 1 Checklist

**Setup:**
- [ ] Data downloaded: `data/raw/oasis_longitudinal.csv`
- [ ] Python deps installed: `pip install -r analysis/requirements.txt`
- [ ] Node deps installed: `cd web && npm install`

**Analysis:**
- [ ] Script runs: `python analysis/tabular_analysis.py`
- [ ] Output exists: `web/public/data/results.json`
- [ ] Metrics are non-zero (not placeholder values)

**Local Testing:**
- [ ] Dev server works: `npm run dev` → http://localhost:3000
- [ ] Subject selector populated
- [ ] Metrics display shows AUC ± std
- [ ] Scatter plot renders

**Deployment:**
- [ ] Production build: `npm run build`
- [ ] Deployed to Vercel
- [ ] Live URL works
- [ ] README updated with live URL

---

## Troubleshooting

### Analysis script fails
```bash
# Check data file exists
ls data/raw/oasis_longitudinal.csv

# Check Python version (need 3.9+)
python --version

# Reinstall dependencies
cd analysis
pip install --upgrade -r requirements.txt
```

### Dashboard shows "Failed to load"
```bash
# Check results.json exists
cat web/public/data/results.json | head

# Re-run analysis
python analysis/tabular_analysis.py

# Restart dev server
cd web && npm run dev
```

### Build fails
```bash
# Clear Next.js cache
cd web
rm -rf .next out node_modules package-lock.json
npm install
npm run build
```

---

## Data-Use Requirements

**OASIS-2 terms prohibit:**
- Facial recognition
- Re-identification of subjects
- Redistribution of raw images (tabular data OK)

**Required acknowledgment** (in README/footer):
> Use of OASIS data is subject to data-use terms prohibiting facial recognition or attempts to re-identify subjects.

---

## Architecture Summary

```
┌─────────────────────────────────────────┐
│  OASIS-2 CSV (Kaggle)                   │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  analysis/tabular_analysis.py           │
│  • Compute per-subject atrophy          │
│  • Stratified 5-fold CV                 │
│  • Group statistics                     │
└────────────┬────────────────────────────┘
             │
             ▼ results.json
┌─────────────────────────────────────────┐
│  web/public/data/                       │
│  (Static JSON served to frontend)       │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  Next.js Dashboard                      │
│  • SubjectViewer                        │
│  • CohortSummary (scatter plot)         │
│  • MetricsDisplay (AUC, accuracy)       │
└─────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  Vercel (Static Export)                 │
│  https://your-app.vercel.app            │
└─────────────────────────────────────────┘
```

**Key principle:** Heavy computation (ML, statistics) happens **offline** in Python. Deployed app serves **static precomputed results**. No server-side inference.

---

## What NOT to Do (Guardrails)

❌ Train models (use pretrained only)
❌ Compute Dice scores (no ground truth segmentations)
❌ Hardcode or fabricate metrics
❌ Run segmentation in production (precompute only)
❌ Re-normalize nWBV (already normalized)
❌ Start Phase 2 before Phase 1 deploys
❌ Use single train/test split (use stratified k-fold)
❌ Expand scope beyond 4-day timeline

---

## Contact & Resources

- **Dataset**: https://www.kaggle.com/datasets/nadiatriki/oasis-2-longitudinal-scan-data
- **SynthSeg** (Phase 2): https://github.com/BBillot/SynthSeg
- **Vercel Docs**: https://vercel.com/docs
- **Next.js Docs**: https://nextjs.org/docs

---

**Current Status**: Phase 1 (Tabular Analysis)
**Next**: Deploy to Vercel → confirm working → proceed to Phase 2
