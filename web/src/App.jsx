import React, { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, NavLink, Navigate } from 'react-router-dom'
import { LayoutDashboard, TrendingUp, BarChart3, Settings as SettingsIcon, Briefcase, Activity, ChevronDown, ChevronUp, Loader, Grid, List, DollarSign, Globe, Package, ArrowLeftRight, Grid3X3, IndianRupee, Zap, Rocket, Shield, Wallet, Newspaper, PieChart, Crown, BrainCircuit } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import './index.css'

// Import our specific page components
import { DashboardOverview, Portfolio, RiskAnalysis, Settings, SectorHeatmap, SectorIndices, DebtFunds, MacroDashboard, CommodityTracker, ForexMonitor, CorrelationMatrix, Nifty500Heatmap, MomentumAnalysis, GrowthAnalysis, RiskAdjustedAnalysis, IncomeAnalysis, MarketNews, AllocationAdvisor, BacktestView, IndiaMutualFunds, LegendaryPortfolios, TickerDetailProvider, useTickerDetail, AlphaAcademy, YouthAlpha, AlphaGuide, Sparkline } from './pages/Views'

const API_BASE = "http://localhost:8001/api"

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true };
  }
  componentDidCatch(error, errorInfo) {
    this.setState({ error: error, errorInfo: errorInfo });
    console.error("ErrorBoundary caught:", error, errorInfo);
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '2rem', color: 'white', background: '#331111', height: '100%', overflow: 'auto' }}>
          <h2>React Crashed</h2>
          <pre style={{ whiteSpace: 'pre-wrap', color: '#ffaaaa' }}>{this.state.error && this.state.error.toString()}</pre>
          <pre style={{ whiteSpace: 'pre-wrap', color: '#ffdddd', fontSize: '0.8rem', marginTop: '1rem' }}>{this.state.errorInfo && this.state.errorInfo.componentStack}</pre>
        </div>
      );
    }
    return this.props.children;
  }
}

function MetricBox({ label, value, isMagic }) {
  return (
    <div style={{
      padding: '0.8rem',
      background: 'rgba(255,255,255,0.03)',
      borderRadius: '8px',
      borderLeft: isMagic ? '3px solid var(--profit-green)' : '3px solid transparent'
    }}>
      <div style={{ fontSize: '0.8rem', color: isMagic ? 'var(--profit-green)' : 'var(--text-muted)', marginBottom: '0.3rem' }}>{label}</div>
      <div style={{ fontWeight: 600, fontSize: '1.1rem' }}>{value}</div>
    </div>
  )
}

function formatBillion(val) {
  if (val === null || val === undefined) return 'N/A';
  return `$${(val / 1e9).toFixed(2)}B`;
}

// Simple SVG Line Chart to avoid Recharts/D3 dependency crashes
const SimpleSvgChart = ({ data, width = 700, height = 300 }) => {
  if (!data || data.length === 0) return null;
  const padding = 20;
  const innerWidth = width - padding * 2;
  const innerHeight = height - padding * 2;
  if (innerHeight <= 0 || innerWidth <= 0) return null;

  const minPrice = Math.min(...data.map(d => d.close));
  const maxPrice = Math.max(...data.map(d => d.close));
  const range = maxPrice - minPrice || 1;

  const points = data.map((d, i) => {
    const x = padding + (i / (data.length - 1)) * innerWidth;
    const y = padding + innerHeight - ((d.close - minPrice) / range) * innerHeight;
    return `${x},${y}`;
  });

  const pathD = `M ${points.join(' L ')}`;

  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
      <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} stroke="rgba(255,255,255,0.1)" />
      <line x1={padding} y1={padding} x2={padding} y2={height - padding} stroke="rgba(255,255,255,0.1)" />
      <path d={pathD} fill="none" stroke="var(--accent-blue)" strokeWidth="3" strokeLinejoin="round" />
      <text x={padding + 10} y={padding + 5} fill="var(--text-muted)" fontSize="12" dominantBaseline="hanging">Max: ${maxPrice.toFixed(2)}</text>
      <text x={padding + 10} y={height - padding - 5} fill="var(--text-muted)" fontSize="12" dominantBaseline="auto">Min: ${minPrice.toFixed(2)}</text>
      <text x={width - padding - 10} y={height - padding + 15} fill="var(--text-muted)" fontSize="10" textAnchor="end">{data[data.length - 1].date}</text>
      <text x={padding + 5} y={height - padding + 15} fill="var(--text-muted)" fontSize="10" textAnchor="start">{data[0].date}</text>
    </svg>
  );
};

function StockHistoryChart({ ticker, metrics }) {
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [period, setPeriod] = useState('5y')

  useEffect(() => {
    setLoading(true)
    fetch(`${API_BASE}/stock/${ticker}/history?period=${period}`)
      .then(res => res.json())
      .then(data => {
        setHistory(data)
        setLoading(false)
      })
      .catch(err => {
        console.error("Failed to fetch history:", err)
        setLoading(false)
      })
  }, [ticker, period])

  return (
    <div style={{ padding: '1.5rem', background: 'rgba(0,0,0,0.2)', borderRadius: '8px', marginTop: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
        <h3 style={{ margin: 0, fontSize: '1.1rem' }}>{ticker} Price History</h3>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          {['1mo', '1y', '5y', 'max'].map(p => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              style={{
                background: period === p ? 'var(--accent-blue)' : 'transparent',
                border: `1px solid ${period === p ? 'transparent' : 'var(--border-glass)'}`,
                color: 'white',
                padding: '0.2rem 0.8rem',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '0.85rem'
              }}
            >
              {p.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      <div style={{ display: 'flex', gap: '2rem' }}>
        {/* Chart Section */}
        <div style={{ flex: 2, height: '300px' }}>
          {loading ? (
            <div style={{ display: 'flex', height: '100%', alignItems: 'center', justifyContent: 'center' }}><Loader className="animate-spin" /></div>
          ) : history.length > 0 ? (
            <SimpleSvgChart data={history} width={700} height={300} />
          ) : (
            <div style={{ display: 'flex', height: '100%', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>No historical data available.</div>
          )}
        </div>

        {/* Metrics Section */}
        <div style={{ flex: 1, paddingLeft: '2rem', borderLeft: '1px solid var(--border-glass)' }}>
          <h4 style={{ margin: '0 0 1rem 0', color: 'var(--text-muted)', fontSize: '0.9rem' }}>CURRENT PARAMETERS</h4>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <MetricBox label="Earnings Yield" value={`${(metrics?.ey * 100).toFixed(2)}%`} isMagic={true} />
            <MetricBox label="Return on Cap." value={`${(metrics?.roc * 100).toFixed(2)}%`} isMagic={true} />
            <MetricBox label="EBIT" value={formatBillion(metrics?.ebit)} />
            <MetricBox label="Enterprise Val." value={formatBillion(metrics?.ev)} />
            <MetricBox label="Curr. Assets" value={formatBillion(metrics?.ca)} />
            <MetricBox label="Curr. Liab." value={formatBillion(metrics?.cl)} />
            <MetricBox label="Net Working Cap." value={formatBillion(metrics?.nwc)} />
            <MetricBox label="Net Fixed Assets" value={formatBillion(metrics?.nfa)} />
          </div>
        </div>
      </div>
    </div>
  )
}

function Screener() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [expandedRow, setExpandedRow] = useState(null)
  const { openTicker } = useTickerDetail()

  useEffect(() => {
    fetch(`${API_BASE}/screener`)
      .then(res => res.json())
      .then(data => {
        setData(data)
        setLoading(false)
      })
      .catch(err => {
        console.error("Failed to fetch screener data:", err)
        setLoading(false)
      })
  }, [])

  const [scannerData, setScannerData] = useState([])
  const [scannerLoading, setScannerLoading] = useState(true)

  useEffect(() => {
    fetch(`${API_BASE}/ai/scanner`)
      .then(res => res.json())
      .then(d => { setScannerData(d); setScannerLoading(false) })
      .catch(() => setScannerLoading(false))
  }, [])

  const groupedData = data.reduce((acc, item) => {
    const region = item.region || 'Other';
    if (!acc[region]) acc[region] = [];
    acc[region].push(item);
    return acc;
  }, {});

  const regions = ['US', 'Europe', 'India', 'Other'];

  return (
    <>
      <header>
        <h1>Global Asset Screener</h1>
        <p className="subtitle">Powered by the Magic Formula (Greenblatt Strategy) + Contrarian Scanner</p>
      </header>

      {/* High-Level Metrics */}
      <div className="dashboard-grid">
        <div className="metric-card glass-panel">
          <span className="label">Total Assets Analyzed</span>
          <span className="value">{loading ? '-' : data.length}</span>
          <span className="metric-positive">{loading ? '' : `${Object.keys(groupedData).length} Markets Tracked`}</span>
        </div>
        <div className="metric-card glass-panel">
          <span className="label">Contrarian Signal</span>
          <span className="value">{scannerLoading ? 'Calculating...' : (scannerData.length > 0 ? 'Active' : 'Neutral')}</span>
          <span className="metric-positive">Deep Value Troughs Detected</span>
        </div>
        <div className="metric-card glass-panel">
          <span className="label">Growth Sweet Spot</span>
          <span className="value">12-35% CAGR</span>
          <span style={{ color: 'var(--accent-blue)', fontSize: '0.9rem' }}>Optimal Stability Range</span>
        </div>
      </div>

      {loading ? (
        <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
          <div className="loader" style={{ margin: '0 auto 1rem' }}></div>
          <h3>Analyzing Global Markets...</h3>
        </div>
      ) : (
        regions.map(region => {
          const regionAssets = groupedData[region] || [];
          const regionalScanner = scannerData.find(s => s.region === region);
          if (regionAssets.length === 0) return null;

          return (
            <div key={region} className="glass-panel" style={{ padding: '1.5rem', marginBottom: '2rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <h2 style={{ fontSize: '1.2rem', margin: 0, fontWeight: 700, color: 'var(--accent-blue)' }}>{region} Opportunities</h2>
                    {regionalScanner && (
                        <span style={{ background: 'rgba(59, 130, 246, 0.1)', color: 'var(--accent-blue)', padding: '0.3rem 0.6rem', borderRadius: '6px', fontSize: '0.75rem', fontWeight: 600 }}>
                            Recovery: {regionalScanner.recovery_estimate}
                        </span>
                    )}
                </div>
                <div style={{ display: 'flex', gap: '1rem' }}>
                  <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>{regionAssets.length} Assets Found</span>
                </div>
              </div>

              <div className="data-table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Rank</th>
                      <th>Asset</th>
                      <th>Sector</th>
                      <th>Trend (30D)</th>
                      <th>Earnings Yield</th>
                      <th>EY Rank</th>
                      <th>Return on Capital</th>
                      <th>ROC Rank</th>
                      <th>5Y CAGR</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {regionAssets.map((row, idx) => (
                      <React.Fragment key={row.ticker}>
                        <tr
                          style={{ cursor: 'pointer' }}
                          onClick={() => setExpandedRow(expandedRow === row.ticker ? null : row.ticker)}
                        >
                          <td><span className="rank-badge">#{idx + 1}</span></td>
                          <td>
                            <div 
                              style={{ display: 'flex', flexDirection: 'column', cursor: 'pointer' }}
                              onClick={(e) => { e.stopPropagation(); openTicker(row.ticker); }}
                            >
                              <span style={{ fontWeight: 600, color: 'var(--accent-blue)', textDecoration: 'underline' }}>{row.ticker}</span>
                              <span style={{ fontSize: 0.85, color: 'var(--text-muted)' }}>{row.name}</span>
                            </div>
                          </td>
                          <td><span style={{ background: 'rgba(255,255,255,0.05)', padding: '0.3rem 0.6rem', borderRadius: '6px', fontSize: '0.85rem' }}>{row.sector}</span></td>
                          <td>
                            <Sparkline data={row.sparkline} color={row.ey >= 0 ? 'var(--profit-green)' : '#ef4444'} width={80} height={24} />
                          </td>
                          <td style={{ fontWeight: 600 }}>{row.ey !== null ? (row.ey * 100).toFixed(2) + '%' : 'N/A'}</td>
                          <td style={{ color: 'var(--text-muted)' }}>{row.eyRank}</td>
                          <td style={{ fontWeight: 600, color: 'var(--profit-green)' }}>{row.roc !== null ? (row.roc * 100).toFixed(2) + '%' : 'N/A'}</td>
                          <td style={{ color: 'var(--text-muted)' }}>{row.rocRank}</td>
                          <td style={{ fontWeight: 600, color: 'white' }}>{row.cagr}</td>
                          <td>
                            {expandedRow === row.ticker ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                          </td>
                        </tr>
                        {expandedRow === row.ticker && (
                          <tr style={{ background: 'rgba(255,255,255,0.02)' }}>
                            <td colSpan="9" style={{ borderBottom: '1px solid var(--border-glass)' }}>
                              <StockHistoryChart ticker={row.ticker} metrics={row} />
                            </td>
                          </tr>
                        )}
                      </React.Fragment>
                    ))}
                  </tbody>
                </table>
              </div>
              
              {/* Regional Investor Footer */}
              {regionalScanner && (
                  <div style={{ marginTop: '1.5rem', padding: '1rem', background: 'rgba(0,0,0,0.1)', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.03)' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                         <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center' }}>
                            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                <Shield size={14} /> Expert Benchmark:
                            </div>
                            <span style={{ fontSize: '0.9rem', fontWeight: 600, color: '#e2e8f0' }}>{regionalScanner.investor_benchmark}</span>
                         </div>
                         <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                            Recovery Confidence: <span style={{ color: 'var(--profit-green)', fontWeight: 700 }}>High (Z-Score Trough)</span>
                         </div>
                      </div>
                  </div>
              )}
            </div>
          );
        })
      )}

      {/* Legend & Definitions Section */}
      <div className="glass-panel" style={{ padding: '2rem', marginTop: '2rem' }}>
        <h3 style={{ marginTop: 0, fontSize: '1.2rem' }}>Metric Definitions {"&"} Legend</h3>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
          Parameters highlighted in <span style={{ color: 'var(--profit-green)', fontWeight: 'bold' }}>Green</span> are the core components of Joel Greenblatt's Magic Formula ("The Little Book That Beats the Market").
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem' }}>

          <div>
            <h4 style={{ color: 'var(--profit-green)', margin: '0 0 0.5rem 0' }}>EY - Earnings Yield</h4>
            <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
              <strong>Definition:</strong> Shows how much a business earns relative to its purchase price (EBIT / Enterprise Value). It's a measure of value.<br /><br />
              <strong>Example:</strong> If a business costs $100 and earns $10 a year, the Earnings Yield is 10%.
            </div>
          </div>

          <div>
            <h4 style={{ color: 'var(--profit-green)', margin: '0 0 0.5rem 0' }}>ROC - Return on Capital</h4>
            <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
              <strong>Definition:</strong> Shows how well a company turns capital into profit (EBIT / (Net Working Capital + Net Fixed Assets)). It's a measure of quality.<br /><br />
              <strong>Example:</strong> Using $10M in factories and inventory to generate $5M profit yields a 50% ROC.
            </div>
          </div>

          <div>
            <h4 style={{ margin: '0 0 0.5rem 0', color: 'white' }}>EBIT - Earnings Before Interest & Taxes</h4>
            <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
              <strong>Definition:</strong> Operating profit. We use this instead of net income to evaluate the business regardless of tax rates and debt levels.
            </div>
          </div>

          <div>
            <h4 style={{ margin: '0 0 0.5rem 0', color: 'white' }}>EV - Enterprise Value</h4>
            <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
              <strong>Definition:</strong> Total theoretical takeover price of the company. It includes market cap plus debt, minus cash.
            </div>
          </div>

          <div>
            <h4 style={{ margin: '0 0 0.5rem 0', color: 'white' }}>NWC / CA / CL</h4>
            <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
              <strong>Definition:</strong> Net Working Capital (NWC) equals Current Assets (CA) minus Current Liabilities (CL). Shows short-term financial health.
            </div>
          </div>

          <div>
            <h4 style={{ margin: '0 0 0.5rem 0', color: 'white' }}>NFA - Net Fixed Assets</h4>
            <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
              <strong>Definition:</strong> Capital tied up in long-term, tangible assets like property, buildings, and equipment.
            </div>
          </div>

        </div>
      </div >
    </>
  )
}

function App() {
  return (
    <BrowserRouter>
      <TickerDetailProvider>
        <div className="app-container">
        {/* Sidebar Navigation */}
        <aside className="sidebar">
          <div className="logo glass-panel" style={{ padding: '1rem', border: 'none', background: 'transparent', boxShadow: 'none' }}>
            <Briefcase className="logo-icon" size={28} />
            <span>ALPHA FUND</span>
          </div>

          <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginTop: '2rem' }}>
            <NavLink to="/dashboard" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
              <LayoutDashboard size={20} /> Dashboard
            </NavLink>
            <NavLink to="/screener" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
              <BarChart3 size={20} /> Magic Screener
            </NavLink>
            <NavLink to="/portfolio" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
              <TrendingUp size={20} /> Portfolio
            </NavLink>
            <NavLink to="/risk" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
              <Activity size={20} /> Risk Analysis
            </NavLink>
            <NavLink to="/sectors" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
              <Grid size={20} /> Sector Heatmap
            </NavLink>
            <NavLink to="/indices" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
              <List size={20} /> Sector Indices
            </NavLink>
            <NavLink to="/debt-funds" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
              <DollarSign size={20} /> Debt Funds
            </NavLink>
            <NavLink to="/macro" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
              <Globe size={20} /> Market Overview
            </NavLink>
            <NavLink to="/commodities" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
              <Package size={20} /> Commodities
            </NavLink>
            <NavLink to="/forex" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
              <ArrowLeftRight size={20} /> Forex
            </NavLink>
            <NavLink to="/correlation" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
              <Grid3X3 size={20} /> Correlation
            </NavLink>
            <NavLink to="/nifty500" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
              <IndianRupee size={20} /> Nifty 500
            </NavLink>
            <NavLink to="/india-funds" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
              <TrendingUp size={20} /> India Mutual Funds
            </NavLink>

            <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.1em', padding: '1rem 1.2rem 0.3rem', marginTop: '0.5rem' }}>Analysis</div>
            <NavLink to="/allocation" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
              <PieChart size={20} /> Allocation Advisor
            </NavLink>
            <NavLink to="/legendary" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
              <Crown size={20} /> Legendary Portfolios
            </NavLink>
            <NavLink to="/backtest" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
              <Activity size={20} /> Portfolio Backtest
            </NavLink>
            <NavLink to="/momentum" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
              <Zap size={20} /> Momentum
            </NavLink>
            <NavLink to="/growth" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
              <Rocket size={20} /> Growth
            </NavLink>
            <NavLink to="/risk-adjusted" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
              <Shield size={20} /> Risk-Adjusted
            </NavLink>
            <NavLink to="/income" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
              <Wallet size={20} /> Income
            </NavLink>
            <NavLink to="/news" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
              <Newspaper size={20} /> Market News
            </NavLink>

            <NavLink to="/settings" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} style={{ marginTop: '0.5rem' }}>
              <SettingsIcon size={20} /> Command Center
            </NavLink>
            
            <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.1em', padding: '1rem 1.2rem 0.3rem', marginTop: '0.5rem' }}>Education & Tools</div>
            <NavLink to="/academy" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
              <Crown size={20} /> Alpha Academy
            </NavLink>
            <NavLink to="/youth" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
              <Rocket size={20} /> Youth Alpha
            </NavLink>
            <NavLink to="/guide" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} style={{ borderTop: '1px solid var(--border-glass)', paddingTop: '0.8rem', marginTop: '0.5rem' }}>
              <BrainCircuit size={20} /> Alpha Guide
            </NavLink>
          </nav>
        </aside>

        {/* Main Content Area */}
        <main className="main-content">
          <ErrorBoundary>
            <Routes>
              <Route path="/" element={<Navigate to="/screener" replace />} />
              <Route path="/dashboard" element={<DashboardOverview />} />
              <Route path="/screener" element={<Screener />} />
              <Route path="/portfolio" element={<Portfolio />} />
              <Route path="/risk" element={<RiskAnalysis />} />
              <Route path="/sectors" element={<SectorHeatmap />} />
              <Route path="/indices" element={<SectorIndices />} />
              <Route path="/debt-funds" element={<DebtFunds />} />
              <Route path="/macro" element={<MacroDashboard />} />
              <Route path="/commodities" element={<CommodityTracker />} />
              <Route path="/forex" element={<ForexMonitor />} />
              <Route path="/correlation" element={<CorrelationMatrix />} />
              <Route path="/nifty500" element={<Nifty500Heatmap />} />
              <Route path="/india-funds" element={<IndiaMutualFunds />} />
              <Route path="/allocation" element={<AllocationAdvisor />} />
              <Route path="/legendary" element={<LegendaryPortfolios />} />
              <Route path="/backtest" element={<BacktestView />} />
              <Route path="/momentum" element={<MomentumAnalysis />} />
              <Route path="/growth" element={<GrowthAnalysis />} />
              <Route path="/risk-adjusted" element={<RiskAdjustedAnalysis />} />
              <Route path="/income" element={<IncomeAnalysis />} />
              <Route path="/news" element={<MarketNews />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/academy" element={<AlphaAcademy />} />
              <Route path="/youth" element={<YouthAlpha />} />
              <Route path="/guide" element={<AlphaGuide />} />
            </Routes>
          </ErrorBoundary>
        </main>
        </div>
      </TickerDetailProvider>
    </BrowserRouter >
  )
}

export default App
