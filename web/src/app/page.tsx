'use client';

import { useEffect, useState } from 'react';
import { AnalysisResults, RegionalResults as RegionalResultsType } from '@/types';
import SubjectViewer from '@/components/SubjectViewer';
import CohortSummary from '@/components/CohortSummary';
import MetricsDisplay from '@/components/MetricsDisplay';
import RegionalResults from '@/components/RegionalResults';

export default function Home() {
  const [data, setData] = useState<AnalysisResults | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Phase 2: Regional results state
  const [regionalData, setRegionalData] = useState<RegionalResultsType | null>(null);
  const [regionalLoading, setRegionalLoading] = useState(true);
  const [regionalError, setRegionalError] = useState<string | null>(null);

  useEffect(() => {
    // Load Phase 1 results
    fetch('/data/results.json')
      .then(res => {
        if (!res.ok) throw new Error('Failed to load analysis results');
        return res.json();
      })
      .then(setData)
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));

    // Load Phase 2 regional results (graceful failure if missing)
    fetch('/data/regional_results.json')
      .then(res => {
        if (!res.ok) return null;
        return res.json();
      })
      .then(setRegionalData)
      .catch(() => setRegionalError('Regional analysis not available'))
      .finally(() => setRegionalLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="container">
        <div className="loading">Loading analysis results...</div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="container">
        <div className="error">
          Error: {error || 'No data available'}
          <br />
          <br />
          Make sure to run the analysis script first:
          <pre>python analysis/tabular_analysis.py</pre>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <header className="header">
        <h1>OASIS-2 Brain Atrophy Analyzer</h1>
        <p>
          Longitudinal analysis of brain volume changes in aging and Alzheimer&apos;s disease
        </p>
        <div style={{ marginTop: '1rem', color: '#666', fontSize: '0.9rem' }}>
          {data.metadata.n_subjects} subjects analyzed |{' '}
          {data.metadata.n_demented} demented |{' '}
          {data.metadata.n_non_demented} non-demented |{' '}
          Analysis date: {new Date(data.metadata.analysis_date).toLocaleDateString()}
        </div>
      </header>

      <div className="grid">
        <SubjectViewer subjects={data.subject_trajectories} />
        <MetricsDisplay
          atrophyMetrics={data.atrophy_classification}
          baselineMetrics={data.baseline_classification}
          groupComparison={data.group_comparison}
        />
      </div>

      <CohortSummary subjects={data.subject_trajectories} />

      {/* Phase 2: Regional Atrophy Analysis */}
      <RegionalResults
        data={regionalData}
        loading={regionalLoading}
        error={regionalError}
      />

      <footer style={{ marginTop: '3rem', paddingTop: '2rem', borderTop: '1px solid #333' }}>
        <div className="note">
          <strong>Data source:</strong> OASIS-2 Longitudinal MRI dataset.
          Use of OASIS data prohibits facial recognition or attempts to re-identify subjects.
          <br /><br />
          <strong>Metrics:</strong> All values are computed from real data using stratified
          5-fold cross-validation. No values are fabricated or hardcoded.
        </div>
      </footer>
    </div>
  );
}
