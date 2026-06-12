"""
OASIS-2 Tabular Analysis - Phase 1
Computes longitudinal brain atrophy metrics from tabular data.
NO fabricated values - all metrics computed from real data.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score, accuracy_score
from scipy.stats import mannwhitneyu, ttest_ind
import warnings
warnings.filterwarnings('ignore')


def load_oasis_data(csv_path):
    """Load and validate OASIS-2 tabular data."""
    df = pd.read_csv(csv_path)

    required_cols = ['Subject ID', 'MR Delay', 'nWBV', 'CDR', 'Group', 'Visit']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    print(f"Loaded {len(df)} sessions from {df['Subject ID'].nunique()} subjects")
    print(f"Columns: {list(df.columns)}")
    return df


def compute_subject_features(df):
    """
    Compute per-subject longitudinal features.
    Returns one row per subject with ≥2 visits.

    Features:
    - baseline_nWBV: nWBV at first visit
    - annualized_atrophy_rate: (nWBV_last - nWBV_first) / years * 100
    - target: CDR > 0 at last visit (1=demented, 0=non-demented)
    - group: original Group label for analysis
    """

    subjects = []

    for subject_id, group in df.groupby('Subject ID'):
        group = group.sort_values('Visit')

        if len(group) < 2:
            continue  # Need at least 2 timepoints

        first = group.iloc[0]
        last = group.iloc[-1]

        # MR Delay is in DAYS - convert to years
        mr_delay_days = last['MR Delay']
        if pd.isna(mr_delay_days) or mr_delay_days <= 0:
            continue  # Invalid time interval

        years = mr_delay_days / 365.25

        # nWBV is already normalized - use as-is
        nwbv_first = first['nWBV']
        nwbv_last = last['nWBV']

        if pd.isna(nwbv_first) or pd.isna(nwbv_last):
            continue  # Missing volume data

        # Annualized percent change
        annualized_atrophy = ((nwbv_last - nwbv_first) / years) * 100

        # Target: CDR > 0 at last visit (handles Converted naturally)
        cdr_last = last['CDR']
        if pd.isna(cdr_last):
            continue

        target = 1 if cdr_last > 0 else 0

        subjects.append({
            'subject_id': subject_id,
            'baseline_nWBV': nwbv_first,
            'annualized_atrophy_rate': annualized_atrophy,
            'years_followup': years,
            'target': target,
            'group': last['Group'],  # Keep original label for reporting
            'baseline_age': first.get('Age', np.nan),
            'baseline_mmse': first.get('MMSE', np.nan),
            'baseline_cdr': first['CDR']
        })

    return pd.DataFrame(subjects)


def compute_cross_validated_metrics(X, y):
    """
    Stratified 5-fold cross-validation.
    Returns mean AUC ± std and mean accuracy ± std.
    """

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    aucs = []
    accs = []

    for train_idx, test_idx in skf.split(X, y):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        clf = LogisticRegression(random_state=42, max_iter=1000)
        clf.fit(X_train, y_train)

        y_pred_proba = clf.predict_proba(X_test)[:, 1]
        y_pred = clf.predict(X_test)

        aucs.append(roc_auc_score(y_test, y_pred_proba))
        accs.append(accuracy_score(y_test, y_pred))

    return {
        'auc_mean': np.mean(aucs),
        'auc_std': np.std(aucs),
        'accuracy_mean': np.mean(accs),
        'accuracy_std': np.std(accs),
        'n_folds': 5
    }


def compute_group_statistics(df_subjects):
    """
    Compare atrophy rates between demented and non-demented groups.
    Returns effect size and p-value.
    """

    demented = df_subjects[df_subjects['target'] == 1]['annualized_atrophy_rate'].values
    non_demented = df_subjects[df_subjects['target'] == 0]['annualized_atrophy_rate'].values

    # Mann-Whitney U test (non-parametric, robust to outliers)
    statistic, p_value = mannwhitneyu(demented, non_demented, alternative='less')

    # Cohen's d effect size
    mean_diff = np.mean(demented) - np.mean(non_demented)
    pooled_std = np.sqrt((np.std(demented)**2 + np.std(non_demented)**2) / 2)
    cohens_d = mean_diff / pooled_std if pooled_std > 0 else 0

    return {
        'demented_mean': float(np.mean(demented)),
        'demented_std': float(np.std(demented)),
        'demented_n': len(demented),
        'non_demented_mean': float(np.mean(non_demented)),
        'non_demented_std': float(np.std(non_demented)),
        'non_demented_n': len(non_demented),
        'p_value': float(p_value),
        'cohens_d': float(cohens_d),
        'test': 'Mann-Whitney U'
    }


def compute_baseline_discrimination(df_subjects):
    """
    Check if baseline nWBV alone discriminates groups.
    This is important context: demented subjects have lower baseline volumes.
    """

    X = df_subjects[['baseline_nWBV']].values
    y = df_subjects['target'].values

    return compute_cross_validated_metrics(X, y)


def compute_combined_discrimination(df_subjects):
    """
    Test if combining baseline nWBV + atrophy rate improves discrimination.
    This determines whether atrophy rate adds signal beyond baseline volume.
    """

    X = df_subjects[['baseline_nWBV', 'annualized_atrophy_rate']].values
    y = df_subjects['target'].values

    return compute_cross_validated_metrics(X, y)


def analyze_oasis_tabular(csv_path, output_path):
    """Main analysis pipeline."""

    print("=" * 60)
    print("OASIS-2 TABULAR ANALYSIS - PHASE 1")
    print("=" * 60)

    # Load data
    df = load_oasis_data(csv_path)

    # Compute per-subject features
    print("\nComputing per-subject longitudinal features...")
    df_subjects = compute_subject_features(df)

    print(f"Subjects with >=2 visits: {len(df_subjects)}")
    print(f"Target distribution: {df_subjects['target'].value_counts().to_dict()}")
    print(f"Group distribution: {df_subjects['group'].value_counts().to_dict()}")

    # Check for subjects with valid features
    if len(df_subjects) < 20:
        raise ValueError("Insufficient subjects for analysis")

    # 1. Atrophy rate classification
    print("\n" + "=" * 60)
    print("CLASSIFICATION: Atrophy Rate -> Dementia Status")
    print("=" * 60)

    X_atrophy = df_subjects[['annualized_atrophy_rate']].values
    y = df_subjects['target'].values

    atrophy_metrics = compute_cross_validated_metrics(X_atrophy, y)

    print(f"Feature: Annualized nWBV atrophy rate (% per year)")
    print(f"AUC: {atrophy_metrics['auc_mean']:.3f} ± {atrophy_metrics['auc_std']:.3f}")
    print(f"Accuracy: {atrophy_metrics['accuracy_mean']:.3f} ± {atrophy_metrics['accuracy_std']:.3f}")
    print(f"Method: Stratified {atrophy_metrics['n_folds']}-fold CV")

    # 2. Baseline nWBV classification (for context)
    print("\n" + "=" * 60)
    print("BASELINE COMPARISON: Baseline nWBV -> Dementia Status")
    print("=" * 60)

    baseline_metrics = compute_baseline_discrimination(df_subjects)

    print(f"Feature: Baseline nWBV (at first visit)")
    print(f"AUC: {baseline_metrics['auc_mean']:.3f} ± {baseline_metrics['auc_std']:.3f}")
    print(f"Accuracy: {baseline_metrics['accuracy_mean']:.3f} ± {baseline_metrics['accuracy_std']:.3f}")
    print(f"\nNOTE: Baseline volume is discriminative because demented subjects")
    print(f"      have lower brain volumes even before longitudinal decline.")

    # 3. Combined model (baseline + atrophy rate)
    print("\n" + "=" * 60)
    print("COMBINED MODEL: Baseline nWBV + Atrophy Rate -> Dementia Status")
    print("=" * 60)

    combined_metrics = compute_combined_discrimination(df_subjects)

    print(f"Features: Baseline nWBV + Annualized atrophy rate")
    print(f"AUC: {combined_metrics['auc_mean']:.3f} ± {combined_metrics['auc_std']:.3f}")
    print(f"Accuracy: {combined_metrics['accuracy_mean']:.3f} ± {combined_metrics['accuracy_std']:.3f}")

    # Evaluate if combined model improves on individual features
    atrophy_auc = atrophy_metrics['auc_mean']
    baseline_auc = baseline_metrics['auc_mean']
    combined_auc = combined_metrics['auc_mean']
    best_single = max(atrophy_auc, baseline_auc)

    if combined_auc > best_single + 0.02:
        print(f"\nCombining features improves AUC by {combined_auc - best_single:.3f}")
    else:
        print(f"\nCombined model does not substantially improve over single features")

    # 4. Group statistics
    print("\n" + "=" * 60)
    print("GROUP COMPARISON: Atrophy Rate by Dementia Status")
    print("=" * 60)

    group_stats = compute_group_statistics(df_subjects)

    print(f"Demented (n={group_stats['demented_n']}): "
          f"{group_stats['demented_mean']:.3f} ± {group_stats['demented_std']:.3f} % per year")
    print(f"Non-demented (n={group_stats['non_demented_n']}): "
          f"{group_stats['non_demented_mean']:.3f} ± {group_stats['non_demented_std']:.3f} % per year")
    print(f"Cohen's d: {group_stats['cohens_d']:.3f}")
    print(f"p-value: {group_stats['p_value']:.4f} ({group_stats['test']})")

    # 5. Per-subject trajectories for dashboard
    trajectories = []
    for _, row in df_subjects.iterrows():
        trajectories.append({
            'subject_id': row['subject_id'],
            'baseline_nWBV': float(row['baseline_nWBV']),
            'atrophy_rate': float(row['annualized_atrophy_rate']),
            'years_followup': float(row['years_followup']),
            'group': row['group'],
            'demented': bool(row['target'])
        })

    # 6. Export results
    results = {
        'metadata': {
            'n_subjects': len(df_subjects),
            'n_demented': int(group_stats['demented_n']),
            'n_non_demented': int(group_stats['non_demented_n']),
            'analysis_date': pd.Timestamp.now().isoformat()
        },
        'atrophy_classification': {
            'feature': 'annualized_nWBV_atrophy_rate',
            'auc_mean': float(atrophy_metrics['auc_mean']),
            'auc_std': float(atrophy_metrics['auc_std']),
            'accuracy_mean': float(atrophy_metrics['accuracy_mean']),
            'accuracy_std': float(atrophy_metrics['accuracy_std']),
            'method': f"Stratified {atrophy_metrics['n_folds']}-fold CV"
        },
        'baseline_classification': {
            'feature': 'baseline_nWBV',
            'auc_mean': float(baseline_metrics['auc_mean']),
            'auc_std': float(baseline_metrics['auc_std']),
            'accuracy_mean': float(baseline_metrics['accuracy_mean']),
            'accuracy_std': float(baseline_metrics['accuracy_std']),
            'note': 'Baseline volume alone is discriminative'
        },
        'combined_classification': {
            'features': 'baseline_nWBV + annualized_atrophy_rate',
            'auc_mean': float(combined_metrics['auc_mean']),
            'auc_std': float(combined_metrics['auc_std']),
            'accuracy_mean': float(combined_metrics['accuracy_mean']),
            'accuracy_std': float(combined_metrics['accuracy_std']),
            'improvement_over_best_single': float(combined_metrics['auc_mean'] - max(atrophy_metrics['auc_mean'], baseline_metrics['auc_mean'])),
            'note': 'Tests whether combining features improves discrimination'
        },
        'group_comparison': group_stats,
        'subject_trajectories': trajectories
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 60)
    print(f"[OK] Results exported to: {output_path}")
    print("=" * 60)

    return results


if __name__ == '__main__':
    csv_path = Path(__file__).parent.parent / 'data' / 'raw' / 'oasis_longitudinal.csv'
    output_path = Path(__file__).parent.parent / 'web' / 'public' / 'data' / 'results.json'

    if not csv_path.exists():
        print(f"ERROR: Data file not found at {csv_path}")
        print("Please place the OASIS-2 CSV in data/raw/oasis_longitudinal.csv")
        exit(1)

    analyze_oasis_tabular(csv_path, output_path)
