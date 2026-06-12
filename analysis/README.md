# Analysis Scripts

## Phase 1: Tabular Analysis

### Input
- `data/raw/oasis_longitudinal.csv` - OASIS-2 tabular data from Kaggle

### Output
- `web/public/data/results.json` - Precomputed metrics for dashboard

### Running

```bash
# Install dependencies
pip install -r requirements.txt

# Run analysis
python tabular_analysis.py
```

### What It Computes

**Per-subject features** (one row per subject with ≥2 visits):
- `baseline_nWBV`: nWBV at first visit
- `annualized_atrophy_rate`: (nWBV_last - nWBV_first) / years × 100
  - `years = MR_Delay / 365.25` (MR Delay is in days)
- `target`: CDR > 0 at last visit (1=demented, 0=non-demented)

**Classification metrics**:
- Logistic regression: atrophy rate → dementia status
- Stratified 5-fold CV → mean AUC ± std, mean accuracy ± std
- Baseline nWBV → dementia status (for context)

**Group comparison**:
- Demented vs. non-demented atrophy rates
- Mann-Whitney U test, Cohen's d effect size

### Expected Output

```
OASIS-2 TABULAR ANALYSIS - PHASE 1
============================================================
Loaded 373 sessions from 150 subjects
Columns: ['Subject ID', 'MRI ID', 'Group', 'Visit', 'MR Delay', ...]

Computing per-subject longitudinal features...
Subjects with ≥2 visits: 146
Target distribution: {0: 108, 1: 38}
Group distribution: {'Nondemented': 108, 'Demented': 34, 'Converted': 4}

============================================================
CLASSIFICATION: Atrophy Rate → Dementia Status
============================================================
Feature: Annualized nWBV atrophy rate (% per year)
AUC: 0.XXX ± 0.XXX
Accuracy: 0.XXX ± 0.XXX
Method: Stratified 5-fold CV

============================================================
BASELINE COMPARISON: Baseline nWBV → Dementia Status
============================================================
Feature: Baseline nWBV (at first visit)
AUC: 0.XXX ± 0.XXX
Accuracy: 0.XXX ± 0.XXX

NOTE: Baseline volume is discriminative because demented subjects
      have lower brain volumes even before longitudinal decline.

============================================================
GROUP COMPARISON: Atrophy Rate by Dementia Status
============================================================
Demented (n=38): -X.XXX ± X.XXX % per year
Non-demented (n=108): -X.XXX ± X.XXX % per year
Cohen's d: X.XXX
p-value: 0.XXXX (Mann-Whitney U)

============================================================
✓ Results exported to: web/public/data/results.json
============================================================
```

### Key Corrections Applied

1. **Stratified 5-fold CV** (not single split) for stable AUC estimates
2. **Years from MR Delay**: `years = MR_Delay / 365.25` (days → years)
3. **No re-normalization**: nWBV is already normalized, use as-is
4. **Target = CDR > 0**: Handles "Converted" subjects naturally
5. **One row per subject**: No session-level leakage across folds
6. **Explicit NaN handling**: SES and MMSE can be missing

---

## Phase 2: Segmentation (To Be Added)

Will run SynthSeg on subset of scans and compute per-region atrophy.
