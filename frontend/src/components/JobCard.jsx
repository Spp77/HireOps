import React from 'react';

export default function JobCard({ job, isSaved, onToggleSave, onSelectDetail, onSelectApply }) {
  return (
    <div className="glass-panel job-card">
      <div>
        <div className="card-header">
          <div className="company-info">
            <div className="company-logo-placeholder">
              {job.company?.name ? job.company.name.charAt(0) : 'J'}
            </div>
            <div>
              <h3 className="job-title">{job.title}</h3>
              <div className="company-name">{job.company?.name || 'Enterprise'}</div>
            </div>
          </div>
          <button 
            style={{background: 'transparent', border: 'none', color: isSaved ? '#f59e0b' : 'var(--text-subtle)', cursor: 'pointer', fontSize: 18}}
            onClick={() => onToggleSave(job.id)}
          >
            <i className={isSaved ? 'fa-solid fa-bookmark' : 'fa-regular fa-bookmark'}></i>
          </button>
        </div>

        <div className="job-meta">
          <span className="meta-tag"><i className="fa-solid fa-location-dot"></i> {job.location}</span>
          <span className="meta-tag"><i className="fa-solid fa-clock"></i> {job.job_type}</span>
        </div>

        <div className="skills-list">
          {(job.skills_required || []).map((sk, idx) => (
            <span key={idx} className="skill-tag">{sk}</span>
          ))}
        </div>
      </div>

      <div className="card-footer">
        <div className="salary-range">
          ${(job.salary_min / 1000).toFixed(0)}k - ${(job.salary_max / 1000).toFixed(0)}k
        </div>
        <div style={{display: 'flex', gap: 8}}>
          <button className="glass-btn" style={{fontSize: 13}} onClick={() => onSelectDetail(job)}>
            Details
          </button>
          <button className="btn-primary" style={{fontSize: 13, padding: '6px 14px'}} onClick={() => onSelectApply(job)}>
            Apply
          </button>
        </div>
      </div>
    </div>
  );
}
