import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Activity, 
  BarChart3, 
  Building2, 
  Search, 
  ArrowUpRight, 
  ArrowDownRight,
  ShieldCheck,
  TrendingUp,
  Filter
} from 'lucide-react';
import './App.css';

const API_BASE = 'http://localhost:8000/api';

function App() {
  const [companies, setCompanies] = useState([]);
  const [sectors, setSectors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSector, setSelectedSector] = useState('All');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      // Try fetching from 127.0.0.1 if localhost fails, common in some environments
      const hosts = ['http://127.0.0.1:8000', 'http://localhost:8000'];
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
          console.warn(`Connection to ${host} failed, trying next...`);
        }
      }
      
      if (!success) {
        throw new Error("Unable to connect to financial intelligence engine. Ensure the backend is running at port 8000.");
      }
    } catch (error) {
      console.error("Error fetching data:", error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const filteredCompanies = companies.filter(c => {
    const matchesSearch = c.company_name.toLowerCase().includes(searchTerm.toLowerCase()) || 
                         c.id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSector = selectedSector === 'All' || c.sector === selectedSector;
    return matchesSearch && matchesSector;
  });

  const getScoreColor = (score) => {
    if (score >= 80) return '#10b981';
    if (score >= 60) return '#fbbf24';
    return '#f43f5e';
  };

  return (
    <div className="app-container">
      {/* Navbar */}
      <nav className="navbar animate-fade-in">
        <div className="logo">
          <Activity size={32} className="accent-icon" />
          <span>NIFTY 100 <span className="intel">INTEL</span></span>
        </div>
        <div className="nav-actions">
          <div className="search-box glass">
            <Search size={18} />
            <input 
              type="text" 
              placeholder="Search symbol or company..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>
      </nav>

      <header className="hero animate-fade-in">
        <h1>Nifty 100 Intelligence</h1>
        <p>AI-driven financial health analysis and market intelligence for India's top companies.</p>
      </header>

      {error && (
        <div className="error-alert animate-fade-in">
          <ShieldCheck size={20} />
          <span>{error}</span>
          <button onClick={fetchData}>Retry</button>
        </div>
      )}

      {/* Overview Cards */}
      <section className="stats-grid animate-fade-in">
        <div className="stat-card glass">
          <div className="stat-info">
            <label>Avg. Market Score</label>
            <h3>{sectors.length > 0 ? (sectors.reduce((acc, s) => acc + s.avg_score, 0) / sectors.length).toFixed(1) : '0'}</h3>
          </div>
          <TrendingUp className="stat-icon" />
        </div>
        <div className="stat-card glass">
          <div className="stat-info">
            <label>Companies Tracked</label>
            <h3>{companies.length}</h3>
          </div>
          <Building2 className="stat-icon" />
        </div>
        <div className="stat-card glass">
          <div className="stat-info">
            <label>Sectors Analyzed</label>
            <h3>{sectors.length}</h3>
          </div>
          <BarChart3 className="stat-icon" />
        </div>
      </section>

      {/* Sectors Horizontal Scroll */}
      <section className="sectors-section animate-fade-in">
        <div className="section-header">
          <h2>Sector Performance</h2>
          <div className="filter-chip-group">
            <button 
              className={`filter-chip ${selectedSector === 'All' ? 'active' : ''}`}
              onClick={() => setSelectedSector('All')}
            >
              All
            </button>
            {sectors.map(s => (
              <button 
                key={s.sector} 
                className={`filter-chip ${selectedSector === s.sector ? 'active' : ''}`}
                onClick={() => setSelectedSector(s.sector)}
              >
                {s.sector}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Company Table */}
      <section className="table-section animate-fade-in">
        <div className="glass table-container">
          <table>
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Company Name</th>
                <th>Sector</th>
                <th>Market Cap</th>
                <th>Health Score</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan="6" align="center">Loading intelligence data...</td></tr>
              ) : filteredCompanies.map(company => (
                <tr key={company.id}>
                  <td><span className="symbol-badge">{company.id}</span></td>
                  <td className="company-name">{company.company_name}</td>
                  <td><span className="sector-tag">{company.sector || 'N/A'}</span></td>
                  <td>₹{company.market_cap ? (company.market_cap / 10000000).toFixed(1) + ' Cr' : 'N/A'}</td>
                  <td>
                    <div className="score-wrapper">
                      <div className="score-bar-bg">
                        <div 
                          className="score-bar-fill" 
                          style={{ 
                            width: `${company.latest_score?.overall_score || 0}%`,
                            backgroundColor: getScoreColor(company.latest_score?.overall_score || 0)
                          }}
                        ></div>
                      </div>
                      <span className="score-val">{company.latest_score?.overall_score || 'N/A'}</span>
                    </div>
                  </td>
                  <td>
                    <button className="view-btn">
                      <ArrowUpRight size={16} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <footer className="footer animate-fade-in">
        <p>&copy; 2026 Nifty 100 Intel Engine. Data powered by internal AI scoring systems.</p>
      </footer>
    </div>
  );
}

export default App;
