import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { Sparkline } from '../pages/Views';

describe('Sparkline Component', () => {
  it('renders without crashing', () => {
    const mockData = [
        { date: '2023-01-01', close: 100 },
        { date: '2023-01-02', close: 110 }
    ];
    render(<Sparkline data={mockData} />);
    // Check if the SVG is present
    const svgElement = document.querySelector('svg');
    expect(svgElement).toBeTruthy();
  });

  it('handles empty data gracefully', () => {
    render(<Sparkline data={[]} />);
    const sparklineDiv = document.querySelector('.sparkline-container');
    // If it's a null return or empty div
    expect(sparklineDiv).toBeFalsy();
  });
});
