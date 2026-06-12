'use client';

import { SubjectTrajectory } from '@/types';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';

interface CohortSummaryProps {
  subjects: SubjectTrajectory[];
}

export default function CohortSummary({ subjects }: CohortSummaryProps) {
  const demented = subjects.filter(s => s.demented);
  const nonDemented = subjects.filter(s => !s.demented);

  const demendedData = demented.map(s => ({
    baseline: s.baseline_nWBV,
    atrophy: s.atrophy_rate,
    subject: s.subject_id
  }));

  const nonDementedData = nonDemented.map(s => ({
    baseline: s.baseline_nWBV,
    atrophy: s.atrophy_rate,
    subject: s.subject_id
  }));

  return (
    <div className="card">
      <h2>Cohort Summary</h2>

      <div style={{ marginBottom: '1.5rem' }}>
        <div className="metric">
          <span className="metric-label">Total Subjects</span>
          <span className="metric-value">{subjects.length}</span>
        </div>
        <div className="metric">
          <span className="metric-label">Demented (CDR {'>'} 0)</span>
          <span className="metric-value">{demented.length}</span>
        </div>
        <div className="metric">
          <span className="metric-label">Non-demented (CDR = 0)</span>
          <span className="metric-value">{nonDemented.length}</span>
        </div>
      </div>

      <h3>Baseline nWBV vs. Atrophy Rate</h3>
      <ResponsiveContainer width="100%" height={400}>
        <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#333" />
          <XAxis
            type="number"
            dataKey="baseline"
            name="Baseline nWBV"
            domain={[0.6, 0.85]}
            stroke="#999"
            label={{ value: 'Baseline nWBV', position: 'insideBottom', offset: -10, fill: '#999' }}
          />
          <YAxis
            type="number"
            dataKey="atrophy"
            name="Atrophy Rate"
            stroke="#999"
            label={{ value: 'Atrophy Rate (% per year)', angle: -90, position: 'insideLeft', fill: '#999' }}
          />
          <Tooltip
            cursor={{ strokeDasharray: '3 3' }}
            contentStyle={{
              backgroundColor: '#1a1a1a',
              border: '1px solid #333',
              borderRadius: '4px'
            }}
          />
          <Legend />
          <ReferenceLine y={0} stroke="#666" strokeDasharray="3 3" />
          <Scatter
            name="Non-demented"
            data={nonDementedData}
            fill="#66b3ff"
          />
          <Scatter
            name="Demented"
            data={demendedData}
            fill="#ff6666"
          />
        </ScatterChart>
      </ResponsiveContainer>

      <div className="note">
        Demented subjects tend toward lower baseline volumes and faster atrophy rates,
        though substantial overlap exists between groups (AUC ~0.64).
      </div>
    </div>
  );
}
