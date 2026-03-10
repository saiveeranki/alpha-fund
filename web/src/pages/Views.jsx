import React, { useState, useEffect } from 'react'
import { LayoutDashboard, TrendingUp, AlertTriangle, PlayCircle, Grid } from 'lucide-react'
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend, BarChart, Bar } from 'recharts'

// Mock Data
export const magicFormulaData = [
    { rank: 1, ticker: 'TCS.NS', name: 'Tata Consultancy Services', ey: '7.27%', roc: '62.02%', eyRank: 4, rocRank: 2, sector: 'Technology' },
    { rank: 2, ticker: 'LVMUY', name: 'LVMH Moët Hennessy', ey: '20.25%', roc: '15.99%', eyRank: 1, rocRank: 9, sector: 'Consumer Cyclical' },
    { rank: 3, ticker: 'AAPL', name: 'Apple Inc.', ey: '3.41%', roc: '68.72%', eyRank: 13, rocRank: 1, sector: 'Technology' },
    { rank: 4, ticker: 'META', name: 'Meta Platforms', ey: '5.30%', roc: '26.87%', eyRank: 8, rocRank: 6, sector: 'Communication Services' },
    { rank: 5, ticker: 'MC.PA', name: 'LVMH (Paris)', ey: '6.05%', roc: '15.99%', eyRank: 6, rocRank: 9, sector: 'Consumer Cyclical' },
]

// SVG Donut Chart component (no Recharts dependency)
function SvgDonut({ data, size = 200, innerRadius = 60, outerRadius = 90 }) {
    if (!data || data.length === 0) return null
    const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#6b7280', '#ec4899', '#14b8a6']
    const total = data.reduce((s, d) => s + d.percent, 0) || 1
    const cx = size / 2, cy = size / 2
    let startAngle = -90
    const paths = data.map((d, i) => {
        const angle = (d.percent / total) * 360
        const endAngle = startAngle + angle
        const largeArc = angle > 180 ? 1 : 0
        const rad1 = (startAngle * Math.PI) / 180
        const rad2 = (endAngle * Math.PI) / 180
        const x1o = cx + outerRadius * Math.cos(rad1)
        const y1o = cy + outerRadius * Math.sin(rad1)
        const x2o = cx + outerRadius * Math.cos(rad2)
        const y2o = cy + outerRadius * Math.sin(rad2)
        const x1i = cx + innerRadius * Math.cos(rad2)
        const y1i = cy + innerRadius * Math.sin(rad2)
        const x2i = cx + innerRadius * Math.cos(rad1)
        const y2i = cy + innerRadius * Math.sin(rad1)
        const path = [
            `M ${x1o} ${y1o}`,
            `A ${outerRadius} ${outerRadius} 0 ${largeArc} 1 ${x2o} ${y2o}`,
            `L ${x1i} ${y1i}`,
            `A ${innerRadius} ${innerRadius} 0 ${largeArc} 0 ${x2i} ${y2i}`,
            'Z'
        ].join(' ')
        startAngle = endAngle
        return <path key={i} d={path} fill={COLORS[i % COLORS.length]} opacity={0.85}
            style={{ transition: 'opacity 0.2s' }}
            onMouseEnter={e => e.currentTarget.style.opacity = 1}
            onMouseLeave={e => e.currentTarget.style.opacity = 0.85} />
    })
    return (
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
            <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>{paths}</svg>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                {data.map((d, i) => (
                    <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem' }}>
                        <div style={{ width: 10, height: 10, borderRadius: 3, background: COLORS[i % COLORS.length] }} />
                        <span style={{ color: 'var(--text-muted)' }}>{d.category || d.sector}</span>
                        <span style={{ fontWeight: 700 }}>{d.percent}%</span>
                    </div>
                ))}
            </div>
        </div>
    )
}

export function DashboardOverview() {
    const [data, setData] = useState(null)
    const [loading, setLoading] = useState(true)
    const API = 'http://127.0.0.1:8001'

    useEffect(() => {
        fetch(`${API}/api/dashboard`)
            .then(r => r.json())
            .then(d => { setData(d); setLoading(false) })
            .catch(() => setLoading(false))
    }, [])

    const changeColor = (v) => v > 0 ? 'var(--profit-green)' : v < 0 ? '#ef4444' : 'var(--text-muted)'
    const fmtPct = (v) => v != null ? `${v > 0 ? '+' : ''}${v}%` : 'N/A'

    if (loading) return (
        <>
            <header><h1>Executive Dashboard</h1><p className="subtitle">Loading portfolio data...</p></header>
            <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                <LayoutDashboard size={48} style={{ color: 'var(--accent-blue)', opacity: 0.5, marginBottom: '1rem' }} />
                <h2>Analyzing your portfolio...</h2>
            </div>
        </>
    )

    if (!data || data.holdings_count === 0) return (
        <>
            <header><h1>Executive Dashboard</h1><p className="subtitle">Your portfolio at a glance.</p></header>
            <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center' }}>
                <LayoutDashboard size={48} style={{ color: 'var(--accent-blue)', opacity: 0.4, marginBottom: '1rem' }} />
                <h2 style={{ fontSize: '1.3rem', marginBottom: '0.5rem' }}>No holdings yet</h2>
                <p style={{ color: 'var(--text-muted)' }}>Add ETFs and assets in the <a href="/portfolio" style={{ color: 'var(--accent-blue)' }}>Portfolio</a> page to see your live dashboard.</p>
            </div>
            {/* Still show market pulse */}
            {data && data.market_pulse && data.market_pulse.length > 0 && (
                <div className="glass-panel" style={{ padding: '1.5rem', marginTop: '1.5rem' }}>
                    <h3 style={{ margin: '0 0 1rem 0', fontSize: '1rem', color: 'var(--text-muted)' }}>📈 Market Pulse</h3>
                    <div className="dashboard-grid">
                        {data.market_pulse.map(m => (
                            <div key={m.name} className="metric-card glass-panel">
                                <span className="label">{m.name}</span>
                                <span className="value">{m.value?.toLocaleString()}</span>
                                <span style={{ color: changeColor(m.change), fontWeight: 600 }}>{fmtPct(m.change)}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </>
    )

    return (
        <>
            <header>
                <h1>Executive Dashboard</h1>
                <p className="subtitle">Real-time portfolio overview — {data.holdings_count} holdings tracked.</p>
            </header>

            {/* Top Metric Cards */}
            <div className="dashboard-grid">
                <div className="metric-card glass-panel" style={{ borderLeft: '4px solid var(--accent-blue)' }}>
                    <span className="label">Total Invested</span>
                    <span className="value">${data.total_value?.toLocaleString()}</span>
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>{data.holdings_count} holdings</span>
                </div>
                <div className="metric-card glass-panel" style={{ borderLeft: `4px solid ${data.daily_pnl >= 0 ? 'var(--profit-green)' : '#ef4444'}` }}>
                    <span className="label">Daily P&L</span>
                    <span className="value" style={{ color: changeColor(data.daily_pnl) }}>
                        {data.daily_pnl >= 0 ? '+' : ''}${data.daily_pnl?.toLocaleString()}
                    </span>
                    <span style={{ color: changeColor(data.daily_pnl_pct), fontWeight: 600, fontSize: '0.9rem' }}>{fmtPct(data.daily_pnl_pct)}</span>
                </div>
                {data.top_performers?.[0] && (
                    <div className="metric-card glass-panel" style={{ borderLeft: '4px solid var(--profit-green)' }}>
                        <span className="label">🏆 Best Today</span>
                        <span className="value" style={{ fontSize: '1.2rem' }}>{data.top_performers[0].name}</span>
                        <span style={{ color: 'var(--profit-green)', fontWeight: 600 }}>{fmtPct(data.top_performers[0].day_change)}</span>
                    </div>
                )}
                {data.worst_performers?.[0] && (
                    <div className="metric-card glass-panel" style={{ borderLeft: '4px solid #ef4444' }}>
                        <span className="label">📉 Worst Today</span>
                        <span className="value" style={{ fontSize: '1.2rem' }}>{data.worst_performers[0].name}</span>
                        <span style={{ color: '#ef4444', fontWeight: 600 }}>{fmtPct(data.worst_performers[0].day_change)}</span>
                    </div>
                )}
            </div>

            {/* Middle Row: Allocation Donut + Performers */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginTop: '1.5rem' }}>
                {/* Allocation Donut */}
                <div className="glass-panel" style={{ padding: '1.5rem' }}>
                    <h3 style={{ margin: '0 0 1rem 0', fontSize: '1rem' }}>Asset Allocation</h3>
                    {data.allocation && data.allocation.length > 0 ? (
                        <SvgDonut data={data.allocation} />
                    ) : (
                        <p style={{ color: 'var(--text-muted)' }}>Set investment amounts in Portfolio to see allocation.</p>
                    )}
                </div>

                {/* Top & Worst Performers */}
                <div className="glass-panel" style={{ padding: '1.5rem' }}>
                    <h3 style={{ margin: '0 0 1rem 0', fontSize: '1rem' }}>Today's Movers</h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                        {(data.top_performers || []).map((p, i) => (
                            <div key={p.ticker} style={{
                                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                                padding: '0.6rem 0.8rem', borderRadius: '8px',
                                background: 'rgba(16, 185, 129, 0.06)', borderLeft: '3px solid var(--profit-green)',
                            }}>
                                <div>
                                    <span style={{ fontWeight: 600, marginRight: '0.5rem' }}>{p.ticker}</span>
                                    <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>{p.name}</span>
                                </div>
                                <span style={{ color: 'var(--profit-green)', fontWeight: 700 }}>{fmtPct(p.day_change)}</span>
                            </div>
                        ))}
                        <div style={{ borderTop: '1px solid rgba(255,255,255,0.06)', margin: '0.3rem 0' }} />
                        {(data.worst_performers || []).map((p, i) => (
                            <div key={p.ticker} style={{
                                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                                padding: '0.6rem 0.8rem', borderRadius: '8px',
                                background: 'rgba(239, 68, 68, 0.06)', borderLeft: '3px solid #ef4444',
                            }}>
                                <div>
                                    <span style={{ fontWeight: 600, marginRight: '0.5rem' }}>{p.ticker}</span>
                                    <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>{p.name}</span>
                                </div>
                                <span style={{ color: '#ef4444', fontWeight: 700 }}>{fmtPct(p.day_change)}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Market Pulse */}
            {data.market_pulse && data.market_pulse.length > 0 && (
                <div className="glass-panel" style={{ padding: '1.5rem', marginTop: '1.5rem' }}>
                    <h3 style={{ margin: '0 0 1rem 0', fontSize: '1rem', color: 'var(--text-muted)' }}>📈 Market Pulse</h3>
                    <div className="dashboard-grid">
                        {data.market_pulse.map(m => (
                            <div key={m.name} className="metric-card glass-panel" style={{ borderLeft: `3px solid ${changeColor(m.change)}` }}>
                                <span className="label">{m.name}</span>
                                <span className="value" style={{ fontSize: '1.2rem' }}>{m.value?.toLocaleString()}</span>
                                <span style={{ color: changeColor(m.change), fontWeight: 600 }}>{fmtPct(m.change)}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </>
    )
}

export function Portfolio() {
    const [holdings, setHoldings] = useState([])
    const [loading, setLoading] = useState(true)
    const [searchQuery, setSearchQuery] = useState('')
    const [searchResults, setSearchResults] = useState([])
    const [searchLoading, setSearchLoading] = useState(false)
    const [expandedTicker, setExpandedTicker] = useState(null)
    const [detailData, setDetailData] = useState(null)
    const [detailLoading, setDetailLoading] = useState(false)
    const [editingTicker, setEditingTicker] = useState(null)

    const API = 'http://127.0.0.1:8001'

    const loadPortfolio = () => {
        setLoading(true)
        fetch(`${API}/api/portfolio`)
            .then(r => r.json())
            .then(d => { setHoldings(d); setLoading(false) })
            .catch(() => setLoading(false))
    }

    useEffect(() => { loadPortfolio() }, [])

    // Search tickers with debounce
    useEffect(() => {
        if (searchQuery.length < 1) { setSearchResults([]); return }
        const timer = setTimeout(() => {
            setSearchLoading(true)
            fetch(`${API}/api/tickers?q=${encodeURIComponent(searchQuery)}`)
                .then(r => r.json())
                .then(d => { setSearchResults(d); setSearchLoading(false) })
                .catch(() => setSearchLoading(false))
        }, 300)
        return () => clearTimeout(timer)
    }, [searchQuery])

    const addTicker = (ticker, name) => {
        fetch(`${API}/api/portfolio`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ticker, name }),
        })
            .then(r => r.json())
            .then(() => { setSearchQuery(''); setSearchResults([]); loadPortfolio() })
    }

    const removeTicker = (ticker) => {
        fetch(`${API}/api/portfolio/${encodeURIComponent(ticker)}`, { method: 'DELETE' })
            .then(() => loadPortfolio())
    }

    const updateInvestment = (ticker, lumpSum, monthlySip) => {
        fetch(`${API}/api/portfolio/${encodeURIComponent(ticker)}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ lump_sum: parseFloat(lumpSum) || 0, monthly_sip: parseFloat(monthlySip) || 0 }),
        })
            .then(r => r.json())
            .then(() => {
                setEditingTicker(null);
                loadPortfolio();
            })
            .catch(err => console.error("Failed to update investment:", err));
    }

    const loadDetail = (ticker) => {
        if (expandedTicker === ticker) { setExpandedTicker(null); return }
        setExpandedTicker(ticker)
        setDetailLoading(true)
        setDetailData(null)
        fetch(`${API}/api/ticker/${encodeURIComponent(ticker)}/detail`)
            .then(r => r.json())
            .then(d => { setDetailData(d); setDetailLoading(false) })
            .catch(() => setDetailLoading(false))
    }

    const changeColor = (v) => v > 0 ? 'var(--profit-green)' : v < 0 ? '#ef4444' : 'var(--text-muted)'
    const fmtPct = (v) => v != null ? `${v > 0 ? '+' : ''}${v}%` : 'N/A'
    const fmtCcy = (ccy) => ccy === 'EUR' ? '€' : ccy === 'GBP' ? '£' : ccy === 'INR' ? '₹' : '$'

    // Summary calculations
    const totalInvested = holdings.reduce((s, h) => s + (h.lump_sum || 0), 0)
    const totalMonthly = holdings.reduce((s, h) => s + (h.monthly_sip || 0), 0)

    return (
        <>
            <header>
                <h1>My Portfolio</h1>
                <p className="subtitle">Track your investments — add ETFs, mutual funds, or indices. Set lump-sum and monthly SIP amounts.</p>
            </header>

            {/* Summary Bar */}
            {holdings.length > 0 && (
                <div className="dashboard-grid" style={{ marginBottom: '1.5rem' }}>
                    <div className="metric-card glass-panel">
                        <span className="label">Holdings</span>
                        <span className="value">{holdings.length}</span>
                    </div>
                    <div className="metric-card glass-panel">
                        <span className="label">Total Invested (Lump Sum)</span>
                        <span className="value">${totalInvested.toLocaleString()}</span>
                    </div>
                    <div className="metric-card glass-panel">
                        <span className="label">Monthly SIP Total</span>
                        <span className="value">${totalMonthly.toLocaleString()}/mo</span>
                    </div>
                </div>
            )}

            {/* Search Bar */}
            <div className="glass-panel" style={{ padding: '1rem 1.5rem', marginBottom: '1.5rem', position: 'relative', zIndex: 200 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem' }}>
                    <span style={{ fontSize: '1.2rem' }}>🔍</span>
                    <input
                        type="text"
                        value={searchQuery}
                        onChange={e => setSearchQuery(e.target.value)}
                        placeholder="Search ETFs, funds, indices... (e.g. 'gold', 'vanguard', 'nifty')"
                        style={{
                            flex: 1,
                            background: 'transparent',
                            border: 'none',
                            outline: 'none',
                            color: 'white',
                            fontSize: '1rem',
                            fontFamily: 'Outfit, sans-serif',
                        }}
                    />
                    {searchQuery && (
                        <button onClick={() => { setSearchQuery(''); setSearchResults([]) }} style={{
                            background: 'rgba(255,255,255,0.1)', border: 'none', color: 'var(--text-muted)',
                            borderRadius: '50%', width: '24px', height: '24px', cursor: 'pointer', fontSize: '0.8rem',
                        }}>✕</button>
                    )}
                </div>

                {/* Dropdown Results */}
                {searchResults.length > 0 && (
                    <div style={{
                        position: 'absolute', top: '100%', left: 0, right: 0, zIndex: 100,
                        background: 'var(--bg-dark)', border: '1px solid var(--border-glass)',
                        borderRadius: '0 0 12px 12px', maxHeight: '300px', overflowY: 'auto',
                    }}>
                        {searchResults.map(r => {
                            const alreadyAdded = holdings.some(h => h.ticker === r.ticker)
                            return (
                                <div key={r.ticker} style={{
                                    padding: '0.7rem 1.5rem',
                                    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                                    borderBottom: '1px solid rgba(255,255,255,0.04)',
                                    cursor: alreadyAdded ? 'default' : 'pointer',
                                    opacity: alreadyAdded ? 0.4 : 1,
                                }} onClick={() => !alreadyAdded && addTicker(r.ticker, r.name)}>
                                    <div>
                                        <span style={{ fontWeight: 700, marginRight: '0.5rem' }}>{r.ticker}</span>
                                        <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>{r.name}</span>
                                        <span style={{
                                            marginLeft: '0.5rem', fontSize: '0.7rem', padding: '0.1rem 0.4rem',
                                            borderRadius: '999px', background: 'rgba(255,255,255,0.06)', color: 'var(--text-muted)',
                                        }}>{r.market} · {r.category}</span>
                                    </div>
                                    {alreadyAdded ? (
                                        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>✓ Added</span>
                                    ) : (
                                        <span style={{ color: 'var(--accent-blue)', fontWeight: 700, fontSize: '1.2rem' }}>+</span>
                                    )}
                                </div>
                            )
                        })}
                    </div>
                )}
            </div>

            {/* Holdings */}
            {loading ? (
                <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                    <h3>Loading portfolio...</h3>
                </div>
            ) : holdings.length === 0 ? (
                <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                    <h3>No holdings yet</h3>
                    <p>Use the search bar above to add ETFs, mutual funds, or indices to your portfolio.</p>
                </div>
            ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    {holdings.map(h => (
                        <div key={h.ticker} className="glass-panel" style={{ padding: '1.5rem' }}>
                            {/* Main card row */}
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', cursor: 'pointer' }}
                                onClick={() => loadDetail(h.ticker)}>
                                <div style={{ flex: 1 }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem', marginBottom: '0.5rem' }}>
                                        <span style={{ fontWeight: 700, fontSize: '1.1rem' }}>{h.name}</span>
                                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{h.ticker}</span>
                                    </div>
                                    <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'baseline', flexWrap: 'wrap' }}>
                                        <span style={{ fontSize: '1.8rem', fontWeight: 700 }}>
                                            {fmtCcy(h.currency)}{h.price?.toLocaleString()}
                                        </span>
                                        <span style={{ color: changeColor(h.day_change), fontWeight: 600 }}>{fmtPct(h.day_change)}</span>
                                        <span style={{ fontSize: '0.85rem' }}>
                                            <span style={{ color: 'var(--text-muted)' }}>1Y </span>
                                            <span style={{ fontWeight: 700, color: changeColor(h.return_1y) }}>{fmtPct(h.return_1y)}</span>
                                        </span>
                                        <span style={{ fontSize: '0.85rem' }}>
                                            <span style={{ color: 'var(--text-muted)' }}>5Y CAGR </span>
                                            <span style={{ fontWeight: 700, color: changeColor(h.cagr_5y) }}>{fmtPct(h.cagr_5y)}</span>
                                        </span>
                                    </div>
                                </div>
                                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'flex-start' }}>
                                    <Sparkline data={h.sparkline} color={h.day_change >= 0 ? '#10b981' : '#ef4444'} width={80} height={28} />
                                    <button onClick={e => { e.stopPropagation(); removeTicker(h.ticker) }} style={{
                                        background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)',
                                        color: '#ef4444', borderRadius: '8px', padding: '0.3rem 0.5rem', cursor: 'pointer',
                                        fontSize: '0.75rem', fontWeight: 600,
                                    }}>✕</button>
                                </div>
                            </div>

                            {/* Investment inputs row */}
                            <div style={{
                                display: 'flex', gap: '1rem', marginTop: '0.8rem', padding: '0.6rem 0',
                                borderTop: '1px solid rgba(255,255,255,0.06)', alignItems: 'center', flexWrap: 'wrap',
                            }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Lump Sum:</span>
                                    {editingTicker === h.ticker ? (
                                        <input id={`ls-${h.ticker}`} type="number" defaultValue={h.lump_sum || 0}
                                            style={{
                                                width: '90px', background: 'rgba(255,255,255,0.08)', border: '1px solid var(--border-glass)',
                                                borderRadius: '6px', padding: '0.3rem', color: 'white', fontSize: '0.85rem', fontFamily: 'Outfit'
                                            }}
                                        />
                                    ) : (
                                        <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>{fmtCcy(h.currency)}{(h.lump_sum || 0).toLocaleString()}</span>
                                    )}
                                </div>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Monthly SIP:</span>
                                    {editingTicker === h.ticker ? (
                                        <input id={`sip-${h.ticker}`} type="number" defaultValue={h.monthly_sip || 0}
                                            style={{
                                                width: '90px', background: 'rgba(255,255,255,0.08)', border: '1px solid var(--border-glass)',
                                                borderRadius: '6px', padding: '0.3rem', color: 'white', fontSize: '0.85rem', fontFamily: 'Outfit'
                                            }}
                                        />
                                    ) : (
                                        <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>{fmtCcy(h.currency)}{(h.monthly_sip || 0).toLocaleString()}/mo</span>
                                    )}
                                </div>
                                {editingTicker === h.ticker ? (
                                    <button onClick={() => {
                                        const ls = document.getElementById(`ls-${h.ticker}`).value
                                        const sip = document.getElementById(`sip-${h.ticker}`).value
                                        updateInvestment(h.ticker, ls, sip)
                                    }} style={{
                                        background: 'var(--accent-blue)', border: 'none', color: 'white',
                                        borderRadius: '6px', padding: '0.3rem 0.8rem', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 600,
                                    }}>Save</button>
                                ) : (
                                    <button onClick={e => { e.stopPropagation(); setEditingTicker(h.ticker) }} style={{
                                        background: 'rgba(255,255,255,0.06)', border: '1px solid var(--border-glass)',
                                        color: 'var(--text-muted)', borderRadius: '6px', padding: '0.3rem 0.6rem',
                                        cursor: 'pointer', fontSize: '0.75rem',
                                    }}>Edit</button>
                                )}
                            </div>

                            {/* Expanded Detail View */}
                            {expandedTicker === h.ticker && (
                                <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid rgba(255,255,255,0.08)' }}>
                                    {detailLoading ? (
                                        <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '2rem' }}>Loading performance data...</div>
                                    ) : detailData ? (
                                        <>
                                            {/* Metrics grid */}
                                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '0.8rem', marginBottom: '1.5rem' }}>
                                                {[
                                                    { label: '1M Return', value: fmtPct(detailData.return_1m), color: changeColor(detailData.return_1m) },
                                                    { label: '1Y Return', value: fmtPct(detailData.return_1y), color: changeColor(detailData.return_1y) },
                                                    { label: '5Y CAGR', value: fmtPct(detailData.cagr_5y), color: changeColor(detailData.cagr_5y) },
                                                    { label: 'Beta', value: detailData.beta?.toFixed(2) || 'N/A', color: 'white' },
                                                    { label: 'Expense Ratio', value: detailData.expense_ratio ? (detailData.expense_ratio * 100).toFixed(2) + '%' : 'N/A', color: 'white' },
                                                    { label: 'Div. Yield', value: detailData.dividend_yield ? (detailData.dividend_yield * 100).toFixed(2) + '%' : 'N/A', color: '#fbbf24' },
                                                ].map(m => (
                                                    <div key={m.label} style={{
                                                        background: 'rgba(255,255,255,0.03)', borderRadius: '8px', padding: '0.8rem',
                                                    }}>
                                                        <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '0.2rem' }}>{m.label}</div>
                                                        <div style={{ fontWeight: 700, fontSize: '1.1rem', color: m.color }}>{m.value}</div>
                                                    </div>
                                                ))}
                                            </div>

                                            {/* 5Y Growth Chart */}
                                            {detailData.chart && detailData.chart.length > 0 && (
                                                <div style={{ height: '250px' }}>
                                                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>5-Year Price History</div>
                                                    <ResponsiveContainer width="100%" height="100%">
                                                        <LineChart data={detailData.chart}>
                                                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                                                            <XAxis dataKey="date" tick={{ fill: '#94a3b8', fontSize: 10 }}
                                                                tickFormatter={v => v.substring(0, 7)} interval="preserveStartEnd" minTickGap={20} />
                                                            <YAxis tick={{ fill: '#94a3b8', fontSize: 10 }} domain={['auto', 'auto']} />
                                                            <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                                                                labelStyle={{ color: '#94a3b8' }} />
                                                            <Line type="monotone" dataKey="price" stroke="var(--accent-blue)"
                                                                strokeWidth={2} dot={false} isAnimationActive={false} />
                                                        </LineChart>
                                                    </ResponsiveContainer>
                                                </div>
                                            )}
                                        </>
                                    ) : null}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </>
    )
}

export function RiskAnalysis() {
    const [data, setData] = useState(null)
    const [loading, setLoading] = useState(true)
    const API = 'http://127.0.0.1:8001'

    useEffect(() => {
        fetch(`${API}/api/risk-analysis`)
            .then(r => r.json())
            .then(d => { setData(d); setLoading(false) })
            .catch(() => setLoading(false))
    }, [])

    const labelColor = (label) => {
        if (!label) return 'var(--text-muted)'
        const map = {
            'Excellent': '#10b981', 'Good': '#10b981', 'Low': '#10b981', 'Conservative': '#10b981',
            'Fair': '#f59e0b', 'Moderate': '#f59e0b',
            'Poor': '#ef4444', 'High': '#ef4444', 'Aggressive': '#f59e0b',
            'Negative': '#ef4444', 'Severe': '#ef4444', 'Very Aggressive': '#ef4444'
        }
        return map[label] || 'var(--text-muted)'
    }

    // Correlation matrix color
    const corrColor = (v) => {
        if (v >= 0.7) return 'rgba(16, 185, 129, 0.6)'
        if (v >= 0.3) return 'rgba(16, 185, 129, 0.25)'
        if (v >= -0.3) return 'rgba(255, 255, 255, 0.05)'
        if (v >= -0.7) return 'rgba(239, 68, 68, 0.25)'
        return 'rgba(239, 68, 68, 0.6)'
    }

    if (loading) return (
        <>
            <header><h1>Risk & Exposure Analysis</h1><p className="subtitle">Computing risk metrics...</p></header>
            <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                <AlertTriangle size={48} style={{ color: 'var(--accent-blue)', opacity: 0.5, marginBottom: '1rem' }} />
                <h2>Analyzing portfolio risk...</h2>
                <p>Fetching 1-year daily returns for all holdings and computing Beta, Sharpe, Drawdown.</p>
            </div>
        </>
    )

    if (!data || data.holdings_count === 0) return (
        <>
            <header><h1>Risk & Exposure Analysis</h1><p className="subtitle">Portfolio risk metrics.</p></header>
            <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center' }}>
                <AlertTriangle size={48} style={{ color: 'var(--text-muted)', opacity: 0.4, marginBottom: '1rem' }} />
                <h2 style={{ fontSize: '1.3rem', marginBottom: '0.5rem' }}>No holdings to analyze</h2>
                <p style={{ color: 'var(--text-muted)' }}>Add assets in the <a href="/portfolio" style={{ color: 'var(--accent-blue)' }}>Portfolio</a> page to see risk analysis.</p>
            </div>
        </>
    )

    return (
        <>
            <header>
                <h1>Risk & Exposure Analysis</h1>
                <p className="subtitle">Real-time risk metrics computed from {data.holdings_count} portfolio holdings.</p>
            </header>

            {/* Risk Metrics Cards */}
            <div className="dashboard-grid">
                <div className="metric-card glass-panel" style={{ borderLeft: `4px solid ${labelColor(data.beta_label)}` }}>
                    <span className="label">Portfolio Beta vs S&P 500</span>
                    <span className="value">{data.beta != null ? data.beta.toFixed(2) : 'N/A'}</span>
                    <span style={{ color: labelColor(data.beta_label), fontWeight: 600, fontSize: '0.85rem' }}>{data.beta_label || ''}</span>
                </div>
                <div className="metric-card glass-panel" style={{ borderLeft: `4px solid ${labelColor(data.sharpe_label)}` }}>
                    <span className="label">Sharpe Ratio (1Y)</span>
                    <span className="value">{data.sharpe_ratio != null ? data.sharpe_ratio.toFixed(2) : 'N/A'}</span>
                    <span style={{ color: labelColor(data.sharpe_label), fontWeight: 600, fontSize: '0.85rem' }}>{data.sharpe_label || ''}</span>
                </div>
                <div className="metric-card glass-panel" style={{ borderLeft: '4px solid var(--accent-blue)' }}>
                    <span className="label">Diversification Score</span>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <span className="value">{data.diversification_score ?? 'N/A'}%</span>
                        <div style={{ flex: 1, height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px', overflow: 'hidden', minWidth: '40px' }}>
                            <div style={{ width: `${data.diversification_score ?? 0}%`, height: '100%', background: 'var(--accent-blue)' }}></div>
                        </div>
                    </div>
                </div>
                <div className="metric-card glass-panel" style={{ borderLeft: '4px solid var(--accent-blue)' }}>
                    <span className="label">Ann. Return / Volatility</span>
                    <span className="value">{data.annual_return != null ? (data.annual_return > 0 ? '+' : '') + data.annual_return.toFixed(2) + '%' : 'N/A'}</span>
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Vol: {data.volatility != null ? data.volatility.toFixed(2) + '%' : 'N/A'}</span>
                </div>
            </div>

            {/* Middle: Sector Exposure + Correlation */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginTop: '1.5rem' }}>
                {/* Sector Exposure */}
                <div className="glass-panel" style={{ padding: '1.5rem' }}>
                    <h3 style={{ margin: '0 0 1rem 0', fontSize: '1rem' }}>Sector Exposure</h3>
                    {data.sector_exposure && data.sector_exposure.length > 0 ? (
                        <SvgDonut data={data.sector_exposure} />
                    ) : (
                        <p style={{ color: 'var(--text-muted)' }}>No sector data available.</p>
                    )}
                </div>

                {/* Correlation Mini-Matrix */}
                <div className="glass-panel" style={{ padding: '1.5rem' }}>
                    <h3 style={{ margin: '0 0 1rem 0', fontSize: '1rem' }}>Holdings Correlation</h3>
                    {data.correlation_matrix && data.correlation_matrix.labels?.length > 0 ? (
                        <div style={{ overflowX: 'auto' }}>
                            <table style={{ borderCollapse: 'separate', borderSpacing: '3px', fontSize: '0.75rem' }}>
                                <thead>
                                    <tr>
                                        <th></th>
                                        {data.correlation_matrix.labels.map(l => (
                                            <th key={l} style={{ padding: '0.3rem 0.4rem', color: 'var(--text-muted)', fontWeight: 500, maxWidth: '55px', overflow: 'hidden', textOverflow: 'ellipsis' }}>{l}</th>
                                        ))}
                                    </tr>
                                </thead>
                                <tbody>
                                    {data.correlation_matrix.matrix.map((row, i) => (
                                        <tr key={i}>
                                            <td style={{ padding: '0.3rem 0.4rem', fontWeight: 600, color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>{data.correlation_matrix.labels[i]}</td>
                                            {row.map((val, j) => (
                                                <td key={j} style={{
                                                    padding: '0.3rem 0.4rem', textAlign: 'center', borderRadius: '4px',
                                                    background: corrColor(val), fontWeight: i === j ? 700 : 500,
                                                    color: i === j ? 'var(--text-muted)' : 'white',
                                                }}>{val != null ? val.toFixed(2) : '—'}</td>
                                            ))}
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    ) : (
                        <p style={{ color: 'var(--text-muted)' }}>Need at least 2 holdings for correlation analysis.</p>
                    )}
                </div>
            </div>

            {/* Intelligence Section: Rolling Correlation */}
            <div className="glass-panel" style={{ padding: '1.5rem', marginTop: '1.5rem' }}>
                <h3 style={{ margin: '0 0 1rem 0', fontSize: '1rem' }}>Rolling Portfolio Correlation (30D Window)</h3>
                <div style={{ height: '200px' }}>
                    {data.rolling_correlation?.length > 0 ? (
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={data.rolling_correlation}>
                                <defs>
                                    <linearGradient id="colorCorr" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="var(--accent-blue)" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="var(--accent-blue)" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                                <XAxis dataKey="date" hide />
                                <YAxis domain={[0, 1]} hide />
                                <Tooltip
                                    contentStyle={{ background: 'rgba(0,0,0,0.8)', border: '1px solid var(--border-glass)', borderRadius: '8px' }}
                                    itemStyle={{ color: 'var(--accent-blue)' }}
                                />
                                <Area type="monotone" dataKey="value" stroke="var(--accent-blue)" fillOpacity={1} fill="url(#colorCorr)" />
                            </AreaChart>
                        </ResponsiveContainer>
                    ) : (
                        <p style={{ color: 'var(--text-muted)', textAlign: 'center', paddingTop: '4rem' }}>Need at least 2 holdings and 30 days of history for rolling analysis.</p>
                    )}
                </div>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '1rem' }}>
                    A rising rolling correlation indicates assets are moving together more closely, meaning diversification benefits are decreasing.
                </p>
            </div>

            {/* Risk Glossary */}
            <div className="glass-panel" style={{ padding: '1.5rem', marginTop: '1.5rem' }}>
                <h3 style={{ margin: '0 0 1rem 0', fontSize: '1rem', color: 'var(--text-muted)' }}>📖 Risk Intelligence</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                    <div>
                        <strong style={{ color: 'white', display: 'block', marginBottom: '0.3rem' }}>Beta: {data.beta?.toFixed(2)}</strong>
                        {data.beta > 1 ? "Portfolio is more volatile than the market. Expect larger swings." : "Portfolio is more stable than the market."}
                    </div>
                    <div>
                        <strong style={{ color: 'white', display: 'block', marginBottom: '0.3rem' }}>Diversification: {data.diversification_score}%</strong>
                        Your assets have an average correlation of {((100 - data.diversification_score) / 100).toFixed(2)}. {data.diversification_score > 70 ? "Excellent spread." : "Consider adding uncorrelated assets like Gold or Bonds."}
                    </div>
                    <div>
                        <strong style={{ color: 'white', display: 'block', marginBottom: '0.3rem' }}>Max Drawdown: {data.max_drawdown?.toFixed(2)}%</strong>
                        The worst-case peak-to-trough decline in the past year. Ensure your cash reserves cover this gap.
                    </div>
                </div>
            </div>
        </>
    )
}

export function Settings() {
    return (
        <>
            <header>
                <h1>Engine Configurations</h1>
                <p className="subtitle">Manage API keys, backtesting parameters, and system preferences.</p>
            </header>
            <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center' }}>
                <PlayCircle size={48} style={{ color: 'var(--text-muted)', opacity: 0.5, marginBottom: '1rem' }} />
                <p style={{ color: 'var(--text-muted)' }}>Configuration panel is currently locked by the CTO.</p>
            </div>
        </>
    )
}

export function SectorHeatmap() {
    const [data, setData] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
    const [market, setMarket] = useState('US')

    const MARKETS = [
        { key: 'US', label: 'United States', shortLabel: 'US' },
        { key: 'EU', label: 'Europe', shortLabel: 'Europe' },
        { key: 'India', label: 'India', shortLabel: 'India' },
    ]

    useEffect(() => {
        setLoading(true)
        setError(null)
        fetch(`http://127.0.0.1:8001/api/sector/heatmap?market=${market}`)
            .then(res => res.json())
            .then(d => {
                if (Array.isArray(d)) {
                    setData(d)
                } else {
                    console.error("API did not return an array:", d)
                    setError("Received invalid data from server.")
                    setData([])
                }
                setLoading(false)
            })
            .catch(err => {
                console.error("Failed to fetch heatmap data:", err)
                setError("Failed to communicate with server.")
                setLoading(false)
            })
    }, [market])

    // Dynamic years logic (2010 to current year)
    const startYear = 2010;
    const currentYear = new Date().getFullYear();
    const years = Array.from({ length: currentYear - startYear + 1 }, (_, i) => currentYear - i);

    const getBgColor = (val, baseColor) => {
        if (!val && val !== 0) return 'rgba(255,255,255,0.05)';
        const hex = baseColor.replace('#', '');
        const r = parseInt(hex.substring(0, 2), 16);
        const g = parseInt(hex.substring(2, 4), 16);
        const b = parseInt(hex.substring(4, 6), 16);
        return `rgba(${r}, ${g}, ${b}, 0.5)`;
    }

    const marketInfo = MARKETS.find(m => m.key === market) || MARKETS[0];

    return (
        <>
            <header>
                <h1>Sector Heatmap Tracker</h1>
                <p className="subtitle">Visualizing annual percentage growth of {marketInfo.label} sectors since 2010.</p>
            </header>

            {/* Market Selector — pill-style segmented control */}
            <div style={{ display: 'flex', justifyContent: 'center', margin: '1.5rem 0' }}>
                <div style={{
                    display: 'inline-flex',
                    background: 'rgba(255,255,255,0.06)',
                    borderRadius: '12px',
                    padding: '4px',
                    border: '1px solid var(--border-glass)',
                    gap: '2px',
                }}>
                    {MARKETS.map(m => (
                        <button
                            key={m.key}
                            onClick={() => setMarket(m.key)}
                            style={{
                                background: market === m.key
                                    ? 'linear-gradient(135deg, var(--accent-blue), #6366f1)'
                                    : 'transparent',
                                color: market === m.key ? 'white' : 'var(--text-muted)',
                                border: 'none',
                                padding: '0.6rem 1.4rem',
                                borderRadius: '10px',
                                cursor: 'pointer',
                                fontFamily: 'Outfit, sans-serif',
                                fontSize: '0.95rem',
                                fontWeight: market === m.key ? 700 : 500,
                                transition: 'all 0.25s ease',
                                boxShadow: market === m.key ? '0 2px 12px rgba(99, 102, 241, 0.35)' : 'none',
                                letterSpacing: '0.3px',
                            }}
                        >
                            {m.shortLabel}
                        </button>
                    ))}
                </div>
            </div>

            {loading ? (
                <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                    <h2>Synthesizing {marketInfo.label} Sector Data...</h2>
                    <p>Retrieving historical records and calculating performance.</p>
                </div>
            ) : (
                <div className="glass-panel" style={{ padding: '2rem', overflowX: 'auto' }}>
                    <table style={{ minWidth: '1000px', borderCollapse: 'separate', borderSpacing: '4px', width: '100%' }}>
                        <thead>
                            <tr>
                                {years.map(y => (
                                    <th key={y} style={{ textAlign: 'center', padding: '1rem', fontSize: '1.05rem', color: 'white', minWidth: '100px' }}>{y}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {error ? (
                                <tr>
                                    <td colSpan={years.length} style={{ padding: '2rem', textAlign: 'center', color: '#ef4444' }}>
                                        {error}
                                    </td>
                                </tr>
                            ) : Array.isArray(data) && data.length > 0 && Array.from({ length: data.length }).map((_, rowIndex) => (
                                <tr key={rowIndex}>
                                    {years.map(y => {
                                        let sectorsForYear = data.map(s => ({
                                            sector: s.sector,
                                            color: s.color,
                                            val: s.returns && s.returns[y.toString()] !== undefined ? s.returns[y.toString()] : null
                                        }));

                                        sectorsForYear.sort((a, b) => {
                                            if (a.val === null && b.val === null) return 0;
                                            if (a.val === null) return 1;
                                            if (b.val === null) return -1;
                                            return b.val - a.val;
                                        });

                                        const cellData = sectorsForYear[rowIndex];
                                        if (!cellData || cellData.val === null) {
                                            return <td key={y} style={{ padding: '1rem', background: 'rgba(255,255,255,0.02)', borderRadius: '6px' }}></td>;
                                        }

                                        return (
                                            <td key={`${y}-${cellData.sector}`} style={{
                                                background: getBgColor(cellData.val, cellData.color),
                                                padding: '0.8rem 0.4rem',
                                                textAlign: 'center',
                                                borderRadius: '6px',
                                                border: '1px solid rgba(255,255,255,0.1)',
                                                transition: 'transform 0.2s, box-shadow 0.2s',
                                                cursor: 'default'
                                            }}
                                                title={`${cellData.sector} ${y}: ${cellData.val !== null ? cellData.val + '%' : 'N/A'}`}
                                                onMouseEnter={(e) => {
                                                    e.currentTarget.style.transform = 'scale(1.05)';
                                                    e.currentTarget.style.boxShadow = `0 4px 15px ${cellData.color}60`;
                                                    e.currentTarget.style.zIndex = '10';
                                                    e.currentTarget.style.position = 'relative';
                                                }}
                                                onMouseLeave={(e) => {
                                                    e.currentTarget.style.transform = 'scale(1)';
                                                    e.currentTarget.style.boxShadow = 'none';
                                                    e.currentTarget.style.zIndex = '1';
                                                }}
                                            >
                                                <div style={{ fontWeight: 600, fontSize: '0.8rem', color: 'rgba(255,255,255,0.95)', marginBottom: '0.3rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                                    {cellData.sector}
                                                </div>
                                                <div style={{ fontWeight: 700, fontSize: '0.95rem', color: 'white' }}>
                                                    {cellData.val > 0 ? '+' : ''}{cellData.val.toFixed(1)}%
                                                </div>
                                            </td>
                                        )
                                    })}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            <div className="glass-panel" style={{ padding: '2rem', marginTop: '2rem' }}>
                <h3 style={{ margin: '0 0 1rem 0' }}>Sectors & Color Coding</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '1rem' }}>
                    {(Array.isArray(data) ? data : []).map(sector => (
                        <div key={sector.sector} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <div style={{ width: '16px', height: '16px', borderRadius: '4px', backgroundColor: sector.color }}></div>
                            <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>{sector.sector}</span>
                        </div>
                    ))}
                </div>
                <div style={{ marginTop: '2rem', display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '0.9rem', color: 'var(--text-muted)', borderTop: '1px solid var(--border-glass)', paddingTop: '1rem' }}>
                    <span><strong>Note:</strong> Columns are sorted from highest to lowest return each year (Quilt Chart style).</span>
                </div>
            </div>
        </>
    )
}

export function SectorIndices() {
    const [data, setData] = useState([])
    const [loading, setLoading] = useState(true)
    const [sectorFilter, setSectorFilter] = useState('All')
    const [market, setMarket] = useState('US')

    const MARKETS = [
        { key: 'US', label: 'United States', shortLabel: 'US' },
        { key: 'EU', label: 'Europe', shortLabel: 'Europe' },
        { key: 'India', label: 'India', shortLabel: 'India' },
    ]

    useEffect(() => {
        setLoading(true)
        setData([])
        setSectorFilter('All')
        fetch(`http://127.0.0.1:8001/api/sector/indices?market=${market}`)
            .then(res => res.json())
            .then(d => {
                setData(d)
                setLoading(false)
            })
            .catch(err => {
                console.error("Failed to fetch sector indices:", err)
                setLoading(false)
            })
    }, [market])

    const marketInfo = MARKETS.find(m => m.key === market) || MARKETS[0];

    // Helper to format large numbers
    const formatBillion = (val) => {
        if (val === null || val === undefined) return 'N/A';
        return `$${(val / 1e9).toFixed(2)}B`;
    };

    // Get unique sectors for filter dropdown
    const sectors = React.useMemo(() => {
        const unique = [...new Set(data.map(d => d.sector))];
        return ['All', ...unique];
    }, [data]);

    // Filter data based on selected sector
    const filteredData = React.useMemo(() => {
        if (sectorFilter === 'All') return data;
        return data.filter(d => d.sector === sectorFilter);
    }, [data, sectorFilter]);

    // Calculate maximums across the FILTERED data so ★ is accurate
    const maxMetrics = React.useMemo(() => {
        if (!filteredData.length) return {};
        return {
            cagr: Math.max(...filteredData.map(d => d.cagr || -Infinity)),
            ey: Math.max(...filteredData.map(d => d.ey || -Infinity)),
            roc: Math.max(...filteredData.map(d => d.roc || -Infinity)),
            ebit: Math.max(...filteredData.map(d => d.ebit || -Infinity)),
            ev: Math.max(...filteredData.map(d => d.ev || -Infinity)),
            nwc: Math.max(...filteredData.map(d => d.nwc || -Infinity)),
        };
    }, [filteredData]);

    // Group filtered data by sector for visual grouping
    const groupedData = React.useMemo(() => {
        const groups = [];
        let lastSector = null;
        filteredData.forEach(row => {
            if (row.sector !== lastSector) {
                groups.push({ type: 'header', sector: row.sector, color: row.color });
                lastSector = row.sector;
            }
            groups.push({ type: 'row', ...row });
        });
        return groups;
    }, [filteredData]);

    return (
        <>
            <header>
                <h1>Sector Indices & Fundamentals</h1>
                <p className="subtitle">Detailed metrics and 5-Year CAGR for {marketInfo.label} — {filteredData.length} instruments across {sectorFilter === 'All' ? sectors.length - 1 : 1} sector{sectorFilter === 'All' && sectors.length - 1 !== 1 ? 's' : ''}.</p>
            </header>

            {/* Market Selector */}
            <div style={{ display: 'flex', justifyContent: 'center', margin: '1.5rem 0' }}>
                <div style={{
                    display: 'inline-flex',
                    background: 'rgba(255,255,255,0.06)',
                    borderRadius: '12px',
                    padding: '4px',
                    border: '1px solid var(--border-glass)',
                    gap: '2px',
                }}>
                    {MARKETS.map(m => (
                        <button
                            key={m.key}
                            onClick={() => setMarket(m.key)}
                            style={{
                                background: market === m.key
                                    ? 'linear-gradient(135deg, var(--accent-blue), #6366f1)'
                                    : 'transparent',
                                color: market === m.key ? 'white' : 'var(--text-muted)',
                                border: 'none',
                                padding: '0.6rem 1.4rem',
                                borderRadius: '10px',
                                cursor: 'pointer',
                                fontFamily: 'Outfit, sans-serif',
                                fontSize: '0.95rem',
                                fontWeight: market === m.key ? 700 : 500,
                                transition: 'all 0.25s ease',
                                boxShadow: market === m.key ? '0 2px 12px rgba(99, 102, 241, 0.35)' : 'none',
                                letterSpacing: '0.3px',
                            }}
                        >
                            {m.shortLabel}
                        </button>
                    ))}
                </div>
            </div>

            <div className="glass-panel" style={{ padding: '1.5rem', marginTop: '1rem' }}>
                {/* Filter Bar */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                    <h2 style={{ fontSize: '1.2rem', margin: 0, fontWeight: 600 }}>{marketInfo.label} Sector Comparison</h2>
                    <select
                        value={sectorFilter}
                        onChange={e => setSectorFilter(e.target.value)}
                        style={{
                            background: 'var(--bg-dark)',
                            border: '1px solid var(--border-glass)',
                            color: 'white',
                            padding: '0.5rem 1rem',
                            borderRadius: '8px',
                            cursor: 'pointer',
                            fontFamily: 'Outfit, sans-serif',
                            fontSize: '0.95rem',
                            outline: 'none',
                            minWidth: '180px',
                        }}
                    >
                        {sectors.map(s => (
                            <option key={s} value={s} style={{ background: 'var(--bg-dark)' }}>
                                {s === 'All' ? '📊 All Sectors' : s}
                            </option>
                        ))}
                    </select>
                </div>

                <div className="data-table-container">
                    {loading ? (
                        <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                            <h3>Evaluating 55 Sector ETFs across 11 Sectors...</h3>
                            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Fetching fundamentals from multiple providers (SPDR, Vanguard, iShares, Fidelity)</p>
                        </div>
                    ) : (
                        <table>
                            <thead>
                                <tr>
                                    <th>ETF Provider</th>
                                    <th>Ticker</th>
                                    <th>5Y CAGR</th>
                                    <th>Earnings Yield</th>
                                    <th>Return on Capital</th>
                                    <th>EBIT</th>
                                    <th>Enterprise Value</th>
                                    <th>Net Working Cap</th>
                                </tr>
                            </thead>
                            <tbody>
                                {groupedData.map((item, idx) => {
                                    if (item.type === 'header') {
                                        return (
                                            <tr key={`header-${item.sector}`}>
                                                <td colSpan="8" style={{
                                                    background: `linear-gradient(90deg, ${item.color}22, transparent)`,
                                                    borderLeft: `4px solid ${item.color}`,
                                                    padding: '0.8rem 1.5rem',
                                                    fontWeight: 700,
                                                    fontSize: '0.95rem',
                                                    letterSpacing: '0.5px',
                                                    color: 'white',
                                                }}>
                                                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                                        <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: item.color, boxShadow: `0 0 10px ${item.color}` }}></div>
                                                        {item.sector}
                                                    </div>
                                                </td>
                                            </tr>
                                        );
                                    }

                                    const row = item;
                                    const isBestCagr = row.cagr === maxMetrics.cagr && row.cagr !== null;
                                    const isBestEy = row.ey === maxMetrics.ey && row.ey !== null;
                                    const isBestRoc = row.roc === maxMetrics.roc && row.roc !== null;
                                    const isBestEbit = row.ebit === maxMetrics.ebit && row.ebit !== null;
                                    const isBestEv = row.ev === maxMetrics.ev && row.ev !== null;
                                    const isBestNwc = row.nwc === maxMetrics.nwc && row.nwc !== null;

                                    // Infer provider from ticker
                                    const providerMap = {
                                        'XLK': 'SPDR', 'XLF': 'SPDR', 'XLV': 'SPDR', 'XLY': 'SPDR', 'XLP': 'SPDR', 'XLE': 'SPDR', 'XLB': 'SPDR', 'XLI': 'SPDR', 'XLU': 'SPDR', 'XLRE': 'SPDR', 'XLC': 'SPDR',
                                        'VGT': 'Vanguard', 'VFH': 'Vanguard', 'VHT': 'Vanguard', 'VCR': 'Vanguard', 'VDC': 'Vanguard', 'VDE': 'Vanguard', 'VAW': 'Vanguard', 'VIS': 'Vanguard', 'VPU': 'Vanguard', 'VNQ': 'Vanguard', 'VOX': 'Vanguard',
                                        'IYW': 'iShares', 'IYF': 'iShares', 'IYH': 'iShares', 'IYC': 'iShares', 'IYK': 'iShares', 'IYE': 'iShares', 'IYM': 'iShares', 'IYJ': 'iShares', 'IDU': 'iShares', 'USRT': 'iShares', 'IXP': 'iShares',
                                        'FTEC': 'Fidelity', 'FNCL': 'Fidelity', 'FHLC': 'Fidelity', 'FDIS': 'Fidelity', 'FSTA': 'Fidelity', 'FENY': 'Fidelity', 'FMAT': 'Fidelity', 'FIDU': 'Fidelity', 'FUTY': 'Fidelity', 'FREL': 'Fidelity', 'FCOM': 'Fidelity',
                                        'IXN': 'iShares Glbl', 'IXG': 'iShares Glbl', 'IXJ': 'iShares Glbl', 'RXI': 'iShares Glbl', 'KXI': 'iShares Glbl', 'IXC': 'iShares Glbl', 'MXI': 'iShares Glbl', 'EXI': 'iShares Glbl', 'JXI': 'iShares Glbl', 'SCHH': 'Schwab', 'IYZ': 'iShares',
                                    };
                                    const provider = providerMap[row.ticker] || row.ticker;

                                    return (
                                        <tr key={row.ticker} style={{ transition: 'background 0.2s' }} onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.02)'} onMouseLeave={e => e.currentTarget.style.background = 'transparent'}>
                                            <td>
                                                <span style={{ fontWeight: 500, color: 'white', fontSize: '0.95rem' }}>{provider}</span>
                                            </td>
                                            <td>
                                                <span style={{
                                                    fontSize: '0.85rem',
                                                    color: 'var(--accent-blue)',
                                                    fontWeight: 600,
                                                    background: 'rgba(59, 130, 246, 0.1)',
                                                    padding: '0.2rem 0.6rem',
                                                    borderRadius: '6px',
                                                }}>{row.ticker}</span>
                                            </td>

                                            <td style={{
                                                fontWeight: isBestCagr ? 700 : 500,
                                                color: isBestCagr ? 'var(--profit-green)' : (row.cagr > 0 ? 'white' : 'var(--text-muted)'),
                                                textShadow: isBestCagr ? '0 0 10px rgba(16, 185, 129, 0.4)' : 'none'
                                            }}>
                                                {row.cagr !== null ? (row.cagr * 100).toFixed(2) + '%' : 'N/A'}
                                                {isBestCagr && <span style={{ fontSize: '0.7rem', verticalAlign: 'super', marginLeft: '4px' }}>★</span>}
                                            </td>

                                            <td style={{
                                                fontWeight: isBestEy ? 700 : 500,
                                                color: isBestEy ? 'var(--accent-blue)' : (row.ey > 0 ? 'white' : 'var(--text-muted)'),
                                                textShadow: isBestEy ? '0 0 10px rgba(59, 130, 246, 0.4)' : 'none'
                                            }}>
                                                {row.ey !== null ? (row.ey * 100).toFixed(2) + '%' : 'N/A'}
                                                {isBestEy && <span style={{ fontSize: '0.7rem', verticalAlign: 'super', marginLeft: '4px' }}>★</span>}
                                            </td>

                                            <td style={{
                                                fontWeight: isBestRoc ? 700 : 500,
                                                color: isBestRoc ? 'var(--accent-blue)' : (row.roc > 0 ? 'white' : 'var(--text-muted)'),
                                                textShadow: isBestRoc ? '0 0 10px rgba(59, 130, 246, 0.4)' : 'none'
                                            }}>
                                                {row.roc !== null ? (row.roc * 100).toFixed(2) + '%' : 'N/A'}
                                                {isBestRoc && <span style={{ fontSize: '0.7rem', verticalAlign: 'super', marginLeft: '4px' }}>★</span>}
                                            </td>

                                            <td style={{ fontWeight: isBestEbit ? 600 : 400, color: isBestEbit ? 'white' : 'var(--text-muted)' }}>
                                                {formatBillion(row.ebit)}
                                                {isBestEbit && <span style={{ fontSize: '0.7rem', color: 'var(--accent-blue)', verticalAlign: 'super', marginLeft: '4px' }}>★</span>}
                                            </td>

                                            <td style={{ fontWeight: isBestEv ? 600 : 400, color: isBestEv ? 'white' : 'var(--text-muted)' }}>
                                                {formatBillion(row.ev)}
                                                {isBestEv && <span style={{ fontSize: '0.7rem', color: 'var(--accent-blue)', verticalAlign: 'super', marginLeft: '4px' }}>★</span>}
                                            </td>

                                            <td style={{ fontWeight: isBestNwc ? 600 : 400, color: isBestNwc ? 'white' : 'var(--text-muted)' }}>
                                                {formatBillion(row.nwc)}
                                                {isBestNwc && <span style={{ fontSize: '0.7rem', color: 'var(--accent-blue)', verticalAlign: 'super', marginLeft: '4px' }}>★</span>}
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    )}
                </div>

                <div style={{ marginTop: '1.5rem', display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '0.9rem', color: 'var(--text-muted)', borderTop: '1px solid var(--border-glass)', paddingTop: '1rem' }}>
                    <span><strong>Legend:</strong> The ★ icon and highlighted text indicate the highest performing metric across the currently displayed ETFs. Sector headers group ETFs from SPDR, Vanguard, iShares, Fidelity, and global providers.</span>
                </div>
            </div>
        </>
    )
}

export function DebtFunds() {
    const [data, setData] = useState([])
    const [loading, setLoading] = useState(true)
    const [market, setMarket] = useState('US')
    const [categoryFilter, setCategoryFilter] = useState('All')

    const MARKETS = [
        { key: 'US', label: 'United States', shortLabel: 'US' },
        { key: 'EU', label: 'Europe', shortLabel: 'Europe' },
        { key: 'India', label: 'India', shortLabel: 'India' },
    ]

    useEffect(() => {
        setLoading(true)
        setCategoryFilter('All')
        fetch(`http://127.0.0.1:8001/api/debt-funds?market=${market}`)
            .then(res => res.json())
            .then(d => {
                setData(d)
                setLoading(false)
            })
            .catch(err => {
                console.error("Failed to fetch debt funds:", err)
                setLoading(false)
            })
    }, [market])

    const marketInfo = MARKETS.find(m => m.key === market) || MARKETS[0]

    const categories = React.useMemo(() => {
        const cats = ['All', ...new Set(data.map(d => d.category))]
        return cats
    }, [data])

    const filteredData = categoryFilter === 'All' ? data : data.filter(d => d.category === categoryFilter)

    const formatAUM = (val) => {
        if (!val) return 'N/A'
        if (val >= 1e12) return `$${(val / 1e12).toFixed(1)}T`
        if (val >= 1e9) return `$${(val / 1e9).toFixed(1)}B`
        if (val >= 1e6) return `$${(val / 1e6).toFixed(0)}M`
        return `$${val.toLocaleString()}`
    }

    const formatReturn = (val) => {
        if (val === null || val === undefined) return 'N/A'
        const color = val >= 0 ? 'var(--profit-green)' : '#ef4444'
        return <span style={{ color, fontWeight: 600 }}>{val >= 0 ? '+' : ''}{val.toFixed(2)}%</span>
    }

    // Group data by category
    const groupedData = React.useMemo(() => {
        const groups = []
        let lastCat = null
        filteredData.forEach(row => {
            if (row.category !== lastCat) {
                groups.push({ type: 'header', category: row.category })
                lastCat = row.category
            }
            groups.push({ type: 'row', ...row })
        })
        return groups
    }, [filteredData])

    return (
        <>
            <header>
                <h1>Debt Funds & Bond ETFs</h1>
                <p className="subtitle">Top fixed-income instruments in {marketInfo.label} — NAV, Yield, AUM, and annualized returns.</p>
            </header>

            {/* Market Selector */}
            <div style={{ display: 'flex', justifyContent: 'center', margin: '1.5rem 0' }}>
                <div style={{
                    display: 'inline-flex',
                    background: 'rgba(255,255,255,0.06)',
                    borderRadius: '12px',
                    padding: '4px',
                    border: '1px solid var(--border-glass)',
                    gap: '2px',
                }}>
                    {MARKETS.map(m => (
                        <button
                            key={m.key}
                            onClick={() => setMarket(m.key)}
                            style={{
                                background: market === m.key
                                    ? 'linear-gradient(135deg, var(--accent-blue), #6366f1)'
                                    : 'transparent',
                                color: market === m.key ? 'white' : 'var(--text-muted)',
                                border: 'none',
                                padding: '0.6rem 1.4rem',
                                borderRadius: '10px',
                                cursor: 'pointer',
                                fontFamily: 'Outfit, sans-serif',
                                fontSize: '0.95rem',
                                fontWeight: market === m.key ? 700 : 500,
                                transition: 'all 0.25s ease',
                                boxShadow: market === m.key ? '0 2px 12px rgba(99, 102, 241, 0.35)' : 'none',
                                letterSpacing: '0.3px',
                            }}
                        >
                            {m.shortLabel}
                        </button>
                    ))}
                </div>
            </div>

            <div className="glass-panel" style={{ padding: '1.5rem', marginTop: '1rem' }}>
                {/* Filter Bar */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                    <h2 style={{ fontSize: '1.2rem', margin: 0, fontWeight: 600 }}>{marketInfo.label} Debt Fund Comparison</h2>
                    <select
                        value={categoryFilter}
                        onChange={e => setCategoryFilter(e.target.value)}
                        style={{
                            background: 'var(--bg-dark)',
                            border: '1px solid var(--border-glass)',
                            color: 'white',
                            padding: '0.5rem 1rem',
                            borderRadius: '8px',
                            cursor: 'pointer',
                            fontFamily: 'Outfit, sans-serif',
                        }}
                    >
                        {categories.map(c => <option key={c} value={c}>{c}</option>)}
                    </select>
                </div>

                <div className="data-table-container">
                    {loading ? (
                        <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                            <h3>Loading {marketInfo.label} debt funds...</h3>
                            <p>Fetching NAV, yields, and return data from Yahoo Finance</p>
                        </div>
                    ) : (
                        <table>
                            <thead>
                                <tr>
                                    <th>#</th>
                                    <th>Fund / ETF</th>
                                    <th>NAV</th>
                                    <th>Yield</th>
                                    <th>AUM</th>
                                    <th>1Y Return</th>
                                    <th>3Y CAGR</th>
                                    <th>5Y CAGR</th>
                                </tr>
                            </thead>
                            <tbody>
                                {groupedData.map((item, idx) => {
                                    if (item.type === 'header') {
                                        return (
                                            <tr key={`cat-${item.category}`} style={{
                                                background: 'rgba(99, 102, 241, 0.08)',
                                                borderLeft: '3px solid var(--accent-blue)',
                                            }}>
                                                <td colSpan="8" style={{
                                                    fontWeight: 700,
                                                    fontSize: '0.95rem',
                                                    padding: '0.8rem 1rem',
                                                    color: 'var(--accent-blue)',
                                                    letterSpacing: '0.5px',
                                                }}>
                                                    {item.category}
                                                </td>
                                            </tr>
                                        )
                                    }
                                    return (
                                        <tr key={item.ticker}>
                                            <td style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>{idx}</td>
                                            <td>
                                                <div style={{ display: 'flex', flexDirection: 'column' }}>
                                                    <span style={{ fontWeight: 600, color: 'white' }}>{item.ticker}</span>
                                                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{item.name}</span>
                                                </div>
                                            </td>
                                            <td style={{ fontWeight: 600 }}>{item.nav ? `${market === 'India' ? '₹' : market === 'EU' ? '€' : '$'}${item.nav.toLocaleString()}` : 'N/A'}</td>
                                            <td style={{ fontWeight: 600, color: item.yield ? 'var(--profit-green)' : 'var(--text-muted)' }}>
                                                {item.yield ? `${item.yield.toFixed(2)}%` : 'N/A'}
                                            </td>
                                            <td style={{ color: 'var(--text-muted)' }}>{formatAUM(item.aum)}</td>
                                            <td>{formatReturn(item.return_1y)}</td>
                                            <td>{formatReturn(item.return_3y)}</td>
                                            <td>{formatReturn(item.return_5y)}</td>
                                        </tr>
                                    )
                                })}
                            </tbody>
                        </table>
                    )}
                </div>

                <div style={{ marginTop: '1.5rem', display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '0.9rem', color: 'var(--text-muted)', borderTop: '1px solid var(--border-glass)', paddingTop: '1rem' }}>
                    <span><strong>Note:</strong> Returns are annualized (CAGR). Yield is trailing 12-month distribution yield. Data sourced from Yahoo Finance.</span>
                </div>
            </div>
        </>
    )
}

// ─── Mini SVG Sparkline ──────────────────────────────────────────
function Sparkline({ data, color = '#3b82f6', width = 120, height = 32 }) {
    if (!data || data.length < 2) return null
    const min = Math.min(...data), max = Math.max(...data)
    const range = max - min || 1
    const points = data.map((v, i) =>
        `${(i / (data.length - 1)) * width},${height - ((v - min) / range) * height}`
    ).join(' ')
    return (
        <svg width={width} height={height} style={{ display: 'block' }}>
            <polyline fill="none" stroke={color} strokeWidth="1.5" points={points} />
        </svg>
    )
}

// ─── 1. MACRO DASHBOARD ─────────────────────────────────────────
export function MacroDashboard() {
    const [data, setData] = useState({ indices: [], gauges: [] })
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetch('http://127.0.0.1:8001/api/macro')
            .then(r => r.json())
            .then(d => { setData(d); setLoading(false) })
            .catch(() => setLoading(false))
    }, [])

    const changeColor = (v) => v > 0 ? 'var(--profit-green)' : v < 0 ? '#ef4444' : 'var(--text-muted)'

    const regions = ['US', 'EU', 'India', 'Asia']

    return (
        <>
            <header>
                <h1>Market Overview</h1>
                <p className="subtitle">Global indices, volatility gauges, treasury yields, and dollar index — live from Yahoo Finance.</p>
            </header>

            {loading ? (
                <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                    <h3>Loading global market data...</h3>
                </div>
            ) : (
                <>
                    {/* Market Gauges Row */}
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
                        {data.gauges.map(g => (
                            <div key={g.ticker} className="glass-panel" style={{
                                padding: '1.2rem',
                                borderLeft: `3px solid ${g.type === 'volatility' ? '#ef4444' : g.type === 'yield' ? '#f59e0b' : '#3b82f6'}`,
                            }}>
                                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.3rem' }}>{g.name}</div>
                                <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem' }}>
                                    <span style={{ fontSize: '1.5rem', fontWeight: 700 }}>{g.price.toLocaleString()}</span>
                                    <span style={{ color: changeColor(g.change_pct), fontWeight: 600, fontSize: '0.9rem' }}>
                                        {g.change_pct > 0 ? '+' : ''}{g.change_pct}%
                                    </span>
                                </div>
                                <Sparkline data={g.sparkline} color={g.change_pct >= 0 ? '#10b981' : '#ef4444'} width={160} height={28} />
                            </div>
                        ))}
                    </div>

                    {/* Global Indices by Region */}
                    {regions.map(region => {
                        const regionIndices = data.indices.filter(i => i.region === region)
                        if (regionIndices.length === 0) return null
                        return (
                            <div key={region} style={{ marginBottom: '1.5rem' }}>
                                <h2 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '0.8rem', color: 'var(--text-muted)', letterSpacing: '1px', textTransform: 'uppercase' }}>{region === 'EU' ? 'Europe' : region}</h2>
                                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
                                    {regionIndices.map(idx => (
                                        <div key={idx.ticker} className="glass-panel" style={{ padding: '1.2rem' }}>
                                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                                <div>
                                                    <div style={{ fontWeight: 700, fontSize: '1.1rem' }}>{idx.name}</div>
                                                    <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem', marginTop: '0.3rem' }}>
                                                        <span style={{ fontSize: '1.3rem', fontWeight: 600 }}>{idx.price.toLocaleString()}</span>
                                                        <span style={{ color: changeColor(idx.change_pct), fontWeight: 600 }}>
                                                            {idx.change_pct > 0 ? '+' : ''}{idx.change_pct}%
                                                        </span>
                                                    </div>
                                                </div>
                                                <Sparkline data={idx.sparkline} color={idx.change_pct >= 0 ? '#10b981' : '#ef4444'} width={100} height={32} />
                                            </div>
                                            <div style={{ display: 'flex', gap: '1.2rem', marginTop: '0.6rem', fontSize: '0.82rem' }}>
                                                <div>
                                                    <span style={{ color: 'var(--text-muted)' }}>1Y </span>
                                                    <span style={{ fontWeight: 600, color: changeColor(idx.return_1y) }}>
                                                        {idx.return_1y != null ? `${idx.return_1y > 0 ? '+' : ''}${idx.return_1y}%` : 'N/A'}
                                                    </span>
                                                </div>
                                                <div>
                                                    <span style={{ color: 'var(--text-muted)' }}>5Y CAGR </span>
                                                    <span style={{ fontWeight: 600, color: changeColor(idx.return_5y) }}>
                                                        {idx.return_5y != null ? `${idx.return_5y > 0 ? '+' : ''}${idx.return_5y}%` : 'N/A'}
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )
                    })}
                </>
            )}
        </>
    )
}

// ─── 2. COMMODITY TRACKER ───────────────────────────────────────
export function CommodityTracker() {
    const [data, setData] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetch('http://127.0.0.1:8001/api/commodities')
            .then(r => r.json())
            .then(d => { setData(d); setLoading(false) })
            .catch(() => setLoading(false))
    }, [])

    const changeColor = (v) => v > 0 ? 'var(--profit-green)' : v < 0 ? '#ef4444' : 'var(--text-muted)'
    const fmtReturn = (v) => v !== null && v !== undefined ? `${v > 0 ? '+' : ''}${v}%` : 'N/A'

    return (
        <>
            <header>
                <h1>Commodity Tracker</h1>
                <p className="subtitle">Live prices for metals, energy, and agriculture commodities with historical returns.</p>
            </header>

            {loading ? (
                <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                    <h3>Loading commodity data...</h3>
                </div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1rem' }}>
                    {data.map(c => (
                        <div key={c.ticker} className="glass-panel" style={{
                            padding: '1.3rem',
                            borderLeft: `3px solid ${c.color}`,
                        }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                <div>
                                    <div style={{ fontWeight: 700, fontSize: '1.15rem' }}>{c.name}</div>
                                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{c.unit}</div>
                                </div>
                                <Sparkline data={c.sparkline} color={c.color} width={100} height={30} />
                            </div>
                            <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.6rem', marginTop: '0.8rem' }}>
                                <span style={{ fontSize: '1.6rem', fontWeight: 700 }}>${c.price.toLocaleString()}</span>
                                <span style={{ color: changeColor(c.day_change), fontWeight: 600 }}>
                                    {c.day_change > 0 ? '+' : ''}{c.day_change}%
                                </span>
                            </div>
                            <div style={{ display: 'flex', gap: '1.2rem', marginTop: '0.8rem', fontSize: '0.85rem' }}>
                                <div>
                                    <span style={{ color: 'var(--text-muted)' }}>1M </span>
                                    <span style={{ fontWeight: 600, color: changeColor(c.return_1m) }}>{fmtReturn(c.return_1m)}</span>
                                </div>
                                <div>
                                    <span style={{ color: 'var(--text-muted)' }}>1Y </span>
                                    <span style={{ fontWeight: 600, color: changeColor(c.return_1y) }}>{fmtReturn(c.return_1y)}</span>
                                </div>
                                <div>
                                    <span style={{ color: 'var(--text-muted)' }}>5Y </span>
                                    <span style={{ fontWeight: 600, color: changeColor(c.return_5y) }}>{fmtReturn(c.return_5y)}</span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </>
    )
}

// ─── 3. FOREX MONITOR ───────────────────────────────────────────
export function ForexMonitor() {
    const [data, setData] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetch('http://127.0.0.1:8001/api/forex')
            .then(r => r.json())
            .then(d => { setData(d); setLoading(false) })
            .catch(() => setLoading(false))
    }, [])

    const changeColor = (v) => v > 0 ? 'var(--profit-green)' : v < 0 ? '#ef4444' : 'var(--text-muted)'

    return (
        <>
            <header>
                <h1>Forex Monitor</h1>
                <p className="subtitle">Major currency pairs — rates, daily change, and 1-month trend lines.</p>
            </header>

            <div className="glass-panel" style={{ padding: '1.5rem' }}>
                {loading ? (
                    <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                        <h3>Loading forex data...</h3>
                    </div>
                ) : (
                    <div className="data-table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Pair</th>
                                    <th>Rate</th>
                                    <th>Day</th>
                                    <th>1M</th>
                                    <th>1Y</th>
                                    <th>5Y CAGR</th>
                                    <th style={{ textAlign: 'right' }}>Trend (1M)</th>
                                </tr>
                            </thead>
                            <tbody>
                                {data.map(p => (
                                    <tr key={p.ticker}>
                                        <td>
                                            <div style={{ fontWeight: 700, fontSize: '1.05rem' }}>{p.name}</div>
                                            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{p.base} → {p.quote}</div>
                                        </td>
                                        <td style={{ fontWeight: 700, fontSize: '1.15rem' }}>{p.rate}</td>
                                        <td style={{ color: changeColor(p.day_change), fontWeight: 600 }}>
                                            {p.day_change > 0 ? '+' : ''}{p.day_change.toFixed(2)}%
                                        </td>
                                        <td style={{ color: changeColor(p.month_change), fontWeight: 600 }}>
                                            {p.month_change > 0 ? '+' : ''}{p.month_change}%
                                        </td>
                                        <td style={{ color: changeColor(p.year_change), fontWeight: 600 }}>
                                            {p.year_change !== null ? `${p.year_change > 0 ? '+' : ''}${p.year_change}%` : 'N/A'}
                                        </td>
                                        <td style={{ color: changeColor(p.return_5y), fontWeight: 600 }}>
                                            {p.return_5y !== null ? `${p.return_5y > 0 ? '+' : ''}${p.return_5y}%` : 'N/A'}
                                        </td>
                                        <td style={{ textAlign: 'right' }}>
                                            <Sparkline data={p.sparkline} color={p.month_change >= 0 ? '#10b981' : '#ef4444'} width={120} height={28} />
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </>
    )
}

// ─── 4. CORRELATION MATRIX ──────────────────────────────────────
export function CorrelationMatrix() {
    const [data, setData] = useState({ labels: [], matrix: [] })
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetch('http://127.0.0.1:8001/api/correlation')
            .then(r => r.json())
            .then(d => { setData(d); setLoading(false) })
            .catch(() => setLoading(false))
    }, [])

    // Color from -1 (red) through 0 (neutral) to +1 (green)
    const corrColor = (v) => {
        if (v >= 0.7) return 'rgba(16, 185, 129, 0.7)'
        if (v >= 0.4) return 'rgba(16, 185, 129, 0.35)'
        if (v >= 0.1) return 'rgba(16, 185, 129, 0.15)'
        if (v >= -0.1) return 'rgba(255, 255, 255, 0.05)'
        if (v >= -0.4) return 'rgba(239, 68, 68, 0.15)'
        if (v >= -0.7) return 'rgba(239, 68, 68, 0.35)'
        return 'rgba(239, 68, 68, 0.7)'
    }

    return (
        <>
            <header>
                <h1>Correlation Matrix</h1>
                <p className="subtitle">Cross-asset correlation based on 1-year daily returns — stocks, bonds, commodities, crypto, and currencies.</p>
            </header>

            <div className="glass-panel" style={{ padding: '1.5rem', overflow: 'auto' }}>
                {loading ? (
                    <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                        <h3>Computing correlation matrix...</h3>
                        <p>Fetching 1-year daily returns for 12 asset classes</p>
                    </div>
                ) : (
                    <div style={{ overflowX: 'auto' }}>
                        <table style={{ borderCollapse: 'collapse', fontSize: '0.8rem' }}>
                            <thead>
                                <tr>
                                    <th style={{ padding: '0.6rem', minWidth: '90px' }}></th>
                                    {data.labels.map(l => (
                                        <th key={l} style={{
                                            padding: '0.5rem 0.4rem',
                                            writingMode: 'vertical-lr',
                                            transform: 'rotate(180deg)',
                                            textAlign: 'left',
                                            fontWeight: 600,
                                            fontSize: '0.75rem',
                                            minWidth: '45px',
                                            maxWidth: '45px',
                                        }}>{l}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {data.matrix.map((row, ri) => (
                                    <tr key={data.labels[ri]}>
                                        <td style={{
                                            fontWeight: 600,
                                            padding: '0.5rem 0.6rem',
                                            whiteSpace: 'nowrap',
                                            fontSize: '0.82rem',
                                        }}>{data.labels[ri]}</td>
                                        {row.map((val, ci) => (
                                            <td key={ci} style={{
                                                background: corrColor(val),
                                                textAlign: 'center',
                                                padding: '0.4rem',
                                                fontWeight: ri === ci ? 700 : 500,
                                                color: ri === ci ? 'var(--text-muted)' : 'white',
                                                fontSize: '0.78rem',
                                                border: '1px solid rgba(255,255,255,0.05)',
                                                minWidth: '45px',
                                            }}>
                                                {val != null ? val.toFixed(2) : '—'}
                                            </td>
                                        ))}
                                    </tr>
                                ))}
                            </tbody>
                        </table>

                        {/* Legend */}
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '1.5rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                            <span>Strong −</span>
                            <div style={{ display: 'flex', gap: '2px' }}>
                                {[-0.9, -0.5, -0.2, 0, 0.2, 0.5, 0.9].map(v => (
                                    <div key={v} style={{
                                        width: '28px', height: '14px',
                                        background: corrColor(v),
                                        borderRadius: '2px',
                                    }} />
                                ))}
                            </div>
                            <span>Strong +</span>
                        </div>
                    </div>
                )}
            </div>
        </>
    )
}

// ─── 5. NIFTY 500 SECTOR HEATMAP ────────────────────────────────
export function Nifty500Heatmap() {
    const [data, setData] = useState({ sectors: [], years: [] })
    const [loading, setLoading] = useState(true)
    const [sortBy, setSortBy] = useState('cagr_5y')

    useEffect(() => {
        fetch('http://127.0.0.1:8001/api/nifty500')
            .then(r => r.json())
            .then(d => { setData(d); setLoading(false) })
            .catch(() => setLoading(false))
    }, [])

    const changeColor = (v) => v > 0 ? 'var(--profit-green)' : v < 0 ? '#ef4444' : 'var(--text-muted)'

    const getBgColor = (val) => {
        if (val === undefined || val === null) return 'transparent'
        if (val >= 40) return 'rgba(16, 185, 129, 0.55)'
        if (val >= 20) return 'rgba(16, 185, 129, 0.35)'
        if (val >= 10) return 'rgba(16, 185, 129, 0.2)'
        if (val >= 0) return 'rgba(16, 185, 129, 0.08)'
        if (val >= -10) return 'rgba(239, 68, 68, 0.1)'
        if (val >= -20) return 'rgba(239, 68, 68, 0.25)'
        return 'rgba(239, 68, 68, 0.45)'
    }

    const sortedSectors = [...data.sectors].sort((a, b) => {
        const av = a[sortBy] ?? -999
        const bv = b[sortBy] ?? -999
        return bv - av
    })

    const sortOptions = [
        { key: 'cagr_5y', label: '5Y CAGR' },
        { key: 'return_1y', label: '1Y Return' },
    ]

    return (
        <>
            <header>
                <h1>Nifty 500 — Sector Performance</h1>
                <p className="subtitle">Annual returns for 15 Nifty sectoral indices, sorted by growth. Color intensity reflects magnitude.</p>
            </header>

            {/* Sort Pills */}
            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem' }}>
                {sortOptions.map(opt => (
                    <button key={opt.key} onClick={() => setSortBy(opt.key)} style={{
                        padding: '0.5rem 1.2rem',
                        borderRadius: '999px',
                        border: sortBy === opt.key ? '1px solid var(--accent-blue)' : '1px solid rgba(255,255,255,0.1)',
                        background: sortBy === opt.key ? 'rgba(59, 130, 246, 0.2)' : 'rgba(255,255,255,0.03)',
                        color: sortBy === opt.key ? 'var(--accent-blue)' : 'var(--text-muted)',
                        cursor: 'pointer',
                        fontWeight: 600,
                        fontSize: '0.85rem',
                    }}>
                        Sort by {opt.label}
                    </button>
                ))}
            </div>

            <div className="glass-panel" style={{ padding: '1.5rem', overflow: 'auto' }}>
                {loading ? (
                    <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                        <h3>Loading Nifty sector data...</h3>
                        <p>Fetching 15 sectoral indices from NSE</p>
                    </div>
                ) : (
                    <div className="data-table-container" style={{ overflowX: 'auto' }}>
                        <table style={{ fontSize: '0.85rem' }}>
                            <thead>
                                <tr>
                                    <th style={{ minWidth: '30px' }}>#</th>
                                    <th style={{ minWidth: '140px' }}>Sector</th>
                                    <th>Level</th>
                                    <th style={{ cursor: 'pointer' }} onClick={() => setSortBy('return_1y')}>
                                        1Y {sortBy === 'return_1y' ? '▼' : ''}
                                    </th>
                                    <th style={{ cursor: 'pointer' }} onClick={() => setSortBy('cagr_5y')}>
                                        5Y CAGR {sortBy === 'cagr_5y' ? '▼' : ''}
                                    </th>
                                    {data.years.map(y => (
                                        <th key={y} style={{ minWidth: '65px', textAlign: 'center' }}>{y}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {sortedSectors.map((s, i) => (
                                    <tr key={s.ticker}>
                                        <td style={{
                                            fontWeight: 700,
                                            color: i < 3 ? '#fbbf24' : 'var(--text-muted)',
                                            fontSize: '0.9rem',
                                        }}>
                                            {i < 3 ? ['🥇', '🥈', '🥉'][i] : i + 1}
                                        </td>
                                        <td>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                                <div style={{
                                                    width: '4px', height: '24px',
                                                    background: s.color,
                                                    borderRadius: '2px',
                                                }} />
                                                <div>
                                                    <div style={{ fontWeight: 700, fontSize: '0.95rem' }}>{s.sector}</div>
                                                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{s.ticker}</div>
                                                </div>
                                            </div>
                                        </td>
                                        <td style={{ fontWeight: 600 }}>{s.price?.toLocaleString()}</td>
                                        <td style={{ fontWeight: 700, color: changeColor(s.return_1y), fontSize: '0.95rem' }}>
                                            {s.return_1y != null ? `${s.return_1y > 0 ? '+' : ''}${s.return_1y}%` : 'N/A'}
                                        </td>
                                        <td style={{ fontWeight: 700, color: changeColor(s.cagr_5y), fontSize: '0.95rem' }}>
                                            {s.cagr_5y != null ? `${s.cagr_5y > 0 ? '+' : ''}${s.cagr_5y}%` : 'N/A'}
                                        </td>
                                        {data.years.map(y => {
                                            const val = s.returns[y]
                                            return (
                                                <td key={y} style={{
                                                    textAlign: 'center',
                                                    background: getBgColor(val),
                                                    fontWeight: 600,
                                                    color: val != null ? (val >= 0 ? '#4ade80' : '#f87171') : 'var(--text-muted)',
                                                    fontSize: '0.82rem',
                                                }}>
                                                    {val != null ? `${val > 0 ? '+' : ''}${val}%` : '—'}
                                                </td>
                                            )
                                        })}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </>
    )
}

// ======================== ANALYSIS PAGES ========================

// Shared analysis card renderer
function AnalysisPage({ title, subtitle, philosophy, sortKey, sortDesc = true, explanationFn }) {
    const [region, setRegion] = useState('US')
    const [data, setData] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        setLoading(true)
        setData(null)
        fetch(`http://127.0.0.1:8001/api/analysis/${region}`)
            .then(r => r.json())
            .then(d => { setData(d); setLoading(false) })
            .catch(() => setLoading(false))
    }, [region])

    const changeColor = (v) => v > 0 ? 'var(--profit-green)' : v < 0 ? '#ef4444' : 'var(--text-muted)'
    const fmtPct = (v) => v != null ? `${v > 0 ? '+' : ''}${v}%` : 'N/A'
    const fmtCcy = (ccy) => ccy === 'EUR' ? '€' : ccy === 'GBP' ? '£' : ccy === 'INR' ? '₹' : '$'

    const sorted = data?.etfs
        ? [...data.etfs].sort((a, b) => {
            const av = a[sortKey] ?? -999
            const bv = b[sortKey] ?? -999
            return sortDesc ? bv - av : av - bv
        }).slice(0, 5)
        : []

    const regionLabels = { US: '🇺🇸 United States', EU: '🇪🇺 Europe', India: '🇮🇳 India' }

    return (
        <>
            <header>
                <h1>{title}</h1>
                <p className="subtitle">{subtitle}</p>
            </header>

            {/* Philosophy Box */}
            <div className="glass-panel" style={{ padding: '1.2rem 1.5rem', marginBottom: '1.5rem', borderLeft: '4px solid var(--accent-blue)' }}>
                <div style={{ fontSize: '0.8rem', color: 'var(--accent-blue)', fontWeight: 700, marginBottom: '0.3rem', textTransform: 'uppercase' }}>Investment Philosophy</div>
                <div style={{ color: 'var(--text-muted)', fontSize: '0.95rem', lineHeight: 1.6 }}>{philosophy}</div>
            </div>

            {/* Region Selector */}
            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem' }}>
                {['US', 'EU', 'India'].map(r => (
                    <button key={r} onClick={() => setRegion(r)} style={{
                        background: region === r ? 'var(--accent-blue)' : 'rgba(255,255,255,0.06)',
                        border: region === r ? 'none' : '1px solid var(--border-glass)',
                        color: region === r ? 'white' : 'var(--text-muted)',
                        padding: '0.6rem 1.5rem', borderRadius: '8px', cursor: 'pointer',
                        fontWeight: 600, fontSize: '0.9rem', fontFamily: 'Outfit',
                    }}>{regionLabels[r]}</button>
                ))}
            </div>

            {loading ? (
                <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                    <h3>Analyzing {regionLabels[region]} ETFs...</h3>
                    <p style={{ fontSize: '0.9rem' }}>Fetching 5-year data from Yahoo Finance. This may take 30-60 seconds.</p>
                </div>
            ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    {sorted.map((etf, idx) => (
                        <div key={etf.ticker} className="glass-panel" style={{ padding: '1.5rem' }}>
                            {/* Rank + Header */}
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                                <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
                                    <div style={{
                                        width: '40px', height: '40px', borderRadius: '10px',
                                        background: idx === 0 ? 'linear-gradient(135deg, #fbbf24, #f59e0b)' :
                                            idx === 1 ? 'linear-gradient(135deg, #94a3b8, #64748b)' :
                                                idx === 2 ? 'linear-gradient(135deg, #d97706, #92400e)' :
                                                    'rgba(255,255,255,0.06)',
                                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                                        fontWeight: 800, fontSize: '1.1rem',
                                        color: idx < 3 ? '#1e293b' : 'var(--text-muted)',
                                    }}>#{idx + 1}</div>
                                    <div>
                                        <div style={{ fontWeight: 700, fontSize: '1.15rem' }}>{etf.name}</div>
                                        <div style={{ display: 'flex', gap: '0.6rem', alignItems: 'center', marginTop: '0.2rem' }}>
                                            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{etf.ticker}</span>
                                            <span style={{
                                                fontSize: '0.7rem', padding: '0.15rem 0.5rem', borderRadius: '999px',
                                                background: 'rgba(59, 130, 246, 0.15)', color: 'var(--accent-blue)',
                                            }}>{etf.focus}</span>
                                        </div>
                                    </div>
                                </div>
                                <div style={{ textAlign: 'right' }}>
                                    <div style={{ fontSize: '1.4rem', fontWeight: 700 }}>
                                        {fmtCcy(etf.currency)}{etf.price?.toLocaleString()}
                                    </div>
                                </div>
                            </div>

                            {/* Metrics Grid */}
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '0.6rem', marginBottom: '1rem' }}>
                                {[
                                    { label: '3M Return', value: fmtPct(etf.return_3m), color: changeColor(etf.return_3m) },
                                    { label: '1Y Return', value: fmtPct(etf.return_1y), color: changeColor(etf.return_1y) },
                                    { label: '5Y CAGR', value: fmtPct(etf.cagr_5y), color: changeColor(etf.cagr_5y) },
                                    { label: 'Sharpe Ratio', value: etf.sharpe?.toFixed(2) || 'N/A', color: etf.sharpe > 0.5 ? 'var(--profit-green)' : '#ef4444' },
                                    { label: 'Volatility', value: `${etf.volatility}%`, color: etf.volatility < 15 ? 'var(--profit-green)' : etf.volatility < 25 ? '#fbbf24' : '#ef4444' },
                                    { label: 'Max Drawdown', value: `${etf.max_drawdown}%`, color: '#ef4444' },
                                    { label: 'Div. Yield', value: etf.dividend_yield ? `${etf.dividend_yield}%` : 'N/A', color: '#fbbf24' },
                                    { label: 'Expense Ratio', value: etf.expense_ratio != null ? `${etf.expense_ratio}%` : 'N/A', color: 'var(--text-muted)' },
                                ].map(m => (
                                    <div key={m.label} style={{ background: 'rgba(255,255,255,0.03)', borderRadius: '6px', padding: '0.5rem 0.7rem' }}>
                                        <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginBottom: '0.15rem', textTransform: 'uppercase' }}>{m.label}</div>
                                        <div style={{ fontWeight: 700, fontSize: '0.95rem', color: m.color }}>{m.value}</div>
                                    </div>
                                ))}
                            </div>

                            {/* Layman Explanation */}
                            <div style={{
                                background: 'rgba(59, 130, 246, 0.05)', borderRadius: '8px', padding: '0.8rem 1rem',
                                borderLeft: '3px solid rgba(59, 130, 246, 0.3)',
                            }}>
                                <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--accent-blue)', marginBottom: '0.3rem' }}>💡 Why This ETF?</div>
                                <div style={{ fontSize: '0.88rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>
                                    {explanationFn(etf, idx)}
                                </div>
                            </div>
                        </div>
                    ))}

                    {sorted.length === 0 && !loading && (
                        <div className="glass-panel" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                            No data available for this region.
                        </div>
                    )}
                </div>
            )}
        </>
    )
}

// ---------- Page 1: Momentum Leaders ----------
export function MomentumAnalysis() {
    const explain = (etf) => {
        const parts = []
        if (etf.return_3m > 5) parts.push(`This ETF has surged ${etf.return_3m}% in just 3 months, showing very strong upward momentum.`)
        else if (etf.return_3m > 0) parts.push(`With a ${etf.return_3m}% gain over 3 months, this ETF is on a steady uptrend.`)
        else parts.push(`Despite a ${etf.return_3m}% dip over 3 months, the longer-term trend may offer a buying opportunity.`)

        if (etf.return_1y > 20) parts.push(`Over the past year, it returned ${etf.return_1y}%, significantly outperforming the broad market.`)
        else if (etf.return_1y > 0) parts.push(`Its 1-year return of ${etf.return_1y}% shows steady growth.`)

        parts.push(`It focuses on "${etf.focus}" — a sector that's been gaining traction with institutional investors.`)
        if (etf.volatility < 18) parts.push(`With ${etf.volatility}% volatility, it's relatively smooth for a momentum pick.`)
        return parts.join(' ')
    }

    return <AnalysisPage
        title="📈 Momentum Leaders"
        subtitle="ETFs with the strongest recent price momentum — riding the trend."
        philosophy="Momentum investing follows the principle that assets that have been going up tend to keep going up. This analysis ranks ETFs by their combined 3-month and 1-year returns — identifying the ones with the strongest current trajectory. Think of it as 'buying what's hot.' While riskier than other strategies, momentum can capture powerful trends early."
        sortKey="return_3m" sortDesc={true}
        explanationFn={explain}
    />
}

// ---------- Page 2: Growth Champions ----------
export function GrowthAnalysis() {
    const explain = (etf) => {
        const parts = []
        if (etf.cagr_5y > 15) parts.push(`With a ${etf.cagr_5y}% compound annual growth over 5 years, $10,000 invested in 2021 would be worth roughly $${Math.round(10000 * Math.pow(1 + etf.cagr_5y / 100, 5)).toLocaleString()} today.`)
        else if (etf.cagr_5y > 8) parts.push(`A ${etf.cagr_5y}% annual growth over 5 years shows consistent compounding — well above inflation.`)
        else parts.push(`The ${etf.cagr_5y}% 5Y CAGR is moderate, but may suit conservative growth investors.`)

        parts.push(`Focused on "${etf.focus}", this ETF captures a sector with long-term structural tailwinds.`)
        if (etf.max_drawdown > -30) parts.push(`Its worst peak-to-trough drop was ${etf.max_drawdown}%, which means it recovered from major downturns.`)
        if (etf.expense_ratio != null && etf.expense_ratio < 0.2) parts.push(`At just ${etf.expense_ratio}% expense ratio, it's very cost-efficient.`)
        return parts.join(' ')
    }

    return <AnalysisPage
        title="🚀 Growth Champions"
        subtitle="ETFs with the highest long-term compounding — the power of CAGR."
        philosophy="Growth investing focuses on assets that have delivered the highest compound annual growth rate (CAGR) over 5 years. Unlike momentum (which looks at recent trends), this analysis rewards consistency over time. A high CAGR means your money doubles faster. For example, a 15% CAGR doubles your money in ~5 years, while a 7% CAGR takes ~10 years."
        sortKey="cagr_5y" sortDesc={true}
        explanationFn={explain}
    />
}

// ---------- Page 3: Risk-Adjusted Returns ----------
export function RiskAdjustedAnalysis() {
    const explain = (etf) => {
        const parts = []
        if (etf.sharpe > 0.8) parts.push(`With a Sharpe ratio of ${etf.sharpe}, this ETF delivers excellent returns for the risk it takes — significantly above the 0.5 threshold that's considered "good."`)
        else if (etf.sharpe > 0.4) parts.push(`A Sharpe ratio of ${etf.sharpe} means this ETF offers decent returns relative to its risk level.`)
        else parts.push(`A Sharpe ratio of ${etf.sharpe} suggests the returns don't fully compensate for the risk involved.`)

        if (etf.volatility < 15) parts.push(`Its ${etf.volatility}% volatility makes it one of the smoother rides — you won't lose sleep at night.`)
        else if (etf.volatility < 25) parts.push(`Its ${etf.volatility}% volatility is moderate — expect some ups and downs, but nothing extreme.`)
        else parts.push(`${etf.volatility}% volatility means bigger swings — suitable for investors who can stomach short-term drops.`)

        parts.push(`The worst it ever dropped from peak was ${etf.max_drawdown}%.`)
        if (etf.cagr_5y > 10) parts.push(`Despite being risk-efficient, it still delivered a strong ${etf.cagr_5y}% annual growth.`)
        return parts.join(' ')
    }

    return <AnalysisPage
        title="🛡️ Risk-Adjusted Returns"
        subtitle="ETFs that give you the best bang for your buck per unit of risk — the Sharpe Ratio ranking."
        philosophy="The Sharpe Ratio measures how much excess return you get for each unit of risk (volatility). A Sharpe of 1.0+ is excellent — it means every 1% of risk translates to 1%+ of extra return above risk-free rates. This analysis is ideal for investors who want growth but don't want to ride a roller-coaster. It answers: 'Which ETFs give the smoothest path to profit?'"
        sortKey="sharpe" sortDesc={true}
        explanationFn={explain}
    />
}

// ---------- Page 4: Income & Dividends ----------
export function IncomeAnalysis() {
    const explain = (etf) => {
        const parts = []
        if (etf.dividend_yield > 3) parts.push(`With a ${etf.dividend_yield}% dividend yield, investing $100,000 here would generate roughly $${Math.round(1000 * etf.dividend_yield).toLocaleString()} per year in passive income — paid out regularly.`)
        else if (etf.dividend_yield > 1) parts.push(`A ${etf.dividend_yield}% dividend yield provides modest but reliable income while your capital grows.`)
        else parts.push(`This ETF has a low dividend yield (${etf.dividend_yield}%) — it's more of a growth play than an income generator.`)

        if (etf.cagr_5y > 5) parts.push(`Beyond dividends, it also grew ${etf.cagr_5y}% per year — so you get income PLUS capital appreciation.`)
        if (etf.volatility < 18) parts.push(`Its low volatility (${etf.volatility}%) makes it a steady holding for retirees or conservative investors.`)
        parts.push(`Focused on "${etf.focus}".`)
        return parts.join(' ')
    }

    return <AnalysisPage
        title="💰 Income & Dividends"
        subtitle="ETFs that pay you to hold them — sorted by dividend yield."
        philosophy="Income investing prioritizes regular cash payouts (dividends) over price growth. These ETFs pay you a percentage of your investment back each quarter or year as income. This approach is ideal for retirees, people building passive income, or those who want their portfolio to 'pay rent.' A $100,000 investment in a 4% yield ETF generates $4,000/year without selling anything."
        sortKey="dividend_yield" sortDesc={true}
        explanationFn={explain}
    />
}

// ======================== MARKET NEWS ========================
export function MarketNews() {
    const [region, setRegion] = useState('US')
    const [news, setNews] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        setLoading(true)
        setNews([])
        fetch(`http://127.0.0.1:8001/api/news/${region}`)
            .then(r => r.json())
            .then(d => { setNews(d); setLoading(false) })
            .catch(() => setLoading(false))
    }, [region])

    const regionLabels = { US: '🇺🇸 United States', EU: '🇪🇺 Europe', India: '🇮🇳 India' }

    return (
        <>
            <header>
                <h1>📰 Market News</h1>
                <p className="subtitle">Latest headlines from major financial sources affecting markets and sectors.</p>
            </header>

            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem' }}>
                {['US', 'EU', 'India'].map(r => (
                    <button key={r} onClick={() => setRegion(r)} style={{
                        background: region === r ? 'var(--accent-blue)' : 'rgba(255,255,255,0.06)',
                        border: region === r ? 'none' : '1px solid var(--border-glass)',
                        color: region === r ? 'white' : 'var(--text-muted)',
                        padding: '0.6rem 1.5rem', borderRadius: '8px', cursor: 'pointer',
                        fontWeight: 600, fontSize: '0.9rem', fontFamily: 'Outfit',
                    }}>{regionLabels[r]}</button>
                ))}
            </div>

            {loading ? (
                <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                    <h3>Loading {regionLabels[region]} news...</h3>
                </div>
            ) : news.length === 0 ? (
                <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                    <h3>No news available</h3>
                </div>
            ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
                    {news.map((item, idx) => (
                        <a key={idx} href={item.link} target="_blank" rel="noopener noreferrer"
                            className="glass-panel" style={{
                                padding: '1.2rem 1.5rem', textDecoration: 'none', color: 'inherit',
                                display: 'block', transition: 'border-color 0.2s, transform 0.2s',
                            }}
                            onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--accent-blue)'; e.currentTarget.style.transform = 'translateX(4px)' }}
                            onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border-glass)'; e.currentTarget.style.transform = 'translateX(0)' }}
                        >
                            <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
                                {item.thumbnail && (
                                    <img src={item.thumbnail} alt="" style={{
                                        width: '80px', height: '60px', borderRadius: '6px',
                                        objectFit: 'cover', flexShrink: 0,
                                    }} />
                                )}
                                <div style={{ flex: 1 }}>
                                    <div style={{ fontWeight: 700, fontSize: '1rem', marginBottom: '0.3rem', lineHeight: 1.4 }}>
                                        {item.title}
                                    </div>
                                    <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
                                        <span style={{ fontSize: '0.75rem', color: 'var(--accent-blue)', fontWeight: 600 }}>
                                            {item.publisher}
                                        </span>
                                        <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                                            {item.date}
                                        </span>
                                        {item.related && item.related.length > 0 && (
                                            <div style={{ display: 'flex', gap: '0.3rem' }}>
                                                {item.related.slice(0, 4).map(t => (
                                                    <span key={t} style={{
                                                        fontSize: '0.6rem', padding: '0.1rem 0.35rem', borderRadius: '4px',
                                                        background: 'rgba(255,255,255,0.06)', color: 'var(--text-muted)',
                                                    }}>{t}</span>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                </div>
                                <span style={{ color: 'var(--text-muted)', fontSize: '1.2rem', flexShrink: 0 }}>→</span>
                            </div>
                        </a>
                    ))}
                </div>
            )}
        </>
    )
}

// ======================== ALLOCATION ADVISOR ========================
const PIE_COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#6b7280']

export function AllocationAdvisor() {
    const [data, setData] = useState(null)
    const [loading, setLoading] = useState(true)
    const [expandedStrategy, setExpandedStrategy] = useState(null)

    useEffect(() => {
        fetch('http://127.0.0.1:8001/api/allocation')
            .then(r => r.json())
            .then(d => { setData(d); setLoading(false) })
            .catch(() => setLoading(false))
    }, [])

    if (loading) return (
        <>
            <header><h1>🎯 Allocation Advisor</h1><p className="subtitle">Loading allocation data...</p></header>
            <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                <h3>Analyzing portfolio allocations...</h3>
            </div>
        </>
    )

    const recPieData = data?.recommended
        ? Object.entries(data.recommended).filter(([, v]) => v > 0).map(([name, value]) => ({ name, value }))
        : []
    const userPieData = data?.user_allocation
        ? Object.entries(data.user_allocation).filter(([, v]) => v > 0).map(([name, value]) => ({ name, value }))
        : []

    return (
        <>
            <header>
                <h1>🎯 Allocation Advisor</h1>
                <p className="subtitle">Optimal portfolio allocation based on strategies from the world's best investors.</p>
            </header>

            {/* Pie Charts Section */}
            <div style={{ display: 'grid', gridTemplateColumns: data?.has_portfolio ? '1fr 1fr' : '1fr', gap: '1.5rem', marginBottom: '1.5rem' }}>
                {/* Recommended Allocation */}
                <div className="glass-panel" style={{ padding: '1.5rem' }}>
                    <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
                        <div style={{ fontSize: '1.1rem', fontWeight: 700 }}>✨ Recommended Allocation</div>
                        <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Average of 5 legendary investor strategies</div>
                    </div>
                    {recPieData.length > 0 ? (
                        <div style={{ height: 260, display: 'flex', justifyContent: 'center' }}>
                            <PieChart width={300} height={260}>
                                <Pie data={recPieData} cx="50%" cy="50%" innerRadius={60} outerRadius={90} dataKey="value" nameKey="name" paddingAngle={2} isAnimationActive={false}>
                                    {recPieData.map((entry, index) => <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />)}
                                </Pie>
                                <Tooltip formatter={(v) => `${v}%`} contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }} itemStyle={{ color: '#fff' }} />
                            </PieChart>
                        </div>
                    ) : (
                        <div style={{ height: 260, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>Loading chart...</div>
                    )}
                    {/* Legend */}
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.8rem', justifyContent: 'center', marginTop: '1rem' }}>
                        {recPieData.map((entry, i) => (
                            <div key={entry.name} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.82rem' }}>
                                <div style={{ width: 12, height: 12, borderRadius: '2px', background: PIE_COLORS[i % PIE_COLORS.length] }} />
                                <span style={{ color: 'var(--text-muted)' }}>{entry.name}</span>
                                <span style={{ fontWeight: 700 }}>{entry.value}%</span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* User's Allocation (if available) */}
                {data?.has_portfolio && (
                    <div className="glass-panel" style={{ padding: '1.5rem' }}>
                        <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
                            <div style={{ fontSize: '1.1rem', fontWeight: 700 }}>📊 Your Current Allocation</div>
                            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Based on your portfolio investments</div>
                        </div>
                        {userPieData.length > 0 ? (
                            <div style={{ height: 260, display: 'flex', justifyContent: 'center' }}>
                                <PieChart width={300} height={260}>
                                    <Pie data={userPieData} cx="50%" cy="50%" innerRadius={60} outerRadius={90} dataKey="value" nameKey="name" paddingAngle={2} isAnimationActive={false}>
                                        {userPieData.map((entry, i) => {
                                            const recIdx = recPieData.findIndex(r => r.name === entry.name)
                                            return <Cell key={`cell-u-${i}`} fill={PIE_COLORS[recIdx >= 0 ? recIdx : i % PIE_COLORS.length]} />
                                        })}
                                    </Pie>
                                    <Tooltip formatter={(v) => `${v}%`} contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }} itemStyle={{ color: '#fff' }} />
                                </PieChart>
                            </div>
                        ) : (
                            <div style={{ height: 260, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>No allocation data</div>
                        )}
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.8rem', justifyContent: 'center', marginTop: '1rem' }}>
                            {userPieData.map((entry, i) => {
                                const recIdx = recPieData.findIndex(r => r.name === entry.name)
                                return (
                                    <div key={entry.name} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.82rem' }}>
                                        <div style={{ width: 12, height: 12, borderRadius: '2px', background: PIE_COLORS[recIdx >= 0 ? recIdx : i % PIE_COLORS.length] }} />
                                        <span style={{ color: 'var(--text-muted)' }}>{entry.name}</span>
                                        <span style={{ fontWeight: 700 }}>{entry.value}%</span>
                                    </div>
                                )
                            })}
                        </div>
                    </div>
                )}
            </div>

            {/* Comparison Bar */}
            {data?.has_portfolio && data?.recommended && (
                <div className="glass-panel" style={{ padding: '1.2rem 1.5rem', marginBottom: '1.5rem' }}>
                    <div style={{ fontSize: '0.8rem', fontWeight: 700, marginBottom: '0.8rem', textTransform: 'uppercase', color: 'var(--accent-blue)' }}>Allocation Comparison</div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                        {Object.entries(data.recommended).map(([cat, rec], i) => {
                            const actual = data.user_allocation?.[cat] || 0
                            const diff = actual - rec
                            return (
                                <div key={cat} style={{ display: 'grid', gridTemplateColumns: '160px 1fr 70px 70px 70px', gap: '0.5rem', alignItems: 'center' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.82rem' }}>
                                        <div style={{ width: 8, height: 8, borderRadius: '50%', background: PIE_COLORS[i] }} />
                                        {cat}
                                    </div>
                                    <div style={{ height: '8px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', position: 'relative', overflow: 'hidden' }}>
                                        <div style={{ position: 'absolute', height: '100%', width: `${rec}%`, background: PIE_COLORS[i], opacity: 0.4, borderRadius: '4px' }} />
                                        <div style={{ position: 'absolute', height: '100%', width: `${actual}%`, background: PIE_COLORS[i], borderRadius: '4px' }} />
                                    </div>
                                    <div style={{ fontSize: '0.78rem', textAlign: 'right', color: 'var(--text-muted)' }}>Rec: {rec}%</div>
                                    <div style={{ fontSize: '0.78rem', textAlign: 'right', fontWeight: 600 }}>You: {actual}%</div>
                                    <div style={{ fontSize: '0.78rem', textAlign: 'right', fontWeight: 700, color: Math.abs(diff) > 10 ? '#ef4444' : Math.abs(diff) > 5 ? '#fbbf24' : 'var(--profit-green)' }}>
                                        {diff > 0 ? '+' : ''}{diff.toFixed(1)}%
                                    </div>
                                </div>
                            )
                        })}
                    </div>
                </div>
            )}

            {/* Suggestions */}
            <div className="glass-panel" style={{ padding: '1.2rem 1.5rem', marginBottom: '1.5rem', borderLeft: '4px solid var(--accent-blue)' }}>
                <div style={{ fontSize: '0.8rem', fontWeight: 700, marginBottom: '0.5rem', textTransform: 'uppercase', color: 'var(--accent-blue)' }}>💡 Personalized Suggestions</div>
                {data?.suggestions?.map((s, i) => (
                    <div key={i} style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.7, marginBottom: '0.3rem' }}>{s}</div>
                ))}
            </div>

            {/* Investor Strategies */}
            <div style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '0.8rem' }}>📚 Investment Strategies from the Masters</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                {data?.strategies?.map((strat, idx) => (
                    <div key={idx} className="glass-panel" style={{ padding: '1rem 1.3rem', cursor: 'pointer' }}
                        onClick={() => setExpandedStrategy(expandedStrategy === idx ? null : idx)}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <div>
                                <div style={{ fontWeight: 700, fontSize: '0.95rem' }}>{strat.name}</div>
                                <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '0.15rem' }}>{strat.philosophy}</div>
                            </div>
                            <span style={{ color: 'var(--text-muted)', fontSize: '1.2rem', transition: 'transform 0.2s', transform: expandedStrategy === idx ? 'rotate(180deg)' : 'rotate(0)' }}>▼</span>
                        </div>
                        {expandedStrategy === idx && (
                            <div style={{ marginTop: '0.8rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '0.5rem' }}>
                                {Object.entries(strat.allocation).filter(([, v]) => v > 0).map(([cat, val], i) => (
                                    <div key={cat} style={{ background: 'rgba(255,255,255,0.03)', borderRadius: '6px', padding: '0.5rem 0.7rem' }}>
                                        <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>{cat}</div>
                                        <div style={{ fontWeight: 700, fontSize: '1rem', color: PIE_COLORS[i % PIE_COLORS.length] }}>{val}%</div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </>
    )
}

export function BacktestView() {
    const [data, setData] = useState(null)
    const [loading, setLoading] = useState(true)
    const [period, setPeriod] = useState(5)
    const API = 'http://127.0.0.1:8001'

    useEffect(() => {
        setLoading(true)
        fetch(`${API}/api/backtest?period=${period}`)
            .then(r => r.json())
            .then(d => { setData(d); setLoading(false) })
            .catch(() => setLoading(false))
    }, [period])

    if (loading) return (
        <>
            <header><h1>Portfolio Backtest</h1><p className="subtitle">Simulating historical performance...</p></header>
            <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                <Rocket size={48} className="animate-pulse" style={{ color: 'var(--accent-blue)', opacity: 0.5, marginBottom: '1rem' }} />
                <h2>Running simulation...</h2>
                <p>fetching historical data for all holdings and compounding SIPs/Lump-sums.</p>
            </div>
        </>
    )

    if (!data || !data.history || data.history.length === 0) return (
        <>
            <header><h1>Portfolio Backtest</h1><p className="subtitle">Historical simulation.</p></header>
            <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center' }}>
                <AlertTriangle size={48} style={{ color: 'var(--text-muted)', opacity: 0.4, marginBottom: '1rem' }} />
                <h2 style={{ fontSize: '1.3rem', marginBottom: '0.5rem' }}>No data to backtest</h2>
                <p style={{ color: 'var(--text-muted)' }}>Add assets in the <a href="/portfolio" style={{ color: 'var(--accent-blue)' }}>Portfolio</a> page to see historical performance.</p>
            </div>
        </>
    )

    return (
        <>
            <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                    <h1>Portfolio Backtest</h1>
                    <p className="subtitle">Simulation of current holdings with SIP + Lump-sum contributions.</p>
                </div>
                <div style={{ display: 'flex', gap: '0.5rem', background: 'rgba(255,255,255,0.05)', padding: '0.3rem', borderRadius: '8px' }}>
                    {[1, 3, 5, 10].map(p => (
                        <button
                            key={p}
                            onClick={() => setPeriod(p)}
                            style={{
                                border: 'none',
                                background: period === p ? 'var(--accent-blue)' : 'transparent',
                                color: 'white',
                                padding: '0.4rem 1rem',
                                borderRadius: '6px',
                                cursor: 'pointer',
                                fontSize: '0.85rem',
                                fontWeight: 500
                            }}
                        >
                            {p}Y
                        </button>
                    ))}
                </div>
            </header>

            {/* Backtest Stats */}
            <div className="dashboard-grid">
                <style>{`
                    .backtest-stat-card {
                        transition: transform 0.2s;
                    }
                    .backtest-stat-card:hover {
                        transform: translateY(-5px);
                    }
                `}</style>
                <div className="metric-card glass-panel backtest-stat-card" style={{ borderLeft: '4px solid var(--accent-blue)' }}>
                    <span className="label">Final Portfolio Value</span>
                    <span className="value">${data.stats.final_value?.toLocaleString()}</span>
                    <span style={{ color: data.stats.absolute_return >= 0 ? 'var(--profit-green)' : '#ef4444', fontWeight: 600, fontSize: '0.85rem' }}>
                        {data.stats.absolute_return >= 0 ? '+' : ''}{data.stats.absolute_return}% Abs. Return
                    </span>
                </div>
                <div className="metric-card glass-panel backtest-stat-card" style={{ borderLeft: '4px solid var(--text-muted)' }}>
                    <span className="label">Benchmark Value (S&P 500)</span>
                    <span className="value">${data.stats.benchmark_value?.toLocaleString()}</span>
                    <span style={{ color: 'var(--text-muted)', fontWeight: 600, fontSize: '0.85rem' }}>
                        {data.stats.benchmark_return >= 0 ? '+' : ''}{data.stats.benchmark_return}% Return
                    </span>
                </div>
                <div className="metric-card glass-panel backtest-stat-card" style={{ borderLeft: `4px solid ${data.stats.outperformance >= 0 ? 'var(--profit-green)' : '#ef4444'}` }}>
                    <span className="label">Alpha (Outperformance)</span>
                    <span className="value" style={{ color: data.stats.outperformance >= 0 ? 'var(--profit-green)' : '#ef4444' }}>
                        {data.stats.outperformance >= 0 ? '+' : ''}{data.stats.outperformance}%
                    </span>
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>vs S&P 500 Benchmark</span>
                </div>
                <div className="metric-card glass-panel backtest-stat-card" style={{ borderLeft: '4px solid var(--accent-blue)' }}>
                    <span className="label">Total Capital Invested</span>
                    <span className="value">${data.stats.total_invested?.toLocaleString()}</span>
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Principal Amount</span>
                </div>
            </div>

            {/* Performance Chart */}
            <div className="glass-panel" style={{ padding: '1.5rem', marginTop: '1.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
                    <h3 style={{ margin: 0, fontSize: '1.1rem' }}>Equity Curve: Portfolio vs Benchmark</h3>
                    <div style={{ display: 'flex', gap: '1rem', fontSize: '0.85rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                            <div style={{ width: '12px', height: '3px', background: 'var(--accent-blue)' }}></div>
                            <span>Portfolio</span>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                            <div style={{ width: '12px', height: '3px', background: 'rgba(255,255,255,0.3)' }}></div>
                            <span>S&P 500</span>
                        </div>
                    </div>
                </div>

                <div style={{ height: '400px', width: '100%' }}>
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={data.history}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                            <XAxis
                                dataKey="date"
                                stroke="var(--text-muted)"
                                fontSize={10}
                                tickFormatter={(str) => {
                                    const date = new Date(str);
                                    return date.toLocaleDateString(undefined, { month: 'short', year: '2-digit' });
                                }}
                            />
                            <YAxis
                                stroke="var(--text-muted)"
                                fontSize={10}
                                tickFormatter={(val) => `$${(val / 1000).toFixed(0)}k`}
                            />
                            <Tooltip
                                contentStyle={{ background: 'rgba(0,0,0,0.85)', border: '1px solid var(--border-glass)', borderRadius: '8px', color: 'white' }}
                                formatter={(val) => [`$${val.toLocaleString()}`, ""]}
                                labelStyle={{ color: 'var(--text-muted)', marginBottom: '5px' }}
                            />
                            <Line
                                type="monotone"
                                dataKey="portfolio"
                                stroke="var(--accent-blue)"
                                strokeWidth={3}
                                dot={false}
                                activeDot={{ r: 6, stroke: 'white', strokeWidth: 2 }}
                            />
                            <Line
                                type="monotone"
                                dataKey="benchmark"
                                stroke="rgba(255,255,255,0.3)"
                                strokeWidth={2}
                                strokeDasharray="5 5"
                                dot={false}
                            />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Methodology Note */}
            <div className="glass-panel" style={{ padding: '1.5rem', marginTop: '1.5rem', borderLeft: '4px solid var(--accent-blue)' }}>
                <h3 style={{ margin: '0 0 0.5rem 0', fontSize: '1rem', color: 'white' }}>How this simulation works</h3>
                <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: '1.6' }}>
                    We take your current portfolio holdings and simulate a reverse time-travel.
                    We assume the <strong>Lump Sum</strong> amount was invested {period} years ago, and the <strong>Monthly SIP</strong> amount was added every month since then.
                    Benchmark performance is calculated by investing the same total capital (Lump Sum + SIPs) into the S&P 500 (^GSPC) on the same schedule.
                    Dividends are not included in this basic capital appreciation model.
                </p>
            </div>
        </>
    )
}
