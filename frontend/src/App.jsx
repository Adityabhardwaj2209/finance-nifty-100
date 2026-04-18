import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Activity, 
  BarChart3, 
  Building2, 
  Search, 
  ArrowUpRight, 
  TrendingUp,
  ShieldCheck,
  LayoutDashboard,
  Wallet,
  PieChart,
  ChevronRight
} from 'lucide-react';
import CompanyDetailModal from './components/CompanyDetailModal';
import './App.css';

const API_BASE = 'http://localhost:8000';

function App() {
  const [companies, setCompanies] = useState([]);
  const [sectors, setSectors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSector, setSelectedSector] = useState('All');
  const [selectedCompanyId, setSelectedCompanyId] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const hosts = ['http://localhost:8000', 'http://127.0.0.1:8000'];
      let success = false;
      
      for (const host of hosts) {
        try {
          const [compRes, sectRes] = await Promise.all([
            axios.get(`${host}/api/companies/`),
            axios.get(`${host}/api/sectors/`)
          ]);
          setCompanies(compRes.data);
          setSectors(sectRes.data);
          success = true;
          break;
        } catch (e) {
          console.warn(`Connection to ${host} failed...`);
        }
      }
      
      if (!success) {
        throw new Error("Unable to connect to financial intelligence engine. Ensure Django is running at port 8000.");
      }
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const filteredCompanies = companies.filter(c => {
    const term = searchTerm.toLowerCase();
    const nameMatch = c.company_name.toLowerCase().includes(term);
    const idMatch = c.id.toLowerCase().includes(term);
    const matchesSearch = nameMatch || idMatch;
    const matchesSector = selectedSector === 'All' || c.sector === selectedSector;
    return matchesSearch && matchesSector;
  });

  const getScoreColor = (score) => {
    if (score >= 80) return '#10b981'; // Success
    if (score >= 60) return '#f59e0b'; // Warning
    return '#ef4444'; // Danger
  };

  return (
    <div className="app-container">
      {/* Sidebar / Nav */}
      <nav className="navbar animate-fade-in">
        <div className="logo">
          <Activity size={32} className="accent-glow-icon" />
          <span className="logo-text">NIFTY 100 <span className="intel-badge">INTEL</span></span>
        </div>
        
        <div className="search-wrapper glass">
          <Search size={18} color="#94a3b8" />
          <input 
            type="text" 
            placeholder="Explore companies or symbols..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="nav-profile">
          <div className="status-indicator">
            <div className="status-dot"></div>
            <span>Engine Online</span>
          </div>
        </div>
      </nav>

      <main className="dashboard-content">
        <header className="hero-section animate-fade-in">
          <div className="hero-text">
            <h1>Market Intelligence <span className="text-secondary">Dashboard</span></h1>
            <p>India's Nifty 100 deep-dive analytics, financial health scoring, and AI insights.</p>
          </div>
        </header>

        {error && (
          <div className="error-card glass animate-fade-in">
            <ShieldCheck size={24} color="#ef4444" />
            <div className="error-info">
              <h4>Connection Fault</h4>
              <p>{error}</p>
            </div>
            <button className="retry-btn" onClick={fetchData}>Re-establish Connection</button>
          </div>
        )}

        {/* Global Market Overview */}
        <section className="stats-strip animate-fade-in">
          <div className="stat-card glass glass-hover">
            <div className="stat-icon-box primary">
              <TrendingUp size={24} />
            </div>
            <div className="stat-content">
              <label>Avg. Health Score</label>
              <h3>{(sectors.reduce((acc, s) => acc + s.avg_score, 0) / (sectors.length || 1)).toFixed(1)}</h3>
            </div>
            <div className="mini-trend positive">
              <ArrowUpRight size={14} /> 2.4%
            </div>
          </div>

          <div className="stat-card glass glass-hover">
            <div className="stat-icon-box accent">
              <Building2 size={24} />
            </div>
            <div className="stat-content">
              <label>Companies Tracked</label>
              <h3>{companies.length}</h3>
            </div>
          </div>

          <div className="stat-card glass glass-hover">
            <div className="stat-icon-box success">
              <PieChart size={24} />
            </div>
            <div className="stat-content">
              <label>Sectors Analyzed</label>
              <h3>{sectors.length}</h3>
            </div>
          </div>
        </section>

        {/* Sector Navigation */}
        <section className="sector-navigation animate-fade-in">
          <div className="section-title">
            <LayoutDashboard size={20} />
            <h2>Sector Performance</h2>
          </div>
          <div className="sector-pills">
            <button 
              className={`pill ${selectedSector === 'All' ? 'active' : ''}`}
              onClick={() => setSelectedSector('All')}
            >
              All Segments
            </button>
            {sectors.map(s => (
              <button 
                key={s.sector} 
                className={`pill ${selectedSector === s.sector ? 'active' : ''}`}
                onClick={() => setSelectedSector(s.sector)}
              >
                {s.sector}
                <span className="pill-val">{s.avg_score.toFixed(0)}</span>
              </button>
            ))}
          </div>
        </section>

        {/* Intelligence Table */}
        <section className="intel-table-section animate-fade-in">
          <div className="glass table-container">
            <table>
              <thead>
                <tr>
                  <th>SYMBOL</th>
                  <th>COMPANY ENTITY</th>
                  <th>SECTOR</th>
                  <th>LATEST FINANCIALS</th>
                  <th>INTEL SCORE</th>
                  <th>ACTIONS</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  Array(5).fill(0).map((_, i) => (
                    <tr key={i} className="skeleton-row">
                      <td colSpan="6"><div className="skeleton-line"></div></td>
                    </tr>
                  ))
                ) : filteredCompanies.map(company => (
                  <tr key={company.id} className="company-row" onClick={() => setSelectedCompanyId(company.id)}>
                    <td className="symbol-cell">
                      <span className="symbol-badge">{company.id}</span>
                    </td>
                    <td className="entity-cell">
                      <div className="entity-info">
                        <strong>{company.company_name}</strong>
                        <span>{company.sub_sector || 'Diversified'}</span>
                      </div>
                    </td>
                    <td>
                      <span className="sector-badge">{company.sector || 'N/A'}</span>
                    </td>
                    <td className="financial-cell">
                      {company.financial_summary ? (
                        <div className="fin-summary">
                          <span>₹{(company.financial_summary.sales / 1000).toFixed(1)}k Cr Rev</span>
                          <span className="mini-label">FY{company.financial_summary.year}</span>
                        </div>
                      ) : '---'}
                    </td>
                    <td className="score-cell">
                      <div className="score-viz">
                        <div className="score-stack">
                           <span className="score-number" style={{ color: getScoreColor(company.latest_score?.overall_score || 0) }}>
                            {company.latest_score?.overall_score?.toFixed(0) || 'N/A'}
                          </span>
                          <div className="progress-bar-bg">
                            <div 
                              className="progress-bar-fill" 
                              style={{ 
                                width: `${company.latest_score?.overall_score || 0}%`,
                                backgroundColor: getScoreColor(company.latest_score?.overall_score || 0)
                              }}
                            ></div>
                          </div>
                        </div>
                        <span className="health-label">{company.latest_score?.health_label}</span>
                      </div>
                    </td>
                    <td className="action-cell">
                      <button className="action-button">
                        <ChevronRight size={18} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </main>

      {selectedCompanyId && (
        <CompanyDetailModal 
          companyId={selectedCompanyId} 
          onClose={() => setSelectedCompanyId(null)}
          apiHost={API_BASE}
        />
      )}

      <footer className="footer animate-fade-in">
        <p>© 2026 NIFTY 100 Intelligence Engine. Proprietary AI Scoring.</p>
      </footer>

      <style>{`
        .navbar {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 2rem 0;
          margin-bottom: 2rem;
        }
        .logo { display: flex; align-items: center; gap: 1rem; }
        .logo-text { font-size: 1.5rem; font-weight: 900; letter-spacing: -1px; }
        .intel-badge { color: var(--accent); position: relative; }
        
        .search-wrapper {
          display: flex;
          align-items: center;
          gap: 1rem;
          padding: 0.75rem 1.5rem;
          width: 400px;
        }
        .search-wrapper input {
          background: transparent;
          border: none;
          color: white;
          width: 100%;
          outline: none;
          font-size: 0.9375rem;
        }
        
        .status-indicator {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          background: rgba(16, 185, 129, 0.1);
          padding: 0.5rem 1rem;
          border-radius: 99px;
          font-size: 0.8125rem;
          color: #10b981;
          font-weight: 600;
        }
        .status-dot {
          width: 8px;
          height: 8px;
          background: #10b981;
          border-radius: 50%;
          box-shadow: 0 0 8px #10b981;
        }

        .hero-section { margin-bottom: 3rem; }
        .hero-text h1 { margin-bottom: 0.5rem; }
        .hero-text p { font-size: 1.125rem; }

        .error-card {
          padding: 1.5rem;
          display: flex;
          align-items: center;
          gap: 1.5rem;
          margin-bottom: 3rem;
          border-left: 4px solid var(--danger);
        }
        .error-info h4 { color: var(--danger); margin-bottom: 0.25rem; }
        .retry-btn {
          margin-left: auto;
          background: var(--danger);
          color: white;
          border: none;
          padding: 0.6rem 1.25rem;
          border-radius: 8px;
          font-weight: 600;
          cursor: pointer;
        }

        .stats-strip {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 1.5rem;
          margin-bottom: 4rem;
        }
        .stat-card {
          padding: 2rem;
          display: flex;
          align-items: center;
          gap: 1.5rem;
          position: relative;
        }
        .stat-icon-box {
          width: 56px;
          height: 56px;
          border-radius: 14px;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .stat-icon-box.primary { background: rgba(99, 102, 241, 0.15); color: var(--primary); }
        .stat-icon-box.accent { background: rgba(45, 212, 191, 0.15); color: var(--accent); }
        .stat-icon-box.success { background: rgba(16, 185, 129, 0.15); color: #10b981; }
        
        .stat-content label { font-size: 0.8125rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 1px; }
        .stat-content h3 { font-size: 2rem; font-weight: 800; }
        
        .mini-trend {
          position: absolute;
          top: 1.5rem;
          right: 1.5rem;
          font-size: 0.75rem;
          font-weight: 700;
          display: flex;
          align-items: center;
          gap: 0.25rem;
          padding: 0.25rem 0.6rem;
          border-radius: 6px;
        }
        .mini-trend.positive { background: rgba(16, 185, 129, 0.1); color: #10b981; }

        .sector-navigation { margin-bottom: 3rem; }
        .section-title { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.5rem; color: var(--text-secondary); }
        .section-title h2 { font-size: 1.25rem; color: white; }
        
        .sector-pills {
          display: flex;
          gap: 0.75rem;
          overflow-x: auto;
          padding-bottom: 1rem;
        }
        .pill {
          padding: 0.6rem 1.25rem;
          border-radius: 99px;
          background: rgba(255, 255, 255, 0.03);
          border: 1px solid var(--border);
          color: var(--text-secondary);
          display: flex;
          align-items: center;
          gap: 0.75rem;
          cursor: pointer;
          transition: all 0.2s;
          white-space: nowrap;
        }
        .pill:hover { border-color: var(--primary); color: white; }
        .pill.active { background: var(--primary); border-color: var(--primary); color: white; font-weight: 600; }
        .pill-val { background: rgba(0, 0, 0, 0.2); padding: 0.1rem 0.5rem; border-radius: 4px; font-size: 0.75rem; }

        .intel-table-section { margin-bottom: 5rem; }
        .table-container { width: 100%; }
        table { width: 100%; border-collapse: collapse; }
        th { text-align: left; padding: 1.5rem; font-size: 0.75rem; color: var(--text-secondary); letter-spacing: 1px; border-bottom: 1px solid var(--border); }
        td { padding: 1.5rem; border-bottom: 1px solid var(--border); }
        
        .company-row { cursor: pointer; transition: background 0.2s; }
        .company-row:hover { background: rgba(255, 255, 255, 0.02); }
        
        .symbol-badge { 
          background: rgba(99, 102, 241, 0.1); 
          color: var(--primary); 
          padding: 0.4rem 0.8rem; 
          border-radius: 8px; 
          font-family: monospace; 
          font-weight: 700; 
          border: 1px solid rgba(99, 102, 241, 0.2);
        }
        
        .entity-info { display: flex; flex-direction: column; gap: 0.25rem; }
        .entity-info span { font-size: 0.8125rem; color: var(--text-secondary); }
        
        .sector-badge { font-size: 0.8125rem; background: var(--border); padding: 0.3rem 0.75rem; border-radius: 6px; }
        .fin-summary { display: flex; flex-direction: column; }
        .mini-label { font-size: 0.6875rem; color: var(--text-secondary); }
        
        .score-viz { display: flex; align-items: center; gap: 1rem; }
        .score-stack { flex: 1; display: flex; align-items: center; gap: 0.75rem; }
        .score-number { font-size: 1.25rem; font-weight: 800; width: 30px; }
        .progress-bar-bg { flex: 1; height: 6px; background: rgba(255, 255, 255, 0.05); border-radius: 3px; overflow: hidden; }
        .progress-bar-fill { height: 100%; border-radius: 3px; transition: width 1s ease-in-out; }
        .health-label { font-size: 0.6875rem; color: var(--text-secondary); text-transform: uppercase; font-weight: 700; width: 60px; }

        .action-button { background: transparent; border: 1px solid var(--border); color: var(--text-secondary); padding: 0.5rem; border-radius: 8px; cursor: pointer; }
        .company-row:hover .action-button { border-color: var(--primary); color: white; transform: translateX(2px); }

        .footer { padding-bottom: 4rem; text-align: center; color: var(--text-secondary); font-size: 0.875rem; }

        .skeleton-row { height: 80px; }
        .skeleton-line { height: 20px; background: var(--border); border-radius: 4px; animation: pulse 1.5s infinite; }
        @keyframes pulse { 0% { opacity: 0.5; } 50% { opacity: 0.8; } 100% { opacity: 0.5; } }
      `}</style>
    </div>
  );
}

export default App;
