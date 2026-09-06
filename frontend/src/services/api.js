const API_BASE = '/api/v1';

export async function fetchActiveJobs() {
  try {
    const res = await fetch(`${API_BASE}/jobs/`);
    if (!res.ok) throw new Error('Failed to fetch jobs');
    const data = await res.json();
    return data.results || data;
  } catch (err) {
    console.warn('API error, using fallback state:', err);
    return null;
  }
}

export async function submitJobApplication(jobId, coverLetter, token) {
  const res = await fetch(`${API_BASE}/applications/apply/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ job: jobId, cover_letter: coverLetter }),
  });
  return res.json();
}

export async function updateApplicationStatus(appId, newStatus, token) {
  const res = await fetch(`${API_BASE}/applications/${appId}/status/`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ status: newStatus }),
  });
  return res.json();
}
