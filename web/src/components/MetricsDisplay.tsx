'use client';

import { ClassificationMetrics, GroupComparison } from '@/types';

interface MetricsDisplayProps {
  atrophyMetrics: ClassificationMetrics;
  baselineMetrics: ClassificationMetrics;
  groupComparison: GroupComparison;
}

export default function MetricsDisplay({
  atrophyMetrics,
  baselineMetrics,
  groupComparison
}: MetricsDisplayProps) {
  return (
    <div className="card">
      <h2>Computed Metrics</h2>

      <h3>Atrophy Rate Classification</h3>
      <div className="metric">
        <span className="metric-label">Feature</span>
        <span className="metric-value">Annualized nWBV change (% per year)</span>
      </div>
      <div className="metric">
        <span className="metric-label">AUC (mean ± std)</span>
        <span className="metric-value highlight">
          {atrophyMetrics.auc_mean.toFixed(3)} ± {atrophyMetrics.auc_std.toFixed(3)}
        </span>
      </div>
      <div className="metric">
        <span className="metric-label">Accuracy (mean ± std)</span>
        <span className="metric-value">
          {atrophyMetrics.accuracy_mean.toFixed(3)} ± {atrophyMetrics.accuracy_std.toFixed(3)}
        </span>
      </div>
      <div className="metric">
        <span className="metric-label">Method</span>
        <span className="metric-value">{atrophyMetrics.method}</span>
      </div>

      <h3 style={{ marginTop: '1.5rem' }}>Baseline Volume (Context)</h3>
      <div className="metric">
        <span className="metric-label">Feature</span>
        <span className="metric-value">Baseline nWBV</span>
      </div>
      <div className="metric">
        <span className="metric-label">AUC (mean ± std)</span>
        <span className="metric-value">
          {baselineMetrics.auc_mean.toFixed(3)} ± {baselineMetrics.auc_std.toFixed(3)}
        </span>
      </div>
      <div className="note">
        Baseline volume alone is discriminative because demented subjects have lower
        brain volumes even before longitudinal decline. Both features show similar
        weak-to-moderate discrimination (AUC ~0.64).
      </div>

      <h3 style={{ marginTop: '1.5rem' }}>Group Comparison</h3>
      <div className="metric">
        <span className="metric-label">Demented (n={groupComparison.demented_n})</span>
        <span className="metric-value">
          {groupComparison.demented_mean.toFixed(3)} ± {groupComparison.demented_std.toFixed(3)} % per year
        </span>
      </div>
      <div className="metric">
        <span className="metric-label">Non-demented (n={groupComparison.non_demented_n})</span>
        <span className="metric-value">
          {groupComparison.non_demented_mean.toFixed(3)} ± {groupComparison.non_demented_std.toFixed(3)} % per year
        </span>
      </div>
      <div className="metric">
        <span className="metric-label">Cohen&apos;s d</span>
        <span className="metric-value highlight">{groupComparison.cohens_d.toFixed(3)}</span>
      </div>
      <div className="metric">
        <span className="metric-label">p-value ({groupComparison.test})</span>
        <span className="metric-value">{groupComparison.p_value.toFixed(4)}</span>
      </div>
    </div>
  );
}
