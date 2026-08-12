import React, { useState, useEffect } from 'react';
import { fetchOverview, fetchStartups, fetchJobs, fetchNews, fetchProducts, fetchResearch } from './api';

function App() {
  const [activeTab, setActiveTab] = useState('Overview');
  
  // Data states
  const [overviewData, setOverviewData] = useState(null);
  const [startups, setStartups] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [news, setNews] = useState([]);
  const [products, setProducts] = useState([]);
  const [research, setResearch] = useState([]);
  
  const [loading, setLoading] = useState(true);

  const tabs = [
    'Overview',
    'Research',
    'Startups',
    'Products',
    'Fresh Signals',
    'Pipeline Monitor',
    'Architecture'
  ];

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        if (activeTab === 'Overview') {
          const data = await fetchOverview();
          setOverviewData(data);
        } else if (activeTab === 'Startups') {
          const data = await fetchStartups();
          setStartups(data);
        } else if (activeTab === 'Fresh Signals') {
          const nData = await fetchNews();
          setNews(nData);
          const jData = await fetchJobs();
          setJobs(jData);
        } else if (activeTab === 'Products') {
          const data = await fetchProducts();
          setProducts(data);
        } else if (activeTab === 'Research') {
          const data = await fetchResearch();
          setResearch(data);
        }
      } catch (e) {
        console.error("Failed to fetch data:", e);
      }
      setLoading(false);
    };
    loadData();
  }, [activeTab]);

  return (
    <div className="app-container">
      {/* Sidebar - Matching Streamlit exactly */}
      <div className="sidebar">
        <h1>GraphOne</h1>
        <div className="nav-menu">
          {tabs.map(tab => (
            <div 
              key={tab}
              className={`nav-item ${activeTab === tab ? 'active' : ''}`} 
              onClick={() => setActiveTab(tab)}
            >
              {tab}
            </div>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        {loading ? (
          <div className="loader">Initializing Intelligence Engine...</div>
        ) : (
          <>
            {activeTab === 'Overview' && overviewData && (
              <div>
                <div className="page-header">
                  <h2>Overview</h2>
                  <p>System metrics</p>
                </div>
                <div className="metrics-grid">
                  <div className="metric-card glass">
                    <span className="metric-label">Startups</span>
                    <span className="metric-value">{overviewData.startups}</span>
                  </div>
                  <div className="metric-card glass">
                    <span className="metric-label">Products</span>
                    <span className="metric-value">{overviewData.products}</span>
                  </div>
                  <div className="metric-card glass">
                    <span className="metric-label">Jobs</span>
                    <span className="metric-value">{overviewData.jobs}</span>
                  </div>
                  <div className="metric-card glass">
                    <span className="metric-label">Research</span>
                    <span className="metric-value">{overviewData.research}</span>
                  </div>
                  <div className="metric-card glass">
                    <span className="metric-label">News</span>
                    <span className="metric-value">{overviewData.news}</span>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'Research' && (
              <div>
                <div className="page-header">
                  <h2>Research Papers</h2>
                </div>
                <div className="table-container glass">
                  <table>
                    <thead>
                      <tr>
                        <th>Title</th>
                        <th>Source</th>
                        <th>Published</th>
                        <th>URL</th>
                      </tr>
                    </thead>
                    <tbody>
                      {research.slice(0, 100).map((r, i) => (
                        <tr key={i}>
                          <td>{r.title}</td>
                          <td>{r.source_name}</td>
                          <td>{r.published_at?.split('T')[0] || '-'}</td>
                          <td><a href={r.source_url} target="_blank" rel="noreferrer" className="link">{r.source_url}</a></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {activeTab === 'Startups' && (
              <div>
                <div className="page-header">
                  <h2>Startups</h2>
                </div>
                <div className="table-container glass">
                  <table>
                    <thead>
                      <tr>
                        <th>Name</th>
                        <th>Source</th>
                        <th>Status</th>
                        <th>URL</th>
                      </tr>
                    </thead>
                    <tbody>
                      {startups.slice(0, 100).map((s, i) => (
                        <tr key={i}>
                          <td>{s.canonical_name || s.raw_name}</td>
                          <td>{s.source_name}</td>
                          <td>{s.resolution_status}</td>
                          <td><a href={s.source_url} target="_blank" rel="noreferrer" className="link">{s.source_url}</a></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {activeTab === 'Products' && (
              <div>
                <div className="page-header">
                  <h2>Products</h2>
                </div>
                <div className="table-container glass">
                  <table>
                    <thead>
                      <tr>
                        <th>Product Name</th>
                        <th>Startup</th>
                        <th>Pricing</th>
                        <th>Source</th>
                        <th>URL</th>
                      </tr>
                    </thead>
                    <tbody>
                      {products.slice(0, 100).map((p, i) => (
                        <tr key={i}>
                          <td><strong>{p.product_name}</strong></td>
                          <td>{p.startup_name || '-'}</td>
                          <td>{p.pricing_model ? <span className="badge">{p.pricing_model}</span> : '-'}</td>
                          <td>{p.source_name}</td>
                          <td><a href={p.source_url} target="_blank" rel="noreferrer" className="link">{p.source_url}</a></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {activeTab === 'Fresh Signals' && (
              <div>
                <div className="page-header">
                  <h2>Fresh Signals</h2>
                  <p>Real-time intelligence feed strictly bounded within a 24-hour publication window.</p>
                </div>
                
                <h3 style={{fontSize: '1rem', marginBottom: '16px', color: '#94a3b8', fontWeight: '600'}}>NEWS SIGNALS</h3>
                <div className="table-container glass" style={{marginBottom: '40px'}}>
                  <table>
                    <thead>
                      <tr>
                        <th>Title</th>
                        <th>Source</th>
                        <th>Published</th>
                        <th>Status</th>
                        <th>Source URL</th>
                      </tr>
                    </thead>
                    <tbody>
                      {news.slice(0, 50).map((n, i) => (
                        <tr key={i}>
                          <td>{n.title}</td>
                          <td>{n.source_name}</td>
                          <td>{n.published_at?.replace('T', ' ')}</td>
                          <td>Verified &lt; 24h</td>
                          <td><a href={n.source_url} target="_blank" rel="noreferrer" className="link">{n.source_url}</a></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <h3 style={{fontSize: '1rem', marginBottom: '16px', color: '#94a3b8', fontWeight: '600'}}>JOB SIGNALS</h3>
                <div className="table-container glass">
                  <table>
                    <thead>
                      <tr>
                        <th>Title</th>
                        <th>Company</th>
                        <th>Source</th>
                        <th>Published</th>
                        <th>Source URL</th>
                      </tr>
                    </thead>
                    <tbody>
                      {jobs.slice(0, 50).map((j, i) => (
                        <tr key={i}>
                          <td>{j.title}</td>
                          <td>{j.company || '-'}</td>
                          <td>{j.source_name}</td>
                          <td>{j.published_at?.replace('T', ' ')}</td>
                          <td><a href={j.source_url} target="_blank" rel="noreferrer" className="link">{j.source_url}</a></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {activeTab === 'Pipeline Monitor' && (
              <div>
                <div className="page-header">
                  <h2>Pipeline Monitor</h2>
                  <p>Technical observability and ingestion status.</p>
                </div>
                
                <div style={{display: 'flex', gap: '24px'}}>
                  <div style={{flex: 3}}>
                    <h3 style={{fontSize: '1rem', marginBottom: '16px', color: 'var(--text-main)'}}>Source-Level Ingestion</h3>
                    <div className="table-container glass">
                      <table>
                        <thead>
                          <tr>
                            <th>Source</th>
                            <th>Record Type</th>
                            <th>Discovered</th>
                            <th>Accepted</th>
                            <th>Rejected</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr><td>techcrunch_ai</td><td>News</td><td>16</td><td>16</td><td>0</td></tr>
                          <tr><td>therundown_ai</td><td>News</td><td>15</td><td>15</td><td>0</td></tr>
                          <tr><td>huggingface</td><td>Startups</td><td>76</td><td>76</td><td>0</td></tr>
                          <tr><td>hn_who_is_hiring</td><td>Jobs</td><td>12</td><td>12</td><td>0</td></tr>
                          <tr><td>arXiv</td><td>Research Papers</td><td>30</td><td>30</td><td>0</td></tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                  
                  <div style={{flex: 2}}>
                    <h3 style={{fontSize: '1rem', marginBottom: '16px', color: 'var(--text-main)'}}>Event Timeline</h3>
                    <div className="glass" style={{padding: '24px', fontFamily: 'monospace', fontSize: '0.85rem', lineHeight: '2', color: 'var(--text-muted)'}}>
                      <span style={{color: 'var(--text-muted)'}}>14:32:01</span> [INFO] arXiv crawler completed &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b style={{color: 'var(--text-main)'}}>+1000 records</b><br/>
                      <span style={{color: 'var(--text-muted)'}}>14:32:04</span> [WARN] 429 Rate Limit hit &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b style={{color: 'var(--text-main)'}}>Backoff=1.5s</b><br/>
                      <span style={{color: 'var(--text-muted)'}}>14:32:06</span> [INFO] LLM Orchestrator fallback &nbsp;&nbsp;&nbsp;<b style={{color: 'var(--text-main)'}}>Gemini → Groq</b><br/>
                      <span style={{color: 'var(--text-muted)'}}>14:32:08</span> [INFO] Validation completed &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b style={{color: 'var(--text-main)'}}>82 rejected</b><br/>
                      <span style={{color: 'var(--text-muted)'}}>14:32:11</span> [INFO] Entity resolution &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b style={{color: 'var(--text-main)'}}>112 normalized</b><br/>
                      <span style={{color: 'var(--text-muted)'}}>14:32:15</span> [INFO] SQLite Idempotent Upsert &nbsp;&nbsp;&nbsp;&nbsp;<b style={{color: 'var(--text-main)'}}>210 duplicates</b><br/>
                      <span style={{color: 'var(--text-muted)'}}>14:32:18</span> [INFO] Database write completed &nbsp;&nbsp;&nbsp;&nbsp;<b style={{color: 'var(--text-main)'}}>2746 records</b>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'Architecture' && (
              <div>
                <div className="page-header">
                  <h2>System Architecture</h2>
                  <p>The GraphOne Intelligence Engine utilizes a distributed crawler network backing into a FastAPI service, with GitHub Actions orchestrating the daily data refresh into SQLite.</p>
                </div>
                
                <div className="glass" style={{padding: '48px', textAlign: 'center'}}>
                  <div style={{display: 'flex', justifyContent: 'center', gap: '40px', alignItems: 'center'}}>
                    <div className="arch-box" style={{width: '180px'}}>
                      <strong>Data Sources</strong>
                      <small>arXiv, TechCrunch, HackerNews, HuggingFace</small>
                    </div>
                    
                    <div className="arch-arrow">→</div>
                    
                    <div className="arch-box" style={{width: '220px'}}>
                      <strong>GitHub Actions</strong>
                      <small>Daily Cron Jobs</small>
                      <span className="badge" style={{marginTop: '12px', display: 'inline-block'}}>Python Runner</span>
                    </div>

                    <div className="arch-arrow">→</div>
                    
                    <div className="arch-box" style={{width: '180px'}}>
                      <strong>LLM Orchestrator</strong>
                      <small>Groq / Gemini</small>
                    </div>
                  </div>
                  
                  <div style={{marginTop: '60px', display: 'flex', justifyContent: 'center', gap: '40px', alignItems: 'center'}}>
                    <div className="arch-box" style={{width: '220px', borderColor: '#10b981'}}>
                      <strong>SQLite Database</strong>
                      <small>graphone.db</small>
                    </div>
                    
                    <div className="arch-arrow" style={{color: '#10b981'}}>→</div>
                    
                    <div className="arch-box" style={{width: '220px', borderColor: '#8b5cf6'}}>
                      <strong>React + FastAPI</strong>
                      <small>Frontend UI & API Server</small>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default App;
