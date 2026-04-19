import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  X, 
  TrendingUp, 
  TrendingDown, 
  Info, 
  CheckCircle2, 
  AlertCircle,
  ExternalLink,
  Globe,
  Building
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  AreaChart,
  Area,
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis
} from 'recharts';

const CompanyDetailModal = ({ companyId, onClose, apiHost }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  useEffect(() => {
    const fetchFullProfile = async () => {
      try {
        setLoading(true);
        const res = await axios.get(`${apiHost}/api/companies/${companyId}/full_profile/`);
        setData(res.data);
      } catch (err) {
        console.error("Error fetching full profile:", err);
      } finally {
        setLoading(false);
      }
    };
    if (companyId) fetchFullProfile();
  }, [companyId, apiHost]);

  if (!data && loading) return (
    <div className="modal-overlay">
      <div className="glass modal-content loading">
        <div className="spinner"></div>
        <p>Analyzing company intelligence...</p>
      </div>
    </div>
  );

  if (!data) return null;

  const { company, profit_loss, balance_sheet, scores, pros_cons } = data;
  const latestScore = scores[0] || {};

  const scoreData = [
    { subject: 'Profitability', A: latestScore.profitability_score || 0, fullMark: 100 },
    { subject: 'Growth', A: latestScore.growth_score || 0, fullMark: 100 },
    { subject: 'Leverage', A: latestScore.leverage_score || 0, fullMark: 100 },
    { subject: 'Cash Flow', A: latestScore.cashflow_score || 0, fullMark: 100 },
    { subject: 'Overall', A: latestScore.overall_score || 0, fullMark: 100 },
  ];

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="glass modal-content animate-fade-in" onClick={e => e.stopPropagation()}>
        <button className="close-btn" onClick={onClose}><X size={24} /></button>
        
        <header className="modal-header">
          <div className="header-info">
            <div className="company-branding">
              {company.company_logo ? (
                <img src={company.company_logo} alt={company.company_name} className="modal-logo" />
              ) : (
                <div className="modal-logo-placeholder">{company.id[0]}</div>
              )}
              <div>
                <h2>{company.company_name}</h2>
                <span className="symbol-large">{company.id}</span>
              </div>
            </div>
            <div className="header-links">
              {company.website && <a href={company.website} target="_blank" rel="noopener noreferrer"><Globe size={18} /> Website</a>}
              {company.nse_profile && <a href={company.nse_profile} target="_blank" rel="noopener noreferrer"><ExternalLink size={18} /> NSE</a>}
            </div>
          </div>
        </header>

        <nav className="modal-tabs">
          <button className={activeTab === 'overview' ? 'active' : ''} onClick={() => setActiveTab('overview')}>Intelligence Overview</button>
          <button className={activeTab === 'financials' ? 'active' : ''} onClick={() => setActiveTab('financials')}>Financial Trends</button>
          <button className={activeTab === 'analysis' ? 'active' : ''} onClick={() => setActiveTab('analysis')}>Analysis</button>
        </nav>

        <div className="tab-content">
          {activeTab === 'overview' && (
            <div className="overview-grid">
              <div className="score-radar-section glass">
                <h3>Health Score Breakdown</h3>
                <div className="radar-container">
                  <ResponsiveContainer width="100%" height={300}>
                    <RadarChart cx="50%" cy="50%" outerRadius="80%" data={scoreData}>
                      <PolarGrid stroke="#334155" />
                      <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                      <Radar
                        name={company.id}
                        dataKey="A"
                        stroke="#6366f1"
                        fill="#6366f1"
                        fillOpacity={0.6}
                      />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
              </div>
              
              <div className="quick-stats-section">
                <div className="stats-mini-grid">
                  <div className="mini-card glass">
                    <label>Health Label</label>
                    <span className={`label-badge ${latestScore.health_label?.toLowerCase()}`}>
                      {latestScore.health_label || 'N/A'}
                    </span>
                  </div>
                  <div className="mini-card glass" title="Return on Equity: Net Income / Shareholder's Equity. Higher is better.">
                    <label className="tooltip-label">ROE <Info size={12} /></label>
                    <span>{company.roe_percentage ? (company.roe_percentage).toFixed(2) + '%' : 'N/A'}</span>
                  </div>
                  <div className="mini-card glass" title="Return on Capital Employed: Indicates efficiency & profitability of capital investments.">
                    <label className="tooltip-label">ROCE <Info size={12} /></label>
                    <span>{company.roce_percentage ? (company.roce_percentage).toFixed(2) + '%' : 'N/A'}</span>
                  </div>
                  <div className="mini-card glass" title="A ratio above 1.0 indicates higher risk due to debt funding.">
                    <label className="tooltip-label">Debt/Equity <Info size={12} /></label>
                    <span>{balance_sheet[balance_sheet.length - 1]?.debt_to_equity?.toFixed(2) || 'N/A'}</span>
                  </div>
                </div>
                
                <div className="about-section glass" style={{ marginBottom: '1rem' }}>
                  <h3>About Company</h3>
                  <p>{company.about_company || 'Information not available.'}</p>
                </div>

                {data.hold_prediction && (
                  <div className="prediction-section glass">
                    <div className="prediction-header">
                      <TrendingUp color="#2dd4bf" size={24} />
                      <h3 style={{ margin: 0 }}>AI Hold Prediction: <span className="duration-text">{data.hold_prediction.duration}</span></h3>
                    </div>
                    <p>{data.hold_prediction.rationale}</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'financials' && (
            <div className="financials-grid">
              <div className="chart-card glass">
                <h3>Revenue & Profit Trend (₹ Cr)</h3>
                <div className="chart-container">
                  <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={profit_loss}>
                      <defs>
                        <linearGradient id="colorSales" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3}/>
                          <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                      <XAxis dataKey="year_label" stroke="#475569" />
                      <YAxis stroke="#475569" />
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '8px' }}
                        itemStyle={{ color: '#fff' }}
                      />
                      <Area type="monotone" dataKey="sales" stroke="#6366f1" fillOpacity={1} fill="url(#colorSales)" name="Revenue" />
                      <Area type="monotone" dataKey="net_profit" stroke="#10b981" fillOpacity={1} fill="transparent" name="Net Profit" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>
              
              <div className="chart-card glass">
                <h3>Operating Margin (%)</h3>
                <div className="chart-container">
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={profit_loss}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                      <XAxis dataKey="year_label" stroke="#475569" />
                      <YAxis stroke="#475569" />
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '8px' }}
                      />
                      <Line type="monotone" dataKey="opm_percentage" stroke="#f59e0b" strokeWidth={3} dot={{ r: 4 }} name="OPM %" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'analysis' && (
            <div className="analysis-grid">
              <div className="analysis-card pros glass">
                <div className="card-header">
                  <CheckCircle2 color="#10b981" />
                  <h3>Strengths</h3>
                </div>
                <ul>
                  {pros_cons?.pros ? pros_cons.pros.split('\n').map((p, i) => (
                    <li key={i}>{p}</li>
                  )) : <li>No specific strengths identified.</li>}
                </ul>
              </div>
              
              <div className="analysis-card cons glass">
                <div className="card-header">
                  <AlertCircle color="#ef4444" />
                  <h3>Risk Factors</h3>
                </div>
                <ul>
                  {pros_cons?.cons ? pros_cons.cons.split('\n').map((c, i) => (
                    <li key={i}>{c}</li>
                  )) : <li>No major risk factors identified.</li>}
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>
      
      <style>{`
        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          width: 100vw;
          height: 100vh;
          background: rgba(2, 6, 23, 0.8);
          backdrop-filter: blur(8px);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
          padding: 2rem;
        }
        .modal-content {
          width: 100%;
          max-width: 1000px;
          max-height: 90vh;
          overflow-y: auto;
          position: relative;
          padding: 2.5rem;
          display: flex;
          flex-direction: column;
          gap: 2rem;
        }
        .modal-content.loading {
          align-items: center;
          justify-content: center;
          height: 400px;
        }
        .close-btn {
          position: absolute;
          top: 1.5rem;
          right: 1.5rem;
          background: transparent;
          border: none;
          color: var(--text-secondary);
          cursor: pointer;
          transition: color 0.2s;
        }
        .close-btn:hover { color: white; }
        
        .company-branding {
          display: flex;
          align-items: center;
          gap: 1.5rem;
        }
        .modal-logo {
          width: 64px;
          height: 64px;
          border-radius: 12px;
          object-fit: contain;
          background: white;
          padding: 4px;
        }
        .modal-logo-placeholder {
          width: 64px;
          height: 64px;
          border-radius: 12px;
          background: var(--primary);
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 2rem;
          font-weight: 800;
        }
        .symbol-large {
          font-family: monospace;
          color: var(--primary);
          font-weight: 600;
          letter-spacing: 1px;
        }
        
        .modal-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          border-bottom: 1px solid var(--border);
          padding-bottom: 2rem;
        }
        .header-links {
          display: flex;
          gap: 1rem;
        }
        .header-links a {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          color: var(--text-secondary);
          text-decoration: none;
          font-size: 0.875rem;
          padding: 0.5rem 1rem;
          border-radius: 99px;
          border: 1px solid var(--border);
          transition: all 0.2s;
        }
        .header-links a:hover {
          background: rgba(255, 255, 255, 0.05);
          color: white;
        }

        .modal-tabs {
          display: flex;
          gap: 2rem;
          border-bottom: 1px solid var(--border);
        }
        .modal-tabs button {
          background: transparent;
          border: none;
          color: var(--text-secondary);
          padding: 1rem 0;
          font-weight: 600;
          cursor: pointer;
          position: relative;
        }
        .modal-tabs button.active {
          color: var(--primary);
        }
        .modal-tabs button.active::after {
          content: '';
          position: absolute;
          bottom: -1px;
          left: 0;
          width: 100%;
          height: 2px;
          background: var(--primary);
          box-shadow: 0 0 10px var(--primary-glow);
        }

        .overview-grid, .financials-grid, .analysis-grid {
          display: grid;
          gap: 1.5rem;
        }
        .overview-grid { grid-template-columns: 1fr 1.5fr; }
        .financials-grid { grid-template-columns: 1fr 1fr; }
        .analysis-grid { grid-template-columns: 1fr 1fr; }

        .score-radar-section { padding: 1.5rem; }
        .radar-container { display: flex; justify-content: center; }
        
        .stats-mini-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 1rem;
          margin-bottom: 1.5rem;
        }
        .mini-card {
          padding: 1rem;
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
        }
        .mini-card label {
          font-size: 0.75rem;
          color: var(--text-secondary);
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }
        .mini-card span {
          font-size: 1.25rem;
          font-weight: 700;
        }
        .label-badge {
          padding: 0.2rem 0.6rem;
          border-radius: 4px;
          font-size: 0.875rem;
          width: fit-content;
        }
        .label-badge.healthy { background: rgba(16, 185, 129, 0.2); color: #10b981; }
        .label-badge.stable { background: rgba(245, 158, 11, 0.2); color: #f59e0b; }
        .label-badge.at-risk { background: rgba(239, 68, 68, 0.2); color: #ef4444; }

        .about-section, .prediction-section { padding: 1.5rem; }
        .about-section p, .prediction-section p { font-size: 0.875rem; color: var(--text-secondary); line-height: 1.8; }
        .prediction-header { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem; }
        .duration-text { color: var(--accent); font-weight: 800; }
        
        .chart-card { padding: 1.5rem; }
        .chart-container { margin-top: 1rem; }

        .analysis-card { padding: 2rem; }
        .analysis-card .card-header { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.5rem; }
        .analysis-card ul { list-style: none; display: flex; flex-direction: column; gap: 1rem; }
        .analysis-card li { font-size: 0.9375rem; color: var(--text-secondary); position: relative; padding-left: 1.5rem; }
        .analysis-card li::before {
          content: '→';
          position: absolute;
          left: 0;
          color: var(--primary);
        }

        .tooltip-label { display: flex; align-items: center; gap: 0.3rem; cursor: help; }

        .spinner {
          width: 40px;
          height: 40px;
          border: 4px solid var(--border);
          border-top-color: var(--primary);
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin-bottom: 1rem;
        }
        @keyframes spin { to { transform: rotate(360deg); } }

        @media (max-width: 768px) {
          .modal-content { padding: 1.5rem; }
          .overview-grid, .financials-grid, .analysis-grid { grid-template-columns: 1fr; }
          .stats-mini-grid { grid-template-columns: 1fr 1fr; }
          .modal-tabs { overflow-x: auto; white-space: nowrap; padding-bottom: 0.5rem; }
          .company-branding { flex-direction: column; align-items: flex-start; gap: 1rem; }
          .header-links { flex-wrap: wrap; }
          h2 { font-size: 1.5rem; }
        }
      `}</style>
    </div>
  );
};

export default CompanyDetailModal;
