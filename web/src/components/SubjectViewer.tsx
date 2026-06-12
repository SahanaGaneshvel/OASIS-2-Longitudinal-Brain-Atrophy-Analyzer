'use client';

import { useState } from 'react';
import { SubjectTrajectory } from '@/types';

interface SubjectViewerProps {
  subjects: SubjectTrajectory[];
}

export default function SubjectViewer({ subjects }: SubjectViewerProps) {
  const [selectedSubject, setSelectedSubject] = useState<SubjectTrajectory | null>(
    subjects.length > 0 ? subjects[0] : null
  );

  const handleSubjectChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const subject = subjects.find(s => s.subject_id === e.target.value);
    setSelectedSubject(subject || null);
  };

  if (!selectedSubject) {
    return <div className="card">No subjects available</div>;
  }

  return (
    <div className="card">
      <h2>Subject Viewer</h2>

      <div className="subject-selector">
        <select
          value={selectedSubject.subject_id}
          onChange={handleSubjectChange}
        >
          {subjects.map(subject => (
            <option key={subject.subject_id} value={subject.subject_id}>
              {subject.subject_id} - {subject.group}
            </option>
          ))}
        </select>
      </div>

      <div className="subject-info">
        <div className="subject-info-grid">
          <div className="info-item">
            <span className="info-label">Subject ID</span>
            <span className="info-value">{selectedSubject.subject_id}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Group</span>
            <span className="info-value">{selectedSubject.group}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Baseline nWBV</span>
            <span className="info-value">{selectedSubject.baseline_nWBV.toFixed(4)}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Follow-up Duration</span>
            <span className="info-value">{selectedSubject.years_followup.toFixed(2)} years</span>
          </div>
          <div className="info-item">
            <span className="info-label">Atrophy Rate</span>
            <span className="info-value" style={{
              color: selectedSubject.atrophy_rate < 0 ? '#ff6666' : '#66ff66'
            }}>
              {selectedSubject.atrophy_rate.toFixed(3)} % per year
            </span>
          </div>
          <div className="info-item">
            <span className="info-label">Dementia Status</span>
            <span className="info-value">
              {selectedSubject.demented ? 'Demented (CDR > 0)' : 'Non-demented (CDR = 0)'}
            </span>
          </div>
        </div>
      </div>

      <div className="note">
        <strong>Atrophy rate</strong> is computed as annualized percent change in nWBV
        between first and last scan. Negative values indicate brain volume loss.
      </div>
    </div>
  );
}
