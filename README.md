# OASIS-2 Longitudinal Brain Atrophy Analyzer

A web application that quantifies how brain regions shrink over time in aging and Alzheimer's patients, testing whether **rate of atrophy** separates demented from non-demented subjects.

**Live demo:** https://oasis-brain-atrophy.vercel.app/

---

## What This Does

This application analyzes longitudinal MRI data to:

1. **Compute per-subject atrophy rates**: Annualized percent change in normalized whole-brain volume (nWBV) between first and last scan
2. **Classify dementia status**: Use atrophy rate to predict whether subjects have dementia (CDR > 0)
3. **Compare groups**: Statistical comparison of atrophy rates between demented and non-demented cohorts

**Key finding**: Whole-brain atrophy rate shows weak-to-moderate discrimination (AUC ~0.64), similar to baseline volume alone. Combining features provides minimal improvement, motivating Phase 2's regional analysis.

---

## Dataset

**OASIS-2** (Open Access Series of Imaging Studies) - Longitudinal MRI and Clinical Data in Nondemented and Demented Older Adults

- 150 subjects aged 60-96
- Each scanned 2+ times, variable follow-up (typically 1-5 years)
- 373 total imaging sessions
- Source: [Kaggle OASIS-2 dataset](https://www.kaggle.com/datasets/nadiatriki/oasis-2-longitudinal-scan-data)

**Data use acknowledgment**: OASIS data-use terms prohibit using the images for facial recognition or any attempt to re-identify subjects.

**Important caveats**:
- Follow-up intervals vary considerably between subjects (1-7+ years)
- Dementia label is based on **CDR at last visit** (CDR > 0 = demented)
- "Converted" subjects started non-demented and became demented during follow-up

---

## Method

### Phase 1: Tabular Analysis (Current)

**Features computed per subject:**
- `baseline_nWBV`: Normalized whole-brain volume at first visit (already normalized by ICV)
- `annualized_atrophy_rate`: `(nWBV_last - nWBV_first) / years * 100` where `years = MR_Delay / 365.25`

**Target variable:**
- `CDR > 0` at last visit (1 = demented, 0 = non-demented)
- This naturally handles "Converted" subjects (start non-demented, become demented)

**Classification:**
- Logistic regression trained on atrophy rate → dementia status
- **Stratified 5-fold cross-validation** to ensure stable estimates on small sample
- Metrics: AUC (mean ± std), accuracy (mean ± std)

**Group comparison:**
- Mann-Whitney U test comparing atrophy rates between demented vs. non-demented
- Effect size: Cohen's d

**Important context:**
Baseline brain volume is itself discriminative (demented subjects have lower volumes even before longitudinal decline). However, atrophy rate provides similar discrimination (AUC ~0.64), and combining both features yields minimal improvement (+0.01 AUC). This suggests whole-brain volume lacks sensitivity to the regional patterns characteristic of Alzheimer's disease.

### Phase 2: Regional MTL Cortex Analysis (Complete)

**Hypothesis**: Since whole-brain atrophy shows only weak discrimination (AUC 0.64), regional atrophy in medial-temporal lobe cortex - where Alzheimer's pathology concentrates earliest - may separate groups better.

**Method**:
- ANTsPyNet DeepFLASH parcellation on 42-subject pilot cohort
- 14 regions analyzed: entorhinal subdivisions (aLEC/pMEC), perirhinal, parahippocampal, hippocampal subfields (DG/CA3, CA1, subiculum)
- Per-region stratified 5-fold CV logistic regression AUC
- Mann-Whitney U test for group separation
- Bonferroni correction for multiple comparisons (14 tests, threshold p < 0.0036)

**Key findings**:
- **Top region**: Left parahippocampal (AUC 0.74 +/- 0.21, p = 0.0031) - **survives Bonferroni**
- **5 regions reach p < 0.05**: parahippocampal L, subiculum R, entorhinal pMEC R, perirhinal R, entorhinal aLEC R
- **Matched whole-brain baseline**: AUC 0.76 +/- 0.04 (same 42 subjects, same labels)
- **Top region does NOT outperform whole-brain** on controlled comparison (-0.02 AUC)
- Combined 14-region model (AUC 0.54) overfits due to n=42 with 14 features

**Interpretation**: While the hypothesis that regional MTL atrophy would outperform whole-brain was not confirmed on this pilot cohort, the regional analysis successfully recovers known early-AD sites (parahippocampal, entorhinal, perirhinal rank highest). The top region shows statistically significant group separation (p = 0.0031, survives Bonferroni). Larger cohorts may show different relative performance.

**Caveats**:
- n=42 pilot cohort (subset of OASIS-2 with usable longitudinal scans)
- Dementia label uses **baseline (first-visit) CDR** (same labels used for matched whole-brain comparison)
- All 14 MTL subregions analyzed; cortical regions (parahippocampal, entorhinal, perirhinal) discriminate well, hippocampal subfields (DG/CA3, CA1, subiculum) rank lower (T1 resolution limits subfield delineation)
- Combined multi-region model not reliable at this sample size

**Note**: Segmentation was computed in Google Colab. The deployed app serves cached results.

---

## Setup & Usage

### Prerequisites

- Python 3.9+
- Node.js 18+

### 1. Get the Data

Download the OASIS-2 longitudinal CSV from [Kaggle](https://www.kaggle.com/datasets/nadiatriki/oasis-2-longitudinal-scan-data) and place it in:

```
data/raw/oasis_longitudinal.csv
```

### 2. Run Analysis

```bash
# Install Python dependencies
cd analysis
pip install -r requirements.txt

# Run tabular analysis (outputs to web/public/data/results.json)
python tabular_analysis.py
```

Expected output:
```
OASIS-2 TABULAR ANALYSIS - PHASE 1
============================================================
Loaded 373 sessions from 150 subjects
Subjects with ≥2 visits: [computed]
...
AUC: [mean] ± [std]
✓ Results exported to: web/public/data/results.json
```

### 3. Run Frontend

```bash
# Install Node dependencies
cd web
npm install

# Development server
npm run dev
# Open http://localhost:3000

# Production build
npm run build
npm start
```

---

## Deployment

### Frontend (Vercel)

```bash
cd web
npm run build
# Deploy the 'out' directory to Vercel
```

### Data Pipeline

The analysis script must be run **before** deploying the frontend to generate `web/public/data/results.json`. This ensures all metrics are precomputed and the deployed app serves static data only.

---

## Metrics (Computed from Real Data)

All values are computed at runtime from the actual OASIS-2 data. **No fabricated or hardcoded metrics.**

### Phase 1: Whole-Brain (n=150)

| Metric | Value | Method |
|--------|-------|--------|
| **Atrophy Rate AUC** | 0.642 +/- 0.037 | Stratified 5-fold CV |
| **Baseline nWBV AUC** | 0.640 +/- 0.110 | Stratified 5-fold CV |
| **Combined Model AUC** | 0.654 +/- 0.039 | Stratified 5-fold CV |
| **Cohen's d** | -0.52 | Effect size (moderate) |
| **p-value** | 0.0035 | Mann-Whitney U test |

**Interpretation**: Both single features show weak-to-moderate discrimination. The combined model adds only +0.01 AUC, confirming that whole-brain measures miss the regional specificity needed for robust classification.

### Phase 2: Regional MTL (n=42 pilot)

| Metric | Value | Method |
|--------|-------|--------|
| **Top Region AUC** | 0.74 +/- 0.21 | parahippocampal L, 5-fold CV |
| **Top Region p-value** | 0.0031 | Survives Bonferroni (14 tests) |
| **Matched Whole-Brain AUC** | 0.76 +/- 0.04 | Same 42 subjects, same labels |
| **Regions at p < 0.05** | 5 of 14 | Mann-Whitney U |
| **vs. Matched Whole-Brain** | -0.02 | Controlled comparison |

**Interpretation**: On controlled comparison (same subjects, same labels), the top regional AUC (0.74) does not exceed whole-brain (0.76). However, the regional analysis recovers known early-AD sites (parahippocampal, entorhinal, perirhinal rank highest), and the top region shows significant group separation (p = 0.0031, survives Bonferroni). Combined multi-region model overfits at n=42.

---

## Limitations & Honesty

1. **Small sample size**: ~150 subjects with longitudinal data. Results are stable due to cross-validation, but larger cohorts would strengthen conclusions.

2. **Variable follow-up**: Follow-up intervals range from 1 to 7+ years. Atrophy rate estimates are noisier for shorter intervals.

3. **No segmentation ground truth**: OASIS-2 does not include manual region segmentations. Phase 2 uses SynthSeg (automated), so we cannot compute Dice scores. Evaluation is based on group separation, not segmentation accuracy.

4. **Weak whole-brain discrimination**: AUC ~0.64 indicates substantial overlap between groups. This is expected - whole-brain volume is a coarse measure that doesn't capture the regional patterns (hippocampal, cortical) characteristic of Alzheimer's.

5. **Volumetric atrophy only**: This analysis measures region volumes, not voxel-wise atrophy patterns or spatial distribution of change.

6. **Offline segmentation**: SynthSeg is CPU-based (~2 min/scan) and runs in a precomputation pipeline, not live in the deployed app.

---

## Project Structure

```
/
├── data/
│   ├── raw/                    # OASIS-2 CSV (user-provided)
│   └── processed/              # Phase 2: regional_atrophy.csv from Colab
├── analysis/
│   ├── tabular_analysis.py     # Phase 1 whole-brain analysis
│   ├── regional_analysis.py    # Phase 2 regional MTL analysis
│   └── requirements.txt
├── web/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx        # Main dashboard
│   │   │   └── layout.tsx
│   │   ├── components/
│   │   │   ├── SubjectViewer.tsx
│   │   │   ├── CohortSummary.tsx
│   │   │   ├── MetricsDisplay.tsx
│   │   │   └── RegionalResults.tsx  # Phase 2 component
│   │   └── types/
│   ├── public/
│   │   └── data/
│   │       ├── results.json          # Phase 1 output
│   │       └── regional_results.json # Phase 2 output
│   └── package.json
└── README.md
```

---

## Tech Stack

- **Frontend**: Next.js 14 + TypeScript + Recharts
- **Analysis**: Python (pandas, NumPy, scikit-learn, scipy)
- **Segmentation** (Phase 2): SynthSeg (standalone, CPU-based)
- **Deployment**: Vercel (frontend), static data serving

---

## License & Attribution

This is a portfolio/application project for demonstrating competence in medical imaging and longitudinal analysis.

**Dataset**: OASIS-2 Longitudinal MRI dataset. Use of OASIS data is subject to data-use terms prohibiting facial recognition or re-identification.

---

## Roadmap

- [x] Phase 1: Tabular analysis with nWBV
- [x] Phase 1: Stratified cross-validation
- [x] Phase 1: Dashboard deployment
- [x] Phase 2: DeepFLASH MTL cortex segmentation (Colab)
- [x] Phase 2: Per-region atrophy metrics with Bonferroni correction
- [x] Phase 2: Dashboard integration with regional results
- [ ] Future: Larger cohort validation
- [ ] Future: Brain viewer (NiiVue or PNG slices)

---

**Status**: Phase 1 and Phase 2 complete. Regional analysis shows left parahippocampal (AUC 0.74, p=0.003) recovers known early-AD sites; matched whole-brain comparison (AUC 0.76) on n=42 pilot.
