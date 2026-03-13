import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import React from 'react';
import { DashboardOverview } from '../pages/Views';
import { BrowserRouter } from 'react-router-dom';

// Mock global fetch
global.fetch = vi.fn();

describe('DashboardOverview Component', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  it('renders loading state initially', () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({})
    });
    
    render(
      <BrowserRouter>
        <DashboardOverview />
      </BrowserRouter>
    );
    
    // Check for "Executive Dashboard" which should be present in header
    expect(screen.getByText(/Executive Dashboard/i)).toBeTruthy();
  });

  it('displays data from API', async () => {
    const mockData = {
      health_score: 85,
      pnl_daily: 1250.50,
      total_value: 50000,
      top_gainers: [{ ticker: 'AAPL', change: 2.5 }],
      top_losers: [{ ticker: 'TSLA', change: -1.2 }],
      allocation: [{ name: 'Stocks', value: 70 }, { name: 'Bonds', value: 30 }],
      market_pulse: []
    };

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockData
    });

    render(
      <BrowserRouter>
        <DashboardOverview />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/85/i)).toBeTruthy();
      expect(screen.getByText(/\$50,000/i)).toBeTruthy();
    });
  });
});
