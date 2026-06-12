"""
OASIS-2 Regional Atrophy Analysis - Phase 2
Analyzes per-region brain atrophy rates from SynthSeg segmentation.
NO fabricated values - all metrics computed from real data.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
from scipy.stats import mannwhitneyu
import warnings
warnings.filterwarnings('ignore')


# ANTsPyNet DeepFLASH parcellation label mapping
# Labels 5-18: MTL subregions (entorhinal subdivisions + hippocampal subfields)
# These are the earliest Alzheimer's atrophy sites
REGION_LABELS = {
    # Entorhinal subdivisions
    5: 'entorhinal_aLEC_L',      # L entorhinal (anterolateral EC)
    6: 'entorhinal_aLEC_R',      # R entorhinal (anterolateral EC)
    7: 'entorhinal_pMEC_L',      # L entorhinal (posteromedial EC)
    8: 'entorhinal_pMEC_R',      # R entorhinal (posteromedial EC)
    # Perirhinal and parahippocampal cortex
    9: 'perirhinal_L',           # L perirhinal
    10: 'perirhinal_R',          # R perirhinal
    11: 'parahippocampal_L',     # L parahippocampal
    12: 'parahippocampal_R',     # R parahippocampal
    # Hippocampal subfields
    13: 'DG_CA3_L',              # L DG/CA3
    14: 'DG_CA3_R',              # R DG/CA3
    15: 'CA1_L',                 # L CA1
    16: 'CA1_R',                 # R CA1
    17: 'subiculum_L',           # L subiculum
    18: 'subiculum_R',           # R subiculum
}

# MTL cortex labels for combined model (all DeepFLASH MTL regions)
MEDIAL_TEMPORAL_LABELS = list(range(5, 19))  # labels 5-18

# Phase 1 baseline for reference (full 150-subject cohort, last-visit CDR)
PHASE1_FULL_COHORT_AUC = 0.640


def load_regional_data(csv_path):
    """Load regional atrophy data from SynthSeg output."""
    df = pd.read_csv(csv_path)

    required_cols = ['Subject ID', 'CDR', 'demented']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Find all label_* columns
    label_cols = [col for col in df.columns if col.startswith('label_')]
    if not label_cols:
        raise ValueError("No label_* columns found in regional data")

    print(f"Loaded {len(df)} subjects with {len(label_cols)} region columns")
    return df, label_cols


def get_region_name(label_col):
    """Map label column to human-readable region name."""
    # Extract numeric label from column name (e.g., 'label_1006' -> 1006)
    try:
        label_num = int(label_col.replace('label_', ''))
        return REGION_LABELS.get(label_num, f'region_{label_num}')
    except ValueError:
        return label_col


def is_medial_temporal(label_col):
    """Check if a label column is a medial-temporal ROI."""
    try:
        label_num = int(label_col.replace('label_', ''))
        return label_num in MEDIAL_TEMPORAL_LABELS
    except ValueError:
        return False


def compute_region_cv_auc(X, y):
    """
    Stratified 5-fold cross-validation for a single region.
    Returns mean AUC and std.
    Uses random_state=0 to match validated Colab run.
    """
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
    aucs = []

    for train_idx, test_idx in skf.split(X, y):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        clf = LogisticRegression(random_state=0, max_iter=1000)
        clf.fit(X_train, y_train)

        y_pred_proba = clf.predict_proba(X_test)[:, 1]
        aucs.append(roc_auc_score(y_test, y_pred_proba))

    return float(np.mean(aucs)), float(np.std(aucs))


def compute_mann_whitney_p(values, labels):
    """Mann-Whitney U test between demented and non-demented groups."""
    demented = values[labels == 1]
    non_demented = values[labels == 0]

    # Two-sided test (matches Colab validation)
    _, p_value = mannwhitneyu(demented, non_demented, alternative='two-sided')
    return float(p_value)


def analyze_single_region(df, label_col):
    """
    Analyze a single region.
    Returns dict with AUC, p-value, etc. or None if insufficient data.
    """
    # Get non-null values for this region
    mask = df[label_col].notna()
    n_valid = mask.sum()

    if n_valid < 20:
        return None

    X = df.loc[mask, label_col].values.reshape(-1, 1)
    y = df.loc[mask, 'demented'].values

    # Check we have both classes
    if len(np.unique(y)) < 2:
        return None

    # Compute CV AUC
    auc_mean, auc_std = compute_region_cv_auc(X, y)

    # Compute p-value
    p_value = compute_mann_whitney_p(X.flatten(), y)

    # Extract label number
    try:
        label_num = int(label_col.replace('label_', ''))
    except ValueError:
        label_num = None

    return {
        'label': label_col,
        'label_num': label_num,
        'name': get_region_name(label_col),
        'auc_mean': auc_mean,
        'auc_std': auc_std,
        'p_value': p_value,
        'n_subjects': int(n_valid),
        'is_medial_temporal': is_medial_temporal(label_col)
    }


def analyze_combined_medial_temporal(df, label_cols):
    """
    Build a combined model using all medial-temporal regions.
    Returns AUC mean/std or None if insufficient data.
    """
    # Filter to medial-temporal columns that exist in the data
    mt_cols = [col for col in label_cols if is_medial_temporal(col)]

    if not mt_cols:
        print("No medial-temporal region columns found in data")
        return None

    # Get rows with all medial-temporal regions non-null
    mask = df[mt_cols].notna().all(axis=1)
    n_valid = mask.sum()

    if n_valid < 20:
        print(f"Insufficient subjects with all MT regions: {n_valid}")
        return None

    X = df.loc[mask, mt_cols].values
    y = df.loc[mask, 'demented'].values

    # Check we have both classes
    if len(np.unique(y)) < 2:
        return None

    # Compute CV AUC for combined model
    auc_mean, auc_std = compute_region_cv_auc(X, y)

    return {
        'auc_mean': auc_mean,
        'auc_std': auc_std,
        'n_regions': len(mt_cols),
        'regions_used': [get_region_name(col) for col in mt_cols],
        'n_subjects': int(n_valid)
    }


def compute_matched_whole_brain_baseline(df_regional, oasis_csv_path):
    """
    Compute whole-brain nWBV atrophy AUC on the SAME 42 subjects
    with the SAME baseline CDR labels used for regional analysis.
    This provides a controlled comparison (same cohort, same labels).
    """
    # Load raw OASIS data
    df_oasis = pd.read_csv(oasis_csv_path)

    # Get subject IDs from regional cohort
    regional_subjects = set(df_regional['Subject ID'].values)

    # Compute annualized nWBV atrophy for each subject
    atrophy_data = []
    for subj_id in regional_subjects:
        subj_data = df_oasis[df_oasis['Subject ID'] == subj_id].sort_values('Visit')
        if len(subj_data) < 2:
            continue

        first = subj_data.iloc[0]
        last = subj_data.iloc[-1]

        nwbv_first = first['nWBV']
        nwbv_last = last['nWBV']
        mr_delay_days = last['MR Delay']

        if pd.isna(nwbv_first) or pd.isna(nwbv_last) or mr_delay_days <= 0:
            continue

        years = mr_delay_days / 365.25
        if years < 0.5:
            continue

        annualized_atrophy = ((nwbv_last - nwbv_first) / years) * 100

        atrophy_data.append({
            'Subject ID': subj_id,
            'annualized_atrophy': annualized_atrophy
        })

    df_atrophy = pd.DataFrame(atrophy_data)

    # Merge with regional data to get the SAME baseline CDR labels
    df_merged = df_regional[['Subject ID', 'demented']].merge(
        df_atrophy, on='Subject ID', how='inner'
    )

    if len(df_merged) < 20:
        print(f"Insufficient matched subjects for whole-brain baseline: {len(df_merged)}")
        return None

    X = df_merged['annualized_atrophy'].values.reshape(-1, 1)
    y = df_merged['demented'].values

    # Use SAME CV setup as regional analysis
    auc_mean, auc_std = compute_region_cv_auc(X, y)

    print(f"\nMATCHED WHOLE-BRAIN BASELINE (n={len(df_merged)}, same subjects & labels)")
    print(f"  Whole-brain nWBV atrophy AUC: {auc_mean:.3f} ± {auc_std:.3f}")

    return {
        'feature': 'whole_brain_nWBV_atrophy',
        'auc_mean': auc_mean,
        'auc_std': auc_std,
        'n_subjects': len(df_merged),
        'description': 'Whole-brain atrophy on same 42 subjects with same baseline CDR labels'
    }


def analyze_regional_atrophy(csv_path, output_path, oasis_csv_path=None):
    """Main regional analysis pipeline."""

    print("=" * 60)
    print("OASIS-2 REGIONAL ATROPHY ANALYSIS - PHASE 2")
    print("=" * 60)

    # Load data
    df, label_cols = load_regional_data(csv_path)

    print(f"\nAnalyzing {len(label_cols)} regions...")

    # Analyze each region
    region_results = []
    for col in label_cols:
        result = analyze_single_region(df, col)
        if result:
            region_results.append(result)
            mt_marker = " [MT]" if result['is_medial_temporal'] else ""
            print(f"  {result['name']}: AUC={result['auc_mean']:.3f}±{result['auc_std']:.3f}, "
                  f"p={result['p_value']:.4f}{mt_marker}")

    # Sort by AUC (descending)
    region_results.sort(key=lambda x: x['auc_mean'], reverse=True)

    print(f"\n{len(region_results)} regions with sufficient data (>=20 subjects)")

    # Combined medial-temporal model
    print("\n" + "=" * 60)
    print("COMBINED MEDIAL-TEMPORAL MODEL")
    print("=" * 60)

    mt_combined = analyze_combined_medial_temporal(df, label_cols)

    if mt_combined:
        print(f"Regions: {', '.join(mt_combined['regions_used'])}")
        print(f"AUC: {mt_combined['auc_mean']:.3f} ± {mt_combined['auc_std']:.3f}")
        print(f"N subjects: {mt_combined['n_subjects']}")
    else:
        print("Could not compute combined medial-temporal model")

    # Compute matched whole-brain baseline (same 42 subjects, same labels)
    print("\n" + "=" * 60)
    print("MATCHED WHOLE-BRAIN COMPARISON")
    print("=" * 60)

    matched_baseline = None
    if oasis_csv_path and oasis_csv_path.exists():
        matched_baseline = compute_matched_whole_brain_baseline(df, oasis_csv_path)
    else:
        print("OASIS CSV not found - cannot compute matched whole-brain baseline")

    # Compute Bonferroni threshold and count significant regions
    n_tests = len(region_results)
    bonferroni_threshold = 0.05 / n_tests if n_tests > 0 else 0.05
    regions_p05 = [r for r in region_results if r['p_value'] < 0.05]
    regions_bonferroni = [r for r in region_results if r['p_value'] < bonferroni_threshold]

    # Top region analysis (for when combined model overfits)
    top_region = region_results[0] if region_results else None

    print(f"\nSignificance summary:")
    print(f"  Bonferroni threshold: p < {bonferroni_threshold:.4f}")
    print(f"  Regions at p < 0.05: {len(regions_p05)}")
    print(f"  Regions surviving Bonferroni: {len(regions_bonferroni)}")

    # Compare top region to matched whole-brain baseline
    if top_region and matched_baseline:
        improvement = top_region['auc_mean'] - matched_baseline['auc_mean']
        print(f"\n  Top region: {top_region['name']} (AUC {top_region['auc_mean']:.3f})")
        print(f"  Matched whole-brain: AUC {matched_baseline['auc_mean']:.3f}")
        print(f"  Improvement: {improvement:+.3f}")
        print(f"  Beats matched whole-brain: {'YES' if improvement > 0 else 'NO'}")

    # Build output structure
    results = {
        'status': 'complete',
        'metadata': {
            'n_subjects': len(df),
            'n_regions_analyzed': len(region_results),
            'n_tests': n_tests,
            'bonferroni_threshold': bonferroni_threshold,
            'n_regions_p05': len(regions_p05),
            'n_regions_bonferroni': len(regions_bonferroni),
            'analysis_date': pd.Timestamp.now().isoformat()
        },
        'matched_baseline': matched_baseline,  # Same 42 subjects, same labels - controlled comparison
        'phase1_reference': {
            'feature': 'whole_brain_nWBV',
            'auc': PHASE1_FULL_COHORT_AUC,
            'description': 'Phase 1 whole-brain (full 150-subject cohort, last-visit CDR) - for reference only'
        },
        'regions': region_results,
        'top_region': top_region,
        'medial_temporal_combined': mt_combined
    }

    # Export results
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 60)
    print(f"[OK] Results exported to: {output_path}")
    print("=" * 60)

    return results


def write_pending_status(output_path):
    """Write a pending status JSON when input data is missing."""
    results = {
        'status': 'pending',
        'message': 'Awaiting regional_atrophy.csv from Phase 2 segmentation'
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"[PENDING] Wrote pending status to: {output_path}")


if __name__ == '__main__':
    csv_path = Path(__file__).parent.parent / 'data' / 'processed' / 'regional_atrophy.csv'
    output_path = Path(__file__).parent.parent / 'web' / 'public' / 'data' / 'regional_results.json'
    oasis_csv_path = Path(__file__).parent.parent / 'data' / 'raw' / 'oasis_longitudinal.csv'

    if not csv_path.exists():
        print(f"Regional atrophy data not found at: {csv_path}")
        print("Phase 2 segmentation has not been run yet.")
        write_pending_status(output_path)
    else:
        analyze_regional_atrophy(csv_path, output_path, oasis_csv_path)
