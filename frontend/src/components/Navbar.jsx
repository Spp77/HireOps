import React from 'react';

export default function Navbar({ view, setView, user, setUser, showNotifs, setShowNotifs, unreadCount }) {
  return (
    <header>
      <div className="logo">
        <div className="logo-icon"><i className="fa-solid fa-briefcase"></i></div>
        HireOps
      </div>

      <nav className="nav-tabs">
        <button 
          className={`nav-tab ${view === 'browse' ? 'active' : ''}`} 
          onClick={() => setView('browse')}
        >
          <i className="fa-solid fa-compass" style={{marginRight: 6}}></i> Browse Jobs
        </button>

        {user.role === 'CANDIDATE' && (
          <button 
            className={`nav-tab ${view === 'candidate' ? 'active' : ''}`} 
            onClick={() => setView('candidate')}
          >
            <i className="fa-solid fa-user-check" style={{marginRight: 6}}></i> Candidate Hub
          </button>
        )}

        {user.role === 'RECRUITER' && (
          <button 
            className={`nav-tab ${view === 'recruiter' ? 'active' : ''}`} 
            onClick={() => setView('recruiter')}
          >
            <i className="fa-solid fa-chart-line" style={{marginRight: 6}}></i> Recruiter Portal
          </button>
        )}
      </nav>

      <div className="user-actions">
        <button 
          className="glass-btn" 
          style={{fontSize: 12}}
          onClick={() => setUser({...user, role: user.role === 'CANDIDATE' ? 'RECRUITER' : 'CANDIDATE'})}
        >
          Switch Role: <span className={`role-badge ${user.role === 'CANDIDATE' ? 'role-candidate' : 'role-recruiter'}`}>{user.role}</span>
        </button>

        <button className="glass-btn" style={{position: 'relative', padding: '8px 12px'}} onClick={() => setShowNotifs(!showNotifs)}>
          <i className="fa-regular fa-bell"></i>
          {unreadCount > 0 && (
            <span style={{position: 'absolute', top: -4, right: -4, background: '#f43f5e', color: '#fff', fontSize: 10, fontWeight: 700, borderRadius: 10, width: 18, height: 18, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
              {unreadCount}
            </span>
          )}
        </button>
      </div>
    </header>
  );
}
