from fpdf import FPDF
from datetime import datetime
import os

class ReportGenerator:
    """
    Institutional quality PDF report generator for Alpha Fund.
    """
    def __init__(self, data_manager):
        self.data_manager = data_manager

class ReportGenerator:
    """
    Institutional quality PDF report generator for Alpha Fund.
    """
    def __init__(self, data_manager):
        self.dm = data_manager

    def generate_full_report(self, output_path: str, ai_briefing: dict = None, risk_stats: dict = None):
        """
        Generates a comprehensive PDF report including Portfolio, Macro, AI Synthesis, and Risk.
        """
        # 1. Gather Data
        dashboard = self.dm.get_dashboard_summary()
        portfolio = self.dm.get_portfolio_data()
        macro = self.dm.get_macro_overview()
        
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        # --- Institutional Header ---
        pdf.set_font("Helvetica", "B", 24)
        pdf.set_text_color(20, 50, 100) # Deep Blue
        pdf.cell(0, 20, "ALPHA FUND | PRIVATE INTEL", ln=True, align="C")
        
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 10, f"Confidential Investment Intelligence Report | {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align="C")
        pdf.ln(10)
        
        # --- Executive Summary ---
        self._section_header(pdf, "EXECUTIVE SUMMARY")
        
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(0, 0, 0)
        
        # Grid layout for summary
        y_start = pdf.get_y()
        pdf.cell(90, 8, f"Total Asset Value: ${dashboard.get('total_value', 0):,.2f}", border=0)
        pdf.cell(90, 8, f"Holdings Count: {dashboard.get('holdings_count', 0)} assets", border=0, ln=True)
        
        pnl = dashboard.get('daily_pnl', 0)
        pnl_pct = dashboard.get('daily_pnl_pct', 0)
        color = (0, 120, 0) if pnl >= 0 else (200, 0, 0)
        
        pdf.cell(90, 8, "Daily Performance: ", border=0)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(*color)
        pdf.cell(90, 8, f"{pnl_pct:+.2f}% (${pnl:,.2f})", border=0, ln=True)
        
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)

        # --- AI Synthesis (New Section) ---
        if ai_briefing and ai_briefing.get('narrative'):
            self._section_header(pdf, "AI SYNTHESIS & MARKET NARRATIVE")
            pdf.set_font("Helvetica", "I", 10)
            pdf.multi_cell(0, 6, ai_briefing['narrative'])
            pdf.ln(5)

        # --- Global Macro Context (New Section) ---
        if macro and (macro.get('indices') or macro.get('gauges')):
            self._section_header(pdf, "GLOBAL MACRO CONTEXT")
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_fill_color(230, 230, 230)
            pdf.cell(60, 8, "Index / Indicator", border=1, fill=True)
            pdf.cell(40, 8, "Current Price", border=1, fill=True)
            pdf.cell(40, 8, "Day Change (%)", border=1, fill=True)
            pdf.cell(50, 8, "Market Status", border=1, fill=True, ln=True)
            
            pdf.set_font("Helvetica", "", 9)
            # Combine indices and gauges for a top overview
            combined_macro = (macro.get('indices', []) + macro.get('gauges', []))
            for item in combined_macro[:10]: # Top 10 macro items
                pdf.cell(60, 8, item['name'], border=1)
                pdf.cell(40, 8, f"{item['price']:,.2f}", border=1)
                
                chg = item.get('change_pct', 0)
                color = (0, 120, 0) if chg >= 0 else (200, 0, 0)
                pdf.set_text_color(*color)
                pdf.cell(40, 8, f"{chg:+.2f}%", border=1)
                pdf.set_text_color(0, 0, 0)
                
                status = "Stable" if abs(chg) < 1.0 else ("Volatile" if abs(chg) < 2.5 else "Extreme")
                pdf.cell(50, 8, status, border=1, ln=True)
            pdf.ln(10)

        # --- Asset Allocation ---
        self._section_header(pdf, "PORTFOLIO ALLOCATION BY CATEGORY")
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(60, 8, "Category", border=1, fill=True)
        pdf.cell(60, 8, "Invested Amount", border=1, fill=True)
        pdf.cell(60, 8, "Weight (%)", border=1, fill=True, ln=True)
        
        pdf.set_font("Helvetica", "", 10)
        for alloc in dashboard.get('allocation', []):
            pdf.cell(60, 8, alloc['category'], border=1)
            pdf.cell(60, 8, f"${alloc['value']:,.2f}", border=1)
            pdf.cell(60, 8, f"{alloc['percent']}%", border=1, ln=True)
        pdf.ln(10)

        # --- Risk Metrics (New Section) ---
        if risk_stats:
            self._section_header(pdf, "STRESS TEST & RISK METRICS")
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(90, 8, f"Portfolio Beta: {risk_stats.get('beta', 'N/A')}", border=0)
            pdf.cell(90, 8, f"Max Drawdown (Hist): {risk_stats.get('max_drawdown', 'N/A')}%", border=0, ln=True)
            pdf.cell(90, 8, f"Sharpe Ratio: {risk_stats.get('sharpe_ratio', 'N/A')}", border=0)
            pdf.cell(90, 8, f"Crisis Sensitivity: {risk_stats.get('crisis_drawdown', 'N/A')}% (2008 Proxy)", border=0, ln=True)
            pdf.ln(5)

        # Add new page for Holdings Details if needed
        pdf.add_page()
        self._section_header(pdf, "INDIVIDUAL HOLDINGS PERFORMANCE")
        
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(20, 8, "Ticker", border=1, fill=True)
        pdf.cell(70, 8, "Asset Name", border=1, fill=True)
        pdf.cell(30, 8, "Price", border=1, fill=True)
        pdf.cell(30, 8, "Day Chg", border=1, fill=True)
        pdf.cell(40, 8, "Invested", border=1, fill=True, ln=True)
        
        pdf.set_font("Helvetica", "", 9)
        for h in portfolio:
            ticker = h.get('ticker', '')
            name = h.get('name', '')[:35]
            price = f"{h.get('price', 0):.2f}"
            chg = float(h.get('day_change', 0))
            inv = f"${h.get('value', 0):,.2f}"
            
            pdf.cell(20, 8, ticker, border=1)
            pdf.cell(70, 8, name, border=1)
            pdf.cell(30, 8, price, border=1)
            
            color = (0, 120, 0) if chg >= 0 else (200, 0, 0)
            pdf.set_text_color(*color)
            pdf.cell(30, 8, f"{chg:+.2f}%", border=1)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(40, 8, inv, border=1, ln=True)
            
        # --- Footer ---
        pdf.set_y(-25)
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(0, 10, "CONFIDENTIAL - For institutional use only. Data derived from AI Forecaster & Risk Engines. Not financial advice.", align="C")
        
        pdf.output(output_path)
        return output_path

    def _section_header(self, pdf, title):
        pdf.set_fill_color(240, 245, 255)
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(20, 50, 100)
        pdf.cell(0, 10, f"  {title}", ln=True, fill=True)
        pdf.ln(5)
        pdf.set_text_color(0, 0, 0)
