#!/usr/bin/env python3
"""
Quick validation script to check if Phase 1 is ready to run.
Run this before attempting to run the analysis or build the frontend.
"""

import sys
from pathlib import Path
import json

def check_file(path, description, required=True):
    """Check if a file exists."""
    exists = path.exists()
    status = "✓" if exists else ("✗" if required else "⚠")
    print(f"{status} {description}: {path}")
    return exists or not required

def check_dir(path, description):
    """Check if a directory exists."""
    exists = path.is_dir()
    status = "✓" if exists else "✗"
    print(f"{status} {description}: {path}")
    return exists

def validate_csv(csv_path):
    """Validate OASIS-2 CSV has required columns."""
    try:
        import pandas as pd
        df = pd.read_csv(csv_path)

        required_cols = ['Subject ID', 'MR Delay', 'nWBV', 'CDR', 'Group', 'Visit']
        missing = [col for col in required_cols if col not in df.columns]

        if missing:
            print(f"  ✗ Missing columns: {missing}")
            return False

        print(f"  ✓ All required columns present")
        print(f"  ✓ {len(df)} rows, {df['Subject ID'].nunique()} unique subjects")
        return True

    except ImportError:
        print(f"  ⚠ pandas not installed, cannot validate CSV structure")
        return True
    except Exception as e:
        print(f"  ✗ Error reading CSV: {e}")
        return False

def validate_results_json(json_path):
    """Validate results.json structure."""
    try:
        with open(json_path) as f:
            data = json.load(f)

        required_keys = ['metadata', 'atrophy_classification', 'baseline_classification',
                        'group_comparison', 'subject_trajectories']
        missing = [k for k in required_keys if k not in data]

        if missing:
            print(f"  ✗ Missing keys: {missing}")
            return False

        n_subjects = data['metadata']['n_subjects']
        n_trajectories = len(data['subject_trajectories'])

        print(f"  ✓ Valid structure")
        print(f"  ✓ {n_subjects} subjects, {n_trajectories} trajectories")

        auc = data['atrophy_classification']['auc_mean']
        if auc == 0:
            print(f"  ⚠ AUC is 0 (placeholder data? run analysis script)")
        else:
            print(f"  ✓ AUC: {auc:.3f}")

        return True

    except Exception as e:
        print(f"  ✗ Error reading JSON: {e}")
        return False

def main():
    print("=" * 60)
    print("OASIS-2 Phase 1 Setup Validation")
    print("=" * 60)
    print()

    root = Path(__file__).parent
    all_ok = True

    # Check directory structure
    print("Directory Structure:")
    all_ok &= check_dir(root / 'data' / 'raw', "Data directory")
    all_ok &= check_dir(root / 'analysis', "Analysis directory")
    all_ok &= check_dir(root / 'web', "Web directory")
    print()

    # Check data file
    print("Data Files:")
    csv_path = root / 'data' / 'raw' / 'oasis_longitudinal.csv'
    if check_file(csv_path, "OASIS-2 CSV", required=True):
        validate_csv(csv_path)
    else:
        print("  → Download from: https://www.kaggle.com/datasets/nadiatriki/oasis-2-longitudinal-scan-data")
    print()

    # Check analysis files
    print("Analysis Files:")
    all_ok &= check_file(root / 'analysis' / 'tabular_analysis.py', "Analysis script")
    all_ok &= check_file(root / 'analysis' / 'requirements.txt', "Python requirements")
    print()

    # Check frontend files
    print("Frontend Files:")
    all_ok &= check_file(root / 'web' / 'package.json', "package.json")
    all_ok &= check_file(root / 'web' / 'tsconfig.json', "tsconfig.json")
    all_ok &= check_file(root / 'web' / 'src' / 'app' / 'page.tsx', "Main page")
    all_ok &= check_dir(root / 'web' / 'src' / 'components', "Components directory")
    print()

    # Check output files (optional)
    print("Generated Files (optional at this stage):")
    results_path = root / 'web' / 'public' / 'data' / 'results.json'
    if check_file(results_path, "Analysis results JSON", required=False):
        validate_results_json(results_path)
    else:
        print("  → Run 'python analysis/tabular_analysis.py' to generate")
    print()

    # Check Python dependencies
    print("Python Dependencies:")
    try:
        import pandas
        print("  ✓ pandas installed")
    except ImportError:
        print("  ✗ pandas not installed")
        all_ok = False

    try:
        import sklearn
        print("  ✓ scikit-learn installed")
    except ImportError:
        print("  ✗ scikit-learn not installed")
        all_ok = False

    try:
        import scipy
        print("  ✓ scipy installed")
    except ImportError:
        print("  ✗ scipy not installed")
        all_ok = False

    print()

    # Summary
    print("=" * 60)
    if all_ok:
        print("✓ Setup looks good! Next steps:")
        print()
        print("1. Run analysis:")
        print("   python analysis/tabular_analysis.py")
        print()
        print("2. Start frontend:")
        print("   cd web && npm install && npm run dev")
        print()
    else:
        print("✗ Some issues found. Please fix before proceeding.")
        print()
        print("If Python packages are missing:")
        print("   cd analysis && pip install -r requirements.txt")
        print()
        print("If OASIS-2 CSV is missing, download from:")
        print("   https://www.kaggle.com/datasets/nadiatriki/oasis-2-longitudinal-scan-data")
        print()
    print("=" * 60)

    return 0 if all_ok else 1

if __name__ == '__main__':
    sys.exit(main())
