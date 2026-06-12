export interface SubjectTrajectory {
  subject_id: string;
  baseline_nWBV: number;
  atrophy_rate: number;
  years_followup: number;
  group: string;
  demented: boolean;
}

export interface ClassificationMetrics {
  feature: string;
  auc_mean: number;
  auc_std: number;
  accuracy_mean: number;
  accuracy_std: number;
  method: string;
  note?: string;
}

export interface GroupComparison {
  demented_mean: number;
  demented_std: number;
  demented_n: number;
  non_demented_mean: number;
  non_demented_std: number;
  non_demented_n: number;
  p_value: number;
  cohens_d: number;
  test: string;
}

export interface AnalysisResults {
  metadata: {
    n_subjects: number;
    n_demented: number;
    n_non_demented: number;
    analysis_date: string;
  };
  atrophy_classification: ClassificationMetrics;
  baseline_classification: ClassificationMetrics;
  group_comparison: GroupComparison;
  subject_trajectories: SubjectTrajectory[];
}

// Phase 2: Regional atrophy types
export interface RegionResult {
  label: string;
  label_num: number | null;
  name: string;
  auc_mean: number;
  auc_std: number;
  p_value: number;
  n_subjects: number;
  is_medial_temporal: boolean;
}

export interface MedialTemporalCombined {
  auc_mean: number;
  auc_std: number;
  n_regions: number;
  regions_used: string[];
  n_subjects: number;
}

export interface MatchedBaseline {
  feature: string;
  auc_mean: number;
  auc_std: number;
  n_subjects: number;
  description: string;
}

export interface RegionalResults {
  status: 'complete' | 'pending';
  message?: string;
  metadata?: {
    n_subjects: number;
    n_regions_analyzed: number;
    n_tests: number;
    bonferroni_threshold: number;
    n_regions_p05: number;
    n_regions_bonferroni: number;
    analysis_date: string;
  };
  matched_baseline?: MatchedBaseline | null;  // Controlled comparison: same 42 subjects, same labels
  phase1_reference?: {
    feature: string;
    auc: number;
    description: string;
  };
  regions?: RegionResult[];
  top_region?: RegionResult | null;
  medial_temporal_combined?: MedialTemporalCombined | null;
}
