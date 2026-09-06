import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import JobCard from './components/JobCard';
import { fetchActiveJobs } from './services/api';

const INITIAL_JOBS = [
  {
    id: '11111111-1111-1111-1111-111111111111',
    title: 'Senior Full Stack Engineer',
    company: { id: 'c1', name: 'TechScale Innovations', location: 'San Francisco, CA' },
    location: 'Remote / San Francisco',
    job_type: 'FULL_TIME',
    experience_level: 'SENIOR',
    salary_min: 140000,
    salary_max: 185000,
    skills_required: ['React', 'Django', 'PostgreSQL', 'Docker'],
    description: 'Lead modern cloud architecture and scalable REST API endpoints.',
    created_at: '2026-08-01'
  },
  {
    id: '22222222-2222-2222-2222-222222222222',
    title: 'AI / Machine Learning Engineer',
    company: { id: 'c2', name: 'NeuroSystems AI', location: 'Austin, TX' },
    location: 'Austin, TX (Hybrid)',
    job_type: 'FULL_TIME',
    experience_level: 'MID',
    salary_min: 130000,
    salary_max: 160000,
    skills_required: ['Python', 'PyTorch', 'FastAPI', 'Celery'],
    description: 'Develop custom NLP models and real-time predictive analytics web pipelines.',
    created_at: '2026-08-02'
  },
  {
    id: '33333333-3333-3333-3333-333333333333',
    title: 'Backend Operations Lead',
    company: { id: 'c3', name: 'CloudScale Global', location: 'New York, NY' },
    location: 'Remote',
    job_type: 'REMOTE',
    experience_level: 'LEAD',
    salary_min: 160000,
    salary_max: 210000,
    skills_required: ['Django', 'Redis', 'Kubernetes', 'AWS'],
    description: 'Lead backend microservices architecture and zero-downtime database routing.',
    created_at: '2026-08-03'
  }
];

export default function App() {
  const [view, setView] = useState('browse');
  const [user, setUser] = useState({
    id: 'usr-1',
    email: 'candidate@hireops.com',
    first_name: 'Alex',
    last_name: 'Dev',
    role: 'CANDIDATE'
  });

  const [jobs, setJobs] = useState(INITIAL_JOBS);
  const [applications, setApplications] = useState([
    {
      id: 'app-1',
      job: INITIAL_JOBS[0],
      status: 'SHORTLISTED',
      cover_letter: 'Excited about the full stack engineering role!',
      created_at: '2026-08-03'
    }
  ]);
  const [savedJobs, setSavedJobs] = useState([INITIAL_JOBS[1].id]);
  const [notifications, setNotifications] = useState([
    { id: 'n1', title: 'Application Update', message: 'Your application for Senior Full Stack Engineer has been Shortlisted!', is_read: false },
    { id: 'n2', title: 'New Job Alert', message: 'CloudScale Global posted a new Remote role.', is_read: true }
  ]);

  const [showNotifs, setShowNotifs] = useState(false);
  const [selectedJob, setSelectedJob] = useState(null);
  const [showPostModal, setShowPostModal] = useState(false);
  const [showApplyModal, setShowApplyModal] = useState(null);
  const [toast, setToast] = useState(null);

  const [searchTerm, setSearchTerm] = useState('');
  const [selectedJobType, setSelectedJobType] = useState('ALL');

  const notifyToast = (msg) => {
    setToast(msg);
    setTimeout(() => setToast(null), 3000);
  };

  useEffect(() => {
    fetchActiveJobs().then(data => {
      if (data && data.length > 0) setJobs(data);
    });
  }, []);

  const filteredJobs = jobs.filter(j => {
    const matchesSearch = j.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          j.company?.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          j.location.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = selectedJobType === 'ALL' || j.job_type === selectedJobType;
    return matchesSearch && matchesType;
  });

  const handleApply = (jobId, coverLetter) => {
    const targetJob = jobs.find(j => j.id === jobId);
    const newApp = {
      id: `app-${Date.now()}`,
      job: targetJob,
      status: 'PENDING',
      cover_letter: coverLetter,
      created_at: new Date().toISOString().split('T')[0]
    };
    setApplications([newApp, ...applications]);
    setShowApplyModal(null);
    notifyToast(`Application submitted for "${targetJob.title}"!`);
  };

  const handleToggleSave = (jobId) => {
    if (savedJobs.includes(jobId)) {
      setSavedJobs(savedJobs.filter(id => id !== jobId));
      notifyToast('Removed job from saved items.');
    } else {
      setSavedJobs([...savedJobs, jobId]);
      notifyToast('Saved job to your bookmark hub!');
    }
  };

  const handlePostJob = (jobData) => {
    const newJob = {
      id: `job-${Date.now()}`,
      ...jobData,
      company: { id: 'c1', name: 'My Tech Enterprise', location: jobData.location },
      view_count: 0,
      application_count: 0,
      created_at: new Date().toISOString().split('T')[0]
    };
    setJobs([newJob, ...jobs]);
    setShowPostModal(false);
    notifyToast('Job successfully published to HireOps portal!');
  };

  const handleStatusChange = (appId, newStatus) => {
    setApplications(applications.map(a => a.id === appId ? { ...a, status: newStatus } : a));
    notifyToast(`Applicant status updated to ${newStatus}`);
  };

  const unreadCount = notifications.filter(n => !n.is_read).length;

  return (
    <div>
      <Navbar 
        view={view} 
        setView={setView} 
        user={user} 
        setUser={setUser} 
        showNotifs={showNotifs} 
        setShowNotifs={setShowNotifs}
        unreadCount={unreadCount}
      />

      {showNotifs && (
        <div className="glass-panel" style={{position: 'absolute', top: 70, right: 32, width: 380, zIndex: 500, padding: 16}}>
          <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: 12}}>
            <h4 style={{fontSize: 15, fontWeight: 700}}>Notifications</h4>
            <button className="glass-btn" style={{fontSize: 11}} onClick={() => setNotifications(notifications.map(n => ({...n, is_read: true})))}>Mark all read</button>
          </div>
          {notifications.map(n => (
            <div key={n.id} style={{padding: 12, borderRadius: 8, background: 'rgba(255,255,255,0.03)', marginBottom: 8, borderLeft: !n.is_read ? '3px solid var(--primary)' : 'none'}}>
              <div style={{fontWeight: 600}}>{n.title}</div>
              <div style={{color: 'var(--text-muted)', fontSize: 13}}>{n.message}</div>
            </div>
          ))}
        </div>
      )}

      <main className="app-container">
        {view === 'browse' && (
          <div>
            <div className="glass-panel hero-search">
              <h1 className="hero-title">Discover Your Next Tech Milestone</h1>
              <p className="hero-subtitle">Connecting top-tier candidates with enterprise recruiters seamlessly.</p>
              
              <div className="search-bar">
                <div className="search-input-group">
                  <i className="fa-solid fa-magnifying-glass"></i>
                  <input 
                    type="text" 
                    placeholder="Search by job title, company, or tech stack..."
                    value={searchTerm}
                    onChange={e => setSearchTerm(e.target.value)}
                  />
                </div>
                <button className="btn-primary" style={{borderRadius: 100}}>Search Jobs</button>
              </div>
            </div>

            <div style={{display: 'flex', gap: 12, marginBottom: 24, alignItems: 'center'}}>
              <span style={{fontSize: 13, color: 'var(--text-muted)', fontWeight: 600}}>Job Type:</span>
              {['ALL', 'FULL_TIME', 'REMOTE', 'CONTRACT', 'INTERNSHIP'].map(type => (
                <span 
                  key={type} 
                  style={{padding: '6px 14px', borderRadius: 100, fontSize: 13, background: selectedJobType === type ? 'var(--primary)' : 'rgba(255,255,255,0.04)', color: '#fff', cursor: 'pointer'}}
                  onClick={() => setSelectedJobType(type)}
                >
                  {type.replace('_', ' ')}
                </span>
              ))}
            </div>

            <div className="jobs-grid">
              {filteredJobs.map(job => (
                <JobCard 
                  key={job.id} 
                  job={job} 
                  isSaved={savedJobs.includes(job.id)} 
                  onToggleSave={handleToggleSave}
                  onSelectDetail={setSelectedJob}
                  onSelectApply={setShowApplyModal}
                />
              ))}
            </div>
          </div>
        )}

        {view === 'candidate' && (
          <div>
            <h2 style={{fontSize: 26, fontWeight: 800, marginBottom: 24}}>Candidate Tracker Hub</h2>
            <div className="glass-panel" style={{padding: 24, marginBottom: 32}}>
              <h3 style={{fontSize: 18, fontWeight: 700, marginBottom: 16}}>Your Submitted Applications ({applications.length})</h3>
              {applications.map(app => (
                <div key={app.id} style={{padding: 16, background: 'rgba(255, 255, 255, 0.03)', borderRadius: 12, display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12}}>
                  <div>
                    <div style={{fontWeight: 700, fontSize: 16}}>{app.job.title}</div>
                    <div style={{color: 'var(--text-muted)', fontSize: 13}}>{app.job.company?.name} • Applied on {app.created_at}</div>
                  </div>
                  <div className={`status-pill status-${app.status.toLowerCase()}`}>{app.status}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {view === 'recruiter' && (
          <div>
            <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24}}>
              <div>
                <h2 style={{fontSize: 26, fontWeight: 800}}>Recruiter Dashboard</h2>
                <p style={{color: 'var(--text-muted)', fontSize: 14}}>Manage company job postings & candidate application funnels.</p>
              </div>
              <button className="btn-primary" onClick={() => setShowPostModal(true)}>
                <i className="fa-solid fa-plus"></i> Post New Job
              </button>
            </div>

            <div className="glass-panel" style={{padding: 24}}>
              <h3 style={{fontSize: 18, fontWeight: 700, marginBottom: 16}}>Applicant Evaluation Queue</h3>
              {applications.map(app => (
                <div key={app.id} style={{padding: 20, background: 'rgba(255, 255, 255, 0.03)', borderRadius: 12, marginBottom: 16}}>
                  <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: 12}}>
                    <div>
                      <h4 style={{fontSize: 16, fontWeight: 700}}>{user.first_name} {user.last_name}</h4>
                      <div style={{color: 'var(--text-muted)', fontSize: 13}}>Applied for <strong style={{color: '#60a5fa'}}>{app.job.title}</strong></div>
                    </div>
                    <select 
                      className="form-control" 
                      value={app.status}
                      onChange={e => handleStatusChange(app.id, e.target.value)}
                      style={{padding: '6px 12px', fontSize: 13, width: 'auto'}}
                    >
                      <option value="PENDING">Pending</option>
                      <option value="REVIEWING">Reviewing</option>
                      <option value="SHORTLISTED">Shortlisted</option>
                      <option value="ACCEPTED">Accepted</option>
                      <option value="REJECTED">Rejected</option>
                    </select>
                  </div>
                  <div style={{fontSize: 14, color: 'var(--text-muted)', fontStyle: 'italic', background: 'rgba(0,0,0,0.2)', padding: 12, borderRadius: 8}}>
                    "{app.cover_letter}"
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      {selectedJob && (
        <div className="modal-overlay" onClick={() => setSelectedJob(null)}>
          <div className="glass-panel modal-body" onClick={e => e.stopPropagation()}>
            <h2 style={{fontSize: 22, fontWeight: 800, marginBottom: 8}}>{selectedJob.title}</h2>
            <p style={{color: 'var(--text-muted)', marginBottom: 20}}>{selectedJob.description}</p>
            <button className="btn-primary" onClick={() => { setSelectedJob(null); setShowApplyModal(selectedJob); }}>Apply Now</button>
          </div>
        </div>
      )}

      {showApplyModal && (
        <div className="modal-overlay" onClick={() => setShowApplyModal(null)}>
          <div className="glass-panel modal-body" onClick={e => e.stopPropagation()}>
            <h3 style={{fontSize: 20, fontWeight: 800, marginBottom: 16}}>Apply for {showApplyModal.title}</h3>
            <form onSubmit={e => { e.preventDefault(); handleApply(showApplyModal.id, e.target.cover.value); }}>
              <div className="form-group">
                <label>Cover Letter</label>
                <textarea className="form-control" name="cover" required placeholder="Describe why you are a great fit for this role..."></textarea>
              </div>
              <div style={{display: 'flex', justifyContent: 'flex-end', gap: 12}}>
                <button type="button" className="glass-btn" onClick={() => setShowApplyModal(null)}>Cancel</button>
                <button type="submit" className="btn-primary">Submit Application</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showPostModal && (
        <div className="modal-overlay" onClick={() => setShowPostModal(false)}>
          <div className="glass-panel modal-body" onClick={e => e.stopPropagation()}>
            <h3 style={{fontSize: 20, fontWeight: 800, marginBottom: 20}}>Post New Opportunity</h3>
            <form onSubmit={e => {
              e.preventDefault();
              const fd = new FormData(e.target);
              handlePostJob({
                title: fd.get('title'),
                location: fd.get('location'),
                job_type: fd.get('job_type'),
                salary_min: parseInt(fd.get('salary_min')),
                salary_max: parseInt(fd.get('salary_max')),
                description: fd.get('description'),
                skills_required: fd.get('skills').split(',').map(s => s.trim())
              });
            }}>
              <div className="form-group">
                <label>Job Title</label>
                <input className="form-control" name="title" required placeholder="e.g. Senior Backend Architect" />
              </div>
              <div className="form-group">
                <label>Location</label>
                <input className="form-control" name="location" required placeholder="e.g. Remote / New York" />
              </div>
              <div className="form-group">
                <label>Skills (comma separated)</label>
                <input className="form-control" name="skills" defaultValue="Python, Django" />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea className="form-control" name="description" required placeholder="Describe the role..."></textarea>
              </div>
              <div style={{display: 'flex', justifyContent: 'flex-end', gap: 12}}>
                <button type="button" className="glass-btn" onClick={() => setShowPostModal(false)}>Cancel</button>
                <button type="submit" className="btn-primary">Publish Job</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {toast && (
        <div className="toast">
          <i className="fa-solid fa-circle-check" style={{color: 'var(--accent-emerald)', fontSize: 18}}></i>
          {toast}
        </div>
      )}
    </div>
  );
}
