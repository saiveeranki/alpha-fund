from data.database import SessionLocal, Asset, FinancialStatementCache, TickerRegistry, PortfolioHolding, GenericCache
from data.providers.yfinance_provider import YFinanceProvider
from data.models import FinancialMetrics
import pandas as pd
import json
from datetime import date, datetime, timedelta

class DataManager:
    """
    Central hub for requesting financial data. Dispatches to the correct 
    API Provider and caches the results in the SQL Database.
    """
    def __init__(self):
        # We start with just YFinance, but can add FMP, AlphaVantage here later
        self.yfinance = YFinanceProvider()

    def _get_cached_data(self, key: str) -> any:
        """Helper to get data from local DB cache if not expired."""
        db: Session = SessionLocal()
        try:
            cache_item = db.query(GenericCache).filter(GenericCache.key == key).first()
            if cache_item and cache_item.expiry > datetime.utcnow():
                return json.loads(cache_item.data)
        except Exception as e:
            print(f"[DataManager] Cache read error for {key}: {e}")
        finally:
            db.close()
        return None

    def _set_cached_data(self, key: str, data: any, expiry_hours: int = 24):
        """Helper to save data to local DB cache with expiry."""
        db: Session = SessionLocal()
        try:
            # Delete old entry if exists
            db.query(GenericCache).filter(GenericCache.key == key).delete()
            
            new_cache = GenericCache(
                key=key,
                data=json.dumps(data),
                expiry=datetime.utcnow() + timedelta(hours=expiry_hours),
                updated_at=datetime.utcnow()
            )
            db.add(new_cache)
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"[DataManager] Cache write error for {key}: {e}")
        finally:
            db.close()
        
    def _fetch_from_api(self, ticker: str, market: str) -> FinancialMetrics | None:
        """Logic to decide which API handles which market. Right now, all default to yfinance."""
        if market in ["US", "GLOBAL"]:
             return self.yfinance.fetch_metrics(ticker)
        return self.yfinance.fetch_metrics(ticker)

    def get_historical_prices(self, ticker: str, period: str = "5y") -> list[dict] | None:
        """
        Passes historical request to the YFinance provider.
        Caches it in SQLite to prevent repeated heavy calls.
        """
        cache_key = f"hist_{ticker}_{period}"
        cached = self._get_cached_data(cache_key)
        if cached:
            print(f"[DataManager] Loaded {ticker} historical from DB Cache.")
            return cached
            
        data = self.yfinance.fetch_history(ticker, period)
        if data:
            self._set_cached_data(cache_key, data, expiry_hours=24) # Cache for 1 day
        return data
        
    def get_magic_formula_data(self, ticker: str, name: str, sector: str, market: str = "GLOBAL") -> dict:
        """
        Attempts to load data from the DB cache for today. If it doesn't exist, 
        fetches it from the selected API, caches it, and returns it.
        """
        db: Session = SessionLocal()
        
        try:
            # 1. Ensure Asset exists in DB
            db_asset = db.query(Asset).filter(Asset.ticker == ticker).first()
            if not db_asset:
                db_asset = Asset(ticker=ticker, name=name, sector=sector)
                db.add(db_asset)
                db.commit()
                
            # 2. Check cache for today's financial statement
            today = date.today()
            cached_stmt = db.query(FinancialStatementCache).filter(
                FinancialStatementCache.ticker == ticker,
                FinancialStatementCache.date_recorded == today
            ).first()
            
            if cached_stmt:
                print(f"[DataManager] Loaded {ticker} from Local DB Cache.")
                
                # Rehydrate into Pydantic model for calculations
                metrics = FinancialMetrics(
                    ticker=cached_stmt.ticker,
                    date_recorded=cached_stmt.date_recorded,
                    source_api=cached_stmt.source_api,
                    ebit=cached_stmt.ebit,
                    enterprise_value=cached_stmt.enterprise_value,
                    current_assets=cached_stmt.current_assets,
                    current_liabilities=cached_stmt.current_liabilities,
                    total_assets=cached_stmt.total_assets,
                    net_fixed_assets=cached_stmt.net_fixed_assets
                )
            else:
                # 3. Hit the API 
                metrics = self._fetch_from_api(ticker, market)
                if not metrics:
                    return {"Ticker": ticker, "Status": "API Fetch Failed"}
                    
                # 4. Save to Cache
                new_stmt = FinancialStatementCache(
                    ticker=metrics.ticker,
                    date_recorded=metrics.date_recorded,
                    source_api=metrics.source_api,
                    ebit=metrics.ebit,
                    enterprise_value=metrics.enterprise_value,
                    current_assets=metrics.current_assets,
                    current_liabilities=metrics.current_liabilities,
                    total_assets=metrics.total_assets,
                    net_fixed_assets=metrics.net_fixed_assets
                )
                db.add(new_stmt)
                db.commit()
                print(f"[DataManager] Saved {ticker} to Local DB Cache.")
                
            # 5. Return standardized dictionary suitable for pandas
            ey = metrics.earnings_yield
            roc = metrics.roc
            
            return {
                "Ticker": metrics.ticker,
                "Name": name,
                "Sector": sector,
                "Earnings_Yield": ey,
                "ROC": roc,
                "EBIT": metrics.ebit,
                "Enterprise_Value": metrics.enterprise_value,
                "Current_Assets": metrics.current_assets,
                "Current_Liabilities": metrics.current_liabilities,
                "Net_Working_Capital": metrics.net_working_capital,
                "Net_Fixed_Assets": metrics.net_fixed_assets,
                "Status": "Success"
            }
                
        except Exception as e:
            db.rollback()
            return {"Ticker": ticker, "Status": f"DB Error: {str(e)}"}
        finally:
            db.close()

    def get_sector_annual_returns(self, start_year: int = 2010, market: str = "US") -> list[dict]:
        """
        Fetches annual returns for pre-defined sector ETFs.
        Supports US, EU, and India markets.
        """
        US_SECTORS = [
            {"name": "Technology", "tickers": ["XLK", "VGT", "IYW", "FTEC", "IXN"], "color": "#3b82f6"},
            {"name": "Financials", "tickers": ["XLF", "VFH", "IYF", "FNCL", "IXG"], "color": "#10b981"},
            {"name": "Healthcare", "tickers": ["XLV", "VHT", "IYH", "FHLC", "IXJ"], "color": "#ef4444"},
            {"name": "Cons. Discr.", "tickers": ["XLY", "VCR", "IYC", "FDIS", "RXI"], "color": "#f59e0b"},
            {"name": "Cons. Staples", "tickers": ["XLP", "VDC", "IYK", "FSTA", "KXI"], "color": "#8b5cf6"},
            {"name": "Energy", "tickers": ["XLE", "VDE", "IYE", "FENY", "IXC"], "color": "#14b8a6"},
            {"name": "Materials", "tickers": ["XLB", "VAW", "IYM", "FMAT", "MXI"], "color": "#f97316"},
            {"name": "Industrials", "tickers": ["XLI", "VIS", "IYJ", "FIDU", "EXI"], "color": "#64748b"},
            {"name": "Utilities", "tickers": ["XLU", "VPU", "IDU", "FUTY", "JXI"], "color": "#06b6d4"},
            {"name": "Real Estate", "tickers": ["VNQ", "XLRE", "USRT", "FREL", "SCHH"], "color": "#ec4899"},
            {"name": "Communication", "tickers": ["XLC", "VOX", "IXP", "FCOM", "IYZ"], "color": "#84cc16"},
        ]
        
        # iShares STOXX Europe 600 sub-sector ETFs (Xetra)
        EU_SECTORS = [
            {"name": "Technology", "tickers": ["EXV8.DE"], "color": "#3b82f6"},
            {"name": "Banks", "tickers": ["EXV1.DE"], "color": "#10b981"},
            {"name": "Healthcare", "tickers": ["EXV4.DE"], "color": "#ef4444"},
            {"name": "Autos & Parts", "tickers": ["EXV5.DE"], "color": "#f59e0b"},
            {"name": "Food & Bev.", "tickers": ["EXV7.DE"], "color": "#8b5cf6"},
            {"name": "Oil & Gas", "tickers": ["EXV6.DE"], "color": "#14b8a6"},
            {"name": "Basic Res.", "tickers": ["EXV3.DE"], "color": "#f97316"},
            {"name": "Industrials", "tickers": ["EXV2.DE"], "color": "#64748b"},
            {"name": "Utilities", "tickers": ["EXV9.DE"], "color": "#06b6d4"},
            {"name": "Real Estate", "tickers": ["IQQP.DE"], "color": "#ec4899"},
            {"name": "Telecom", "tickers": ["EXH8.DE"], "color": "#84cc16"},
        ]
        
        # Indian Nifty / BSE Sector Indices (matching FundsIndia reference chart)
        # Tickers verified against Yahoo Finance availability
        # Note: Most indices start mid-2011, so 2010 data is sparse
        INDIA_SECTORS = [
            {"name": "Healthcare", "tickers": ["^CNXPHARMA"], "color": "#ef4444"},
            {"name": "Auto", "tickers": ["^CNXAUTO"], "color": "#f59e0b"},
            {"name": "FMCG", "tickers": ["^CNXFMCG"], "color": "#f97316"},
            {"name": "Financials", "tickers": ["NIFTY_FIN_SERVICE.NS"], "color": "#10b981"},
            {"name": "IT", "tickers": ["^CNXIT"], "color": "#3b82f6"},
            {"name": "Cons Disc.", "tickers": ["^CNXCONSUM"], "color": "#a855f7"},
            {"name": "Media", "tickers": ["^CNXMEDIA"], "color": "#64748b"},
            {"name": "Telecom", "tickers": ["BHARTIARTL.NS"], "color": "#84cc16"},
            {"name": "Oil & Gas", "tickers": ["^CNXENERGY"], "color": "#14b8a6"},
            {"name": "Realty", "tickers": ["^CNXREALTY"], "color": "#ec4899"},
            {"name": "Metals", "tickers": ["^CNXMETAL"], "color": "#a8a29e"},
            {"name": "Utilities", "tickers": ["^CNXPSE"], "color": "#06b6d4"},
            {"name": "Infrastructure", "tickers": ["^CNXINFRA"], "color": "#8b5cf6"},
        ]
        
        market_map = {"US": US_SECTORS, "EU": EU_SECTORS, "India": INDIA_SECTORS}
        SECTORS = market_map.get(market, US_SECTORS)
        
        cache_key = f"sector_returns_{market}_{start_year}"
        cached = self._get_cached_data(cache_key)
        if cached:
            print(f"[DataManager] Loaded Sector Returns ({market}) from DB Cache.")
            return cached

        results = []
        for sector in SECTORS:
            # Fetch returns for all ETFs in this sector and average them per year
            all_returns = []
            for ticker in sector["tickers"]:
                returns = self.yfinance.fetch_annual_returns(ticker, start_year)
                if returns:
                    all_returns.append(returns)
            
            if all_returns:
                # Merge all year keys and compute the average return per year
                all_years = set()
                for r in all_returns:
                    all_years.update(r.keys())
                
                avg_returns = {}
                for year in all_years:
                    year_vals = [r[year] for r in all_returns if year in r]
                    if year_vals:
                        avg_returns[year] = round(sum(year_vals) / len(year_vals), 2)
                
                results.append({
                    "sector": sector["name"],
                    "color": sector["color"],
                    "returns": avg_returns
                })
        
        if results:
            self._set_cached_data(cache_key, results, expiry_hours=24)
        return results

    def get_sector_indices_metrics(self, market: str = "US") -> list[dict]:
        """
        Fetches detailed financial metrics (Magic Formula + CAGR) for sector ETFs/indices.
        Supports US, EU, and India markets.
        """
        cache_key = f"sector_metrics_{market}"
        cached = self._get_cached_data(cache_key)
        if cached:
            print(f"[DataManager] Loaded Sector Metrics ({market}) from DB Cache.")
            return cached

        US_SECTORS = [
            {"name": "Technology", "tickers": ["XLK", "VGT", "IYW", "FTEC", "IXN"], "color": "#3b82f6"},
            {"name": "Financials", "tickers": ["XLF", "VFH", "IYF", "FNCL", "IXG"], "color": "#10b981"},
            {"name": "Healthcare", "tickers": ["XLV", "VHT", "IYH", "FHLC", "IXJ"], "color": "#ef4444"},
            {"name": "Cons. Discr.", "tickers": ["XLY", "VCR", "IYC", "FDIS", "RXI"], "color": "#f59e0b"},
            {"name": "Cons. Staples", "tickers": ["XLP", "VDC", "IYK", "FSTA", "KXI"], "color": "#8b5cf6"},
            {"name": "Energy", "tickers": ["XLE", "VDE", "IYE", "FENY", "IXC"], "color": "#14b8a6"},
            {"name": "Materials", "tickers": ["XLB", "VAW", "IYM", "FMAT", "MXI"], "color": "#f97316"},
            {"name": "Industrials", "tickers": ["XLI", "VIS", "IYJ", "FIDU", "EXI"], "color": "#64748b"},
            {"name": "Utilities", "tickers": ["XLU", "VPU", "IDU", "FUTY", "JXI"], "color": "#06b6d4"},
            {"name": "Real Estate", "tickers": ["VNQ", "XLRE", "USRT", "FREL", "SCHH"], "color": "#ec4899"},
            {"name": "Communication", "tickers": ["XLC", "VOX", "IXP", "FCOM", "IYZ"], "color": "#84cc16"},
        ]
        
        # European sector ETFs (iShares STOXX 600) + Xtrackers + major blue-chips
        EU_SECTORS = [
            {"name": "Technology", "tickers": ["EXV8.DE", "XDWT.DE", "STK.PA", "TNOW.L", "IUIT.L"], "color": "#3b82f6"},
            {"name": "Banks", "tickers": ["EXV1.DE", "EXXW.DE", "EXI5.DE", "BNKE.L", "BNP.PA"], "color": "#10b981"},
            {"name": "Healthcare", "tickers": ["EXV4.DE", "EXHE.DE", "IUHC.L", "STW.PA", "HEAL.L"], "color": "#ef4444"},
            {"name": "Autos & Parts", "tickers": ["EXV5.DE", "EXHB.DE", "BMW.DE", "VOW3.DE", "MBG.DE"], "color": "#f59e0b"},
            {"name": "Food & Bev.", "tickers": ["EXV7.DE", "EXHC.DE", "IUFS.L", "FOO.PA", "ULVR.L"], "color": "#8b5cf6"},
            {"name": "Oil & Gas", "tickers": ["EXV6.DE", "EXHF.DE", "SHEL.L", "TTE.PA", "ENRG.L"], "color": "#14b8a6"},
            {"name": "Basic Res.", "tickers": ["EXV3.DE", "EXHD.DE", "RIO.L", "GLEN.L", "BHP.L"], "color": "#f97316"},
            {"name": "Industrials", "tickers": ["EXV2.DE", "SIE.DE", "ABB.ST", "PRIJ.L", "C500.L"], "color": "#64748b"},
            {"name": "Utilities", "tickers": ["EXV9.DE", "ENEL.MI", "IBE.MC", "ENGI.PA", "NG.L"], "color": "#06b6d4"},
            {"name": "Real Estate", "tickers": ["IQQP.DE", "VNA.DE", "LEG.DE", "SBRY.L", "INGA.AS"], "color": "#ec4899"},
            {"name": "Telecom", "tickers": ["EXH8.DE", "DTE.DE", "TEF.MC", "KPN.AS", "SPYE.L"], "color": "#84cc16"},
        ]
        
        # Indian Nifty sector indices + top blue-chip stocks per sector
        INDIA_SECTORS = [
            {"name": "Healthcare", "tickers": ["^CNXPHARMA", "SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "DIVISLAB.NS"], "color": "#ef4444"},
            {"name": "Auto", "tickers": ["^CNXAUTO", "MARUTI.NS", "M&M.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS"], "color": "#f59e0b"},
            {"name": "FMCG", "tickers": ["^CNXFMCG", "HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS", "DABUR.NS"], "color": "#f97316"},
            {"name": "Financials", "tickers": ["NIFTY_FIN_SERVICE.NS", "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS"], "color": "#10b981"},
            {"name": "IT", "tickers": ["^CNXIT", "TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS"], "color": "#3b82f6"},
            {"name": "Cons Disc.", "tickers": ["^CNXCONSUM", "TITAN.NS", "TRENT.NS", "PAGEIND.NS", "JUBLFOOD.NS"], "color": "#a855f7"},
            {"name": "Media", "tickers": ["^CNXMEDIA", "ZEEL.NS", "PVRINOX.NS", "SUNTV.NS", "NETWORK18.NS"], "color": "#64748b"},
            {"name": "Telecom", "tickers": ["BHARTIARTL.NS", "IDEA.NS", "TATACOMM.NS", "INDUSTOWER.NS", "ROUTE.NS"], "color": "#84cc16"},
            {"name": "Oil & Gas", "tickers": ["^CNXENERGY", "RELIANCE.NS", "ONGC.NS", "BPCL.NS", "IOC.NS"], "color": "#14b8a6"},
            {"name": "Realty", "tickers": ["^CNXREALTY", "DLF.NS", "GODREJPROP.NS", "OBEROIRLTY.NS", "PRESTIGE.NS"], "color": "#ec4899"},
            {"name": "Metals", "tickers": ["^CNXMETAL", "TATASTEEL.NS", "HINDALCO.NS", "JSWSTEEL.NS", "VEDL.NS"], "color": "#a8a29e"},
            {"name": "Utilities", "tickers": ["^CNXPSE", "NTPC.NS", "POWERGRID.NS", "TATAPOWER.NS", "NHPC.NS"], "color": "#06b6d4"},
            {"name": "Infrastructure", "tickers": ["^CNXINFRA", "LT.NS", "ADANIPORTS.NS", "IRB.NS", "LTIM.NS"], "color": "#8b5cf6"},
        ]
        
        market_map = {"US": US_SECTORS, "EU": EU_SECTORS, "India": INDIA_SECTORS}
        SECTORS = market_map.get(market, US_SECTORS)
        
        results = []
        for sector in SECTORS:
            for ticker in sector["tickers"]:
                # Try to get Magic Formula fundamentals
                data = self.get_magic_formula_data(
                    ticker=ticker,
                    name=f"{sector['name']} ({ticker})",
                    sector=sector["name"],
                    market=market if market != "India" else "GLOBAL"
                )
                
                # Calculate 5-Year CAGR regardless of fundamentals
                hist = self.get_historical_prices(ticker, "5y")
                cagr_val = None
                
                if hist and len(hist) > 1:
                    start_price = hist[0]["close"]
                    end_price = hist[-1]["close"]
                    years = len(hist) / 252.0
                    if years > 0 and start_price > 0:
                        cagr_val = ((end_price / start_price) ** (1 / years)) - 1
                
                def safe_round(val, decimals=2):
                    return round(float(val), decimals) if pd.notna(val) and val is not None else None
                
                result_entry = {
                    "ticker": ticker,
                    "sector": sector["name"],
                    "color": sector["color"],
                    "cagr": safe_round(cagr_val, 4),
                }
                
                if data.get("Status") == "Success":
                    result_entry.update({
                        "ey": safe_round(data.get("Earnings_Yield"), 4),
                        "roc": safe_round(data.get("ROC"), 4),
                        "ebit": safe_round(data.get("EBIT")),
                        "ev": safe_round(data.get("Enterprise_Value")),
                        "ca": safe_round(data.get("Current_Assets")),
                        "cl": safe_round(data.get("Current_Liabilities")),
                        "nwc": safe_round(data.get("Net_Working_Capital")),
                        "nfa": safe_round(data.get("Net_Fixed_Assets")),
                    })
                else:
                    # Indices (e.g. India) won't have fundamentals — fill with None
                    result_entry.update({
                        "ey": None, "roc": None, "ebit": None, "ev": None,
                        "ca": None, "cl": None, "nwc": None, "nfa": None,
                    })
                
                results.append(result_entry)
                    
        if results:
            self._set_cached_data(cache_key, results, expiry_hours=12)
        return results

    def get_debt_funds_data(self, market: str = "US") -> list[dict]:
        """
        Fetches metrics for top debt funds/ETFs: yield, NAV, 1Y/3Y/5Y returns, AUM.
        Supports US, EU, and India markets.
        """
        cache_key = f"debt_funds_{market}"
        cached = self._get_cached_data(cache_key)
        if cached:
            print(f"[DataManager] Loaded Debt Funds ({market}) from DB Cache.")
            return cached

        US_FUNDS = [
            {"category": "Aggregate Bond", "funds": [
                {"ticker": "BND", "name": "Vanguard Total Bond Market ETF"},
                {"ticker": "AGG", "name": "iShares Core US Aggregate Bond ETF"},
                {"ticker": "SCHZ", "name": "Schwab US Aggregate Bond ETF"},
                {"ticker": "BNDX", "name": "Vanguard Total Intl Bond ETF"},
                {"ticker": "GOVT", "name": "iShares US Treasury Bond ETF"},
            ]},
            {"category": "Treasury Long", "funds": [
                {"ticker": "TLT", "name": "iShares 20+ Year Treasury Bond ETF"},
                {"ticker": "SPTL", "name": "SPDR Portfolio Long Term Treasury ETF"},
                {"ticker": "BLV", "name": "Vanguard Long-Term Bond ETF"},
                {"ticker": "IEF", "name": "iShares 7-10 Year Treasury Bond ETF"},
                {"ticker": "SHY", "name": "iShares 1-3 Year Treasury Bond ETF"},
            ]},
            {"category": "Corporate Bond", "funds": [
                {"ticker": "LQD", "name": "iShares Investment Grade Corp Bond ETF"},
                {"ticker": "VCSH", "name": "Vanguard Short-Term Corporate Bond ETF"},
                {"ticker": "VCIT", "name": "Vanguard Intermediate-Term Corp Bond ETF"},
                {"ticker": "IGSB", "name": "iShares 1-5 Year Invest Grade Corp ETF"},
                {"ticker": "BSV", "name": "Vanguard Short-Term Bond ETF"},
            ]},
            {"category": "High Yield", "funds": [
                {"ticker": "HYG", "name": "iShares High Yield Corporate Bond ETF"},
                {"ticker": "BIV", "name": "Vanguard Intermediate-Term Bond ETF"},
                {"ticker": "VTIP", "name": "Vanguard Short-Term Inflation-Protected ETF"},
                {"ticker": "TIP", "name": "iShares TIPS Bond ETF"},
                {"ticker": "MUB", "name": "iShares National Muni Bond ETF"},
            ]},
        ]

        EU_FUNDS = [
            {"category": "Euro Aggregate", "funds": [
                {"ticker": "IEAC.L", "name": "iShares Core Euro Corp Bond ETF"},
                {"ticker": "AGGH.L", "name": "iShares Core Global Aggregate Bond ETF"},
                {"ticker": "SEGA.L", "name": "iShares Core Euro Govt Bond ETF"},
                {"ticker": "EUNA.DE", "name": "iShares Core Global Aggregate Bond EUR"},
                {"ticker": "IBCI.DE", "name": "iShares Euro Inflation Linked Govt Bond"},
            ]},
            {"category": "Euro Government", "funds": [
                {"ticker": "IBGS.DE", "name": "iShares Euro Govt Bond 1-3yr ETF"},
                {"ticker": "IBGL.DE", "name": "iShares Euro Govt Bond 15-30yr ETF"},
                {"ticker": "IS04.DE", "name": "iShares USD Treasury Bond 20+yr ETF"},
                {"ticker": "IBTS.L", "name": "iShares USD Treasury Bond 1-3yr ETF"},
                {"ticker": "IBTM.L", "name": "iShares USD Treasury Bond 7-10yr ETF"},
            ]},
            {"category": "Euro Corporate", "funds": [
                {"ticker": "IHYG.L", "name": "iShares Euro High Yield Corp Bond ETF"},
                {"ticker": "IBTL.L", "name": "iShares USD Treasury Bond 20+yr ETF"},
                {"ticker": "VGEA.L", "name": "Vanguard EUR Eurozone Govt Bond ETF"},
                {"ticker": "XBLD.L", "name": "Xtrackers EUR Corporate Bond ETF"},
                {"ticker": "EXHE.DE", "name": "iShares STOXX Europe 600 Healthcare ETF"},
            ]},
        ]

        INDIA_FUNDS = [
            {"category": "Liquid / Money Market", "funds": [
                {"ticker": "LIQUIDBEES.NS", "name": "Nippon India ETF Liquid BeES"},
                {"ticker": "LIQUID.NS", "name": "DSP Liquidity Fund"},
                {"ticker": "HDFCLIQUID.NS", "name": "HDFC Liquid Fund"},
                {"ticker": "CPSEETF.NS", "name": "Nippon India ETF CPSE"},
                {"ticker": "SETFNIF50.NS", "name": "SBI ETF Nifty 50"},
            ]},
            {"category": "Government Securities", "funds": [
                {"ticker": "NTPC.NS", "name": "NTPC Ltd (Govt PSU)"},
                {"ticker": "POWERGRID.NS", "name": "Power Grid Corp (Govt PSU)"},
                {"ticker": "NHPC.NS", "name": "NHPC Ltd (Govt PSU)"},
                {"ticker": "IRFC.NS", "name": "Indian Railway Finance Corp"},
                {"ticker": "PFC.NS", "name": "Power Finance Corporation"},
            ]},
            {"category": "PSU & Infrastructure Bonds", "funds": [
                {"ticker": "RECLTD.NS", "name": "REC Ltd"},
                {"ticker": "IRCTC.NS", "name": "IRCTC Ltd"},
                {"ticker": "COALINDIA.NS", "name": "Coal India Ltd"},
                {"ticker": "GAIL.NS", "name": "GAIL India Ltd"},
                {"ticker": "BHEL.NS", "name": "Bharat Heavy Electricals"},
            ]},
        ]

        market_map = {"US": US_FUNDS, "EU": EU_FUNDS, "India": INDIA_FUNDS}
        categories = market_map.get(market, US_FUNDS)

        results = []
        for cat in categories:
            for fund in cat["funds"]:
                ticker = fund["ticker"]
                try:
                    import yfinance as yf_mod
                    yf_ticker = yf_mod.Ticker(ticker)
                    info = yf_ticker.info or {}
                    
                    # Get price history for return calculations
                    hist_5y = yf_ticker.history(period="5y")
                    hist_3y = yf_ticker.history(period="3y")
                    hist_1y = yf_ticker.history(period="1y")
                    
                    def calc_return(hist, years):
                        if hist is not None and len(hist) > 1:
                            start = hist['Close'].iloc[0]
                            end = hist['Close'].iloc[-1]
                            if start > 0:
                                return round(((end / start) ** (1 / years) - 1) * 100, 2)
                        return None
                    
                    nav = round(float(info.get('previousClose', 0)), 2) if info.get('previousClose') else None
                    aum = info.get('totalAssets')
                    yld = info.get('yield')
                    
                    results.append({
                        "ticker": ticker,
                        "name": fund["name"],
                        "category": cat["category"],
                        "nav": nav,
                        "yield": round(yld * 100, 2) if yld else None,
                        "aum": aum,
                        "return_1y": calc_return(hist_1y, 1),
                        "return_3y": calc_return(hist_3y, 3),
                        "return_5y": calc_return(hist_5y, 5),
                    })
                except Exception as e:
                    print(f"[DebtFunds] Error for {ticker}: {e}")
                    results.append({
                        "ticker": ticker,
                        "name": fund["name"],
                        "category": cat["category"],
                        "nav": None, "yield": None, "aum": None,
                        "return_1y": None, "return_3y": None, "return_5y": None,
                    })
        if results:
            self._set_cached_data(cache_key, results, expiry_hours=12)
        return results

    def get_india_mutual_funds_data(self) -> list[dict]:
        """
        Fetches comprehensive data for Indian Mutual Funds and related assets.
        Categories: Equity Leaders, Sectoral/Thematic, Fixed Income & Liquid, G-Secs, Gold & SGBs.
        """
        cache_key = "india_mutual_funds"
        cached = self._get_cached_data(cache_key)
        if cached:
            print("[DataManager] Loaded India Mutual Funds from DB Cache.")
            return cached

        import yfinance as yf_mod
        import numpy as np
        import pandas as pd

        INDIA_MF_UNIVERSE = [
            {"category": "Equity Leaders (Large/Mid/Flexi)", "funds": [
                {"ticker": "NIFTYBEES.NS", "name": "Nippon India ETF Nifty 50 BeES"},
                {"ticker": "JUNIORBEES.NS", "name": "Nippon India ETF Nifty Next 50"},
                {"ticker": "M100.NS", "name": "Motilal Oswal Midcap 100 ETF"},
                {"ticker": "SETFNIF50.NS", "name": "SBI ETF Nifty 50"},
                {"ticker": "HDFCNIFTY.NS", "name": "HDFC Nifty 50 ETF"},
            ]},
            {"category": "Sectoral & Thematic", "funds": [
                {"ticker": "BANKBEES.NS", "name": "Nippon India ETF Bank BeES"},
                {"ticker": "ITBEES.NS", "name": "Nippon India ETF IT BeES"},
                {"ticker": "PHARMABEES.NS", "name": "Nippon India ETF Pharma BeES"},
                {"ticker": "CPSEETF.NS", "name": "Nippon India ETF CPSE"},
                {"ticker": "ICICINV20.NS", "name": "ICICI Pru NV20 ETF"},
                {"ticker": "MON100.NS", "name": "Motilal Oswal Nasdaq 100 ETF"},
            ]},
            {"category": "Fixed Income & Liquid Funds", "funds": [
                {"ticker": "LIQUIDBEES.NS", "name": "Nippon India ETF Liquid BeES"},
                {"ticker": "ICICILIQ.NS", "name": "ICICI Pru Liquid ETF"},
                {"ticker": "HDFCLIQUID.NS", "name": "HDFC Liquid ETF"},
                {"ticker": "EBBETF0430.NS", "name": "BHARAT Bond ETF - April 2030"},
                {"ticker": "BBETF0432.NS", "name": "BHARAT Bond ETF - April 2032"},
            ]},
            {"category": "Government Securities (G-Secs)", "funds": [
                {"ticker": "GSEC10YEAR.NS", "name": "Mirae Asset Nifty 8-13 yr G-Sec ETF"},
                {"ticker": "LTGILTBEES.NS", "name": "Nippon India ETF Gilt BeES"},
                {"ticker": "LICNETFGSC.NS", "name": "LIC MF Nifty 8-13 yr G-Sec ETF"},
                {"ticker": "SDL26BEES.NS", "name": "Nippon India ETF SDL Apr 2026"},
            ]},
            {"category": "Gold & Sovereign Gold Bonds (SGBs)", "funds": [
                {"ticker": "GOLDBEES.NS", "name": "Nippon India ETF Gold BeES"},
                {"ticker": "HDFCGOLD.NS", "name": "HDFC Gold ETF"},
                {"ticker": "SETFGOLD.NS", "name": "SBI ETF Gold"},
                {"ticker": "GOLDIETF.NS", "name": "ICICI Pru Gold ETF"},
                {"ticker": "SGBDEC25.NS", "name": "Sovereign Gold Bond Dec 2025"},
                {"ticker": "SGBMAR28.NS", "name": "Sovereign Gold Bond Mar 2028"},
            ]},
        ]

        results = []
        for cat in INDIA_MF_UNIVERSE:
            for fund in cat["funds"]:
                ticker = fund["ticker"]
                try:
                    t = yf_mod.Ticker(ticker)
                    info = t.info or {}
                    
                    hist_5y = t.history(period="5y")
                    hist_3y = t.history(period="3y")
                    hist_1y = t.history(period="1y")

                    def calc_cagr(hist, years):
                        if hist is not None and len(hist) > 50:
                            start = float(hist['Close'].iloc[0])
                            end = float(hist['Close'].iloc[-1])
                            if start > 0:
                                return round(((end / start) ** (1 / years) - 1) * 100, 2)
                        return None

                    # Volatility (Annualized Standard Deviation)
                    volatility = None
                    if hist_1y is not None and len(hist_1y) > 20:
                        daily_returns = hist_1y['Close'].pct_change().dropna()
                        volatility = round(float(daily_returns.std() * np.sqrt(252) * 100), 2)

                    results.append({
                        "ticker": ticker,
                        "name": fund["name"],
                        "category": cat["category"],
                        "last_price": round(float(info.get("previousClose", 0)), 2) if info.get("previousClose") else None,
                        "yield": round(info.get("yield", 0) * 100, 2) if info.get("yield") else None,
                        "expense_ratio": round(info.get("annualReportExpenseRatio", 0) * 100, 2) if info.get("annualReportExpenseRatio") else None,
                        "aum": info.get("totalAssets"),
                        "return_1y": calc_cagr(hist_1y, 1),
                        "return_3y": calc_cagr(hist_3y, 3),
                        "return_5y": calc_cagr(hist_5y, 5),
                        "volatility": volatility,
                        "sparkline": [round(float(s), 2) for s in hist_1y['Close'].tail(20).tolist()] if hist_1y is not None and not hist_1y.empty else [],
                    })
                except Exception as e:
                    print(f"[IndiaMF] Error for {ticker}: {e}")
                    results.append({
                        "ticker": ticker, "name": fund["name"], "category": cat["category"],
                        "return_1y": None, "return_3y": None, "return_5y": None,
                    })

        if results:
            self._set_cached_data(cache_key, results, expiry_hours=12)
        return results

    def get_macro_overview(self) -> dict:
        """Fetches major market indices, VIX, and treasury yields with sparkline data."""
        cache_key = "macro_overview"
        cached = self._get_cached_data(cache_key)
        if cached:
            print("[DataManager] Loaded Macro Overview from DB Cache.")
            return cached
            
        import yfinance as yf_mod
        
        INDICES = [
            {"ticker": "^GSPC", "name": "S&P 500", "region": "US"},
            {"ticker": "^DJI", "name": "Dow Jones", "region": "US"},
            {"ticker": "^IXIC", "name": "NASDAQ", "region": "US"},
            {"ticker": "^FTSE", "name": "FTSE 100", "region": "EU"},
            {"ticker": "^GDAXI", "name": "DAX", "region": "EU"},
            {"ticker": "^FCHI", "name": "CAC 40", "region": "EU"},
            {"ticker": "^NSEI", "name": "Nifty 50", "region": "India"},
            {"ticker": "^BSESN", "name": "Sensex", "region": "India"},
            {"ticker": "^N225", "name": "Nikkei 225", "region": "Asia"},
            {"ticker": "^HSI", "name": "Hang Seng", "region": "Asia"},
        ]
        
        GAUGES = [
            {"ticker": "^VIX", "name": "VIX (Fear Index)", "type": "volatility"},
            {"ticker": "^TNX", "name": "US 10Y Yield", "type": "yield"},
            {"ticker": "^FVX", "name": "US 5Y Yield", "type": "yield"},
            {"ticker": "^IRX", "name": "US 13W T-Bill", "type": "yield"},
            {"ticker": "DX-Y.NYB", "name": "US Dollar Index", "type": "currency"},
        ]
        
        results = {"indices": [], "gauges": []}
        
        for item in INDICES + GAUGES:
            try:
                t = yf_mod.Ticker(item["ticker"])
                hist = t.history(period="1mo")
                hist_1y = t.history(period="1y")
                hist_5y = t.history(period="5y")
                info = t.info or {}
                
                if hist.empty:
                    continue
                
                current = round(float(hist['Close'].iloc[-1]), 2)
                prev = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current
                change_pct = round((current - prev) / prev * 100, 2) if prev else 0
                
                def calc_cagr(h, years):
                    if h is not None and len(h) > 1:
                        s = float(h['Close'].iloc[0])
                        e = float(h['Close'].iloc[-1])
                        if s > 0:
                            return round(((e / s) ** (1 / years) - 1) * 100, 2)
                    return None
                
                # Sparkline: last 20 daily closes normalized
                sparkline = hist['Close'].tail(20).tolist()
                
                entry = {
                    "ticker": item["ticker"],
                    "name": item["name"],
                    "price": current,
                    "change_pct": change_pct,
                    "return_1y": calc_cagr(hist_1y, 1),
                    "return_5y": calc_cagr(hist_5y, 5),
                    "sparkline": [round(s, 2) for s in sparkline],
                }
                
                if "region" in item:
                    entry["region"] = item["region"]
                    results["indices"].append(entry)
                else:
                    entry["type"] = item["type"]
                    results["gauges"].append(entry)
                    
            except Exception as e:
                print(f"[Macro] Error for {item['ticker']}: {e}")
        
        if results:
            self._set_cached_data(cache_key, results, expiry_hours=4)
        return results

    def get_commodities_data(self) -> list[dict]:
        """Fetches commodity prices, daily change, and 1-month sparkline."""
        cache_key = "commodities_data"
        cached = self._get_cached_data(cache_key)
        if cached:
            print("[DataManager] Loaded Commodities Data from DB Cache.")
            return cached

        import yfinance as yf_mod
        
        COMMODITIES = [
            {"ticker": "GC=F", "name": "Gold", "unit": "$/oz", "color": "#f59e0b"},
            {"ticker": "SI=F", "name": "Silver", "unit": "$/oz", "color": "#94a3b8"},
            {"ticker": "CL=F", "name": "Crude Oil (WTI)", "unit": "$/bbl", "color": "#14b8a6"},
            {"ticker": "BZ=F", "name": "Brent Crude", "unit": "$/bbl", "color": "#0ea5e9"},
            {"ticker": "NG=F", "name": "Natural Gas", "unit": "$/mmBtu", "color": "#ef4444"},
            {"ticker": "HG=F", "name": "Copper", "unit": "$/lb", "color": "#f97316"},
            {"ticker": "PL=F", "name": "Platinum", "unit": "$/oz", "color": "#6366f1"},
            {"ticker": "ZW=F", "name": "Wheat", "unit": "cents/bu", "color": "#84cc16"},
            {"ticker": "ZC=F", "name": "Corn", "unit": "cents/bu", "color": "#eab308"},
            {"ticker": "ZS=F", "name": "Soybeans", "unit": "cents/bu", "color": "#10b981"},
        ]
        
        results = []
        for item in COMMODITIES:
            try:
                t = yf_mod.Ticker(item["ticker"])
                hist_1m = t.history(period="1mo")
                hist_1y = t.history(period="1y")
                hist_5y = t.history(period="5y")
                
                if hist_1m.empty:
                    continue
                
                current = round(float(hist_1m['Close'].iloc[-1]), 2)
                prev = float(hist_1m['Close'].iloc[-2]) if len(hist_1m) > 1 else current
                day_change = round((current - prev) / prev * 100, 2) if prev else 0
                
                # Calculate period returns
                def period_return(hist):
                    if hist is not None and len(hist) > 1:
                        s, e = float(hist['Close'].iloc[0]), float(hist['Close'].iloc[-1])
                        return round((e - s) / s * 100, 2) if s > 0 else None
                    return None
                
                sparkline = hist_1m['Close'].tail(20).tolist()
                
                results.append({
                    "ticker": item["ticker"],
                    "name": item["name"],
                    "unit": item["unit"],
                    "color": item["color"],
                    "price": current,
                    "day_change": day_change,
                    "return_1m": period_return(hist_1m),
                    "return_1y": period_return(hist_1y),
                    "return_5y": period_return(hist_5y),
                    "sparkline": [round(s, 2) for s in sparkline],
                })
            except Exception as e:
                print(f"[Commodities] Error for {item['ticker']}: {e}")
        
        if results:
            self._set_cached_data(cache_key, results, expiry_hours=4)
        return results

    def get_forex_data(self) -> list[dict]:
        """Fetches major forex pairs with rates, daily change, and sparklines."""
        cache_key = "forex_data"
        cached = self._get_cached_data(cache_key)
        if cached:
            print("[DataManager] Loaded Forex Data from DB Cache.")
            return cached

        import yfinance as yf_mod
        
        PAIRS = [
            {"ticker": "EURUSD=X", "name": "EUR/USD", "base": "EUR", "quote": "USD"},
            {"ticker": "GBPUSD=X", "name": "GBP/USD", "base": "GBP", "quote": "USD"},
            {"ticker": "USDJPY=X", "name": "USD/JPY", "base": "USD", "quote": "JPY"},
            {"ticker": "USDCHF=X", "name": "USD/CHF", "base": "USD", "quote": "CHF"},
            {"ticker": "AUDUSD=X", "name": "AUD/USD", "base": "AUD", "quote": "USD"},
            {"ticker": "USDCAD=X", "name": "USD/CAD", "base": "USD", "quote": "CAD"},
            {"ticker": "USDINR=X", "name": "USD/INR", "base": "USD", "quote": "INR"},
            {"ticker": "EURGBP=X", "name": "EUR/GBP", "base": "EUR", "quote": "GBP"},
            {"ticker": "EURJPY=X", "name": "EUR/JPY", "base": "EUR", "quote": "JPY"},
            {"ticker": "GBPINR=X", "name": "GBP/INR", "base": "GBP", "quote": "INR"},
            {"ticker": "EURINR=X", "name": "EUR/INR", "base": "EUR", "quote": "INR"},
            {"ticker": "USDCNY=X", "name": "USD/CNY", "base": "USD", "quote": "CNY"},
        ]
        
        results = []
        for pair in PAIRS:
            try:
                t = yf_mod.Ticker(pair["ticker"])
                hist = t.history(period="1mo")
                hist_1y = t.history(period="1y")
                hist_5y = t.history(period="5y")
                
                if hist.empty:
                    continue
                
                current = round(float(hist['Close'].iloc[-1]), 4)
                prev = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current
                day_change = round((current - prev) / prev * 100, 4) if prev else 0
                
                month_start = float(hist['Close'].iloc[0])
                month_change = round((current - month_start) / month_start * 100, 2) if month_start else 0
                
                def calc_return(h, years):
                    if h is not None and len(h) > 1:
                        s = float(h['Close'].iloc[0])
                        e = float(h['Close'].iloc[-1])
                        if s > 0:
                            return round(((e / s) ** (1 / years) - 1) * 100, 2)
                    return None
                
                sparkline = hist['Close'].tail(20).tolist()
                
                results.append({
                    "ticker": pair["ticker"],
                    "name": pair["name"],
                    "base": pair["base"],
                    "quote": pair["quote"],
                    "rate": current,
                    "day_change": day_change,
                    "month_change": month_change,
                    "year_change": calc_return(hist_1y, 1),
                    "return_5y": calc_return(hist_5y, 5),
                    "sparkline": [round(s, 4) for s in sparkline],
                })
            except Exception as e:
                print(f"[Forex] Error for {pair['ticker']}: {e}")
        
        if results:
            self._set_cached_data(cache_key, results, expiry_hours=4)
        return results

    def get_correlation_matrix(self) -> dict:
        """Computes correlation matrix across major asset classes using 1Y daily returns."""
        cache_key = "correlation_matrix"
        cached = self._get_cached_data(cache_key)
        if cached:
            print("[DataManager] Loaded Correlation Matrix from DB Cache.")
            return cached

        import yfinance as yf_mod
        import numpy as np
        import pandas as pd
        
        ASSETS = [
            {"ticker": "^GSPC", "name": "S&P 500"},
            {"ticker": "^IXIC", "name": "NASDAQ"},
            {"ticker": "^FTSE", "name": "FTSE 100"},
            {"ticker": "^NSEI", "name": "Nifty 50"},
            {"ticker": "GC=F", "name": "Gold"},
            {"ticker": "CL=F", "name": "Crude Oil"},
            {"ticker": "^TNX", "name": "US 10Y Yield"},
            {"ticker": "^VIX", "name": "VIX"},
            {"ticker": "EURUSD=X", "name": "EUR/USD"},
            {"ticker": "DX-Y.NYB", "name": "USD Index"},
            {"ticker": "BND", "name": "US Bonds"},
            {"ticker": "BTC-USD", "name": "Bitcoin"},
        ]
        
        # Fetch 1Y daily returns for all assets
        returns_dict = {}
        for asset in ASSETS:
            try:
                t = yf_mod.Ticker(asset["ticker"])
                hist = t.history(period="1y")
                if hist is not None and len(hist) > 10:
                    returns_dict[asset["name"]] = hist['Close'].pct_change().dropna()
            except:
                pass
        
        # Align on common dates and compute correlation
        df = pd.DataFrame(returns_dict)
        
        if df.empty or len(df) < 5:
            return {"labels": [], "matrix": []}
        
        # Using pairwise correlation which handles missing values much better than global dropna()
        corr = df.corr(min_periods=10)
        
        # Remove columns/rows that resulted in all NaNs (rare but possible if no overlap)
        corr = corr.dropna(how='all', axis=0).dropna(how='all', axis=1)
        
        if corr.empty:
            return {"labels": [], "matrix": []}
        
        return {
            "labels": corr.columns.tolist(),
            "matrix": [[round(v, 3) if pd.notna(v) else 0 for v in row] for row in corr.values.tolist()],
        }

    def get_nifty500_sector_heatmap(self, start_year: int = 2015) -> dict:
        """
        Fetches annual returns + 5Y CAGR for all Nifty sectoral indices.
        Returns heatmap data sorted by 5Y CAGR (best first).
        """
        cache_key = f"nifty500_heatmap_{start_year}"
        cached = self._get_cached_data(cache_key)
        if cached:
            print(f"[DataManager] Loaded Nifty 500 Heatmap ({start_year}) from DB Cache.")
            return cached

        import yfinance as yf_mod
        from datetime import datetime

        NIFTY_SECTORS = [
            {"name": "IT", "ticker": "^CNXIT", "color": "#3b82f6"},
            {"name": "Pharma", "ticker": "^CNXPHARMA", "color": "#ef4444"},
            {"name": "Auto", "ticker": "^CNXAUTO", "color": "#f59e0b"},
            {"name": "Metal", "ticker": "^CNXMETAL", "color": "#a8a29e"},
            {"name": "FMCG", "ticker": "^CNXFMCG", "color": "#f97316"},
            {"name": "Realty", "ticker": "^CNXREALTY", "color": "#ec4899"},
            {"name": "Infrastructure", "ticker": "^CNXINFRA", "color": "#8b5cf6"},
            {"name": "Media", "ticker": "^CNXMEDIA", "color": "#64748b"},
            {"name": "PSE", "ticker": "^CNXPSE", "color": "#06b6d4"},
            {"name": "Energy", "ticker": "^CNXENERGY", "color": "#14b8a6"},
            {"name": "Bank", "ticker": "^NSEBANK", "color": "#10b981"},
            {"name": "Consumer Durables", "ticker": "^CNXCONSUM", "color": "#a855f7"},
            {"name": "Financial Services", "ticker": "NIFTY_FIN_SERVICE.NS", "color": "#22d3ee"},
            {"name": "MNC", "ticker": "^CNXMNC", "color": "#fbbf24"},
            {"name": "Services", "ticker": "^CNXSERVICE", "color": "#84cc16"},
        ]

        current_year = datetime.now().year
        results = []

        for sector in NIFTY_SECTORS:
            try:
                t = yf_mod.Ticker(sector["ticker"])
                hist = t.history(period="max")
                
                if hist.empty or len(hist) < 10:
                    continue

                # Annual returns per year
                annual_returns = {}
                for year in range(start_year, current_year + 1):
                    year_data = hist[hist.index.year == year]
                    if len(year_data) >= 2:
                        open_price = float(year_data['Close'].iloc[0])
                        close_price = float(year_data['Close'].iloc[-1])
                        if open_price > 0:
                            annual_returns[str(year)] = round(
                                (close_price - open_price) / open_price * 100, 2
                            )

                # 5Y CAGR
                hist_5y = t.history(period="5y")
                cagr_5y = None
                if hist_5y is not None and len(hist_5y) > 50:
                    start_price = float(hist_5y['Close'].iloc[0])
                    end_price = float(hist_5y['Close'].iloc[-1])
                    if start_price > 0:
                        cagr_5y = round(((end_price / start_price) ** (1 / 5) - 1) * 100, 2)

                # 1Y return
                hist_1y = t.history(period="1y")
                return_1y = None
                if hist_1y is not None and len(hist_1y) > 10:
                    s = float(hist_1y['Close'].iloc[0])
                    e = float(hist_1y['Close'].iloc[-1])
                    if s > 0:
                        return_1y = round((e - s) / s * 100, 2)

                # Current price
                current_price = round(float(hist['Close'].iloc[-1]), 2)

                results.append({
                    "sector": sector["name"],
                    "ticker": sector["ticker"],
                    "color": sector["color"],
                    "price": current_price,
                    "return_1y": return_1y,
                    "cagr_5y": cagr_5y,
                    "returns": annual_returns,
                })

            except Exception as e:
                print(f"[Nifty500] Error for {sector['name']}: {e}")

        # Sort by 5Y CAGR descending (best performers first)
        results.sort(key=lambda x: x.get("cagr_5y") or -999, reverse=True)

        # Build years list
        all_years = set()
        for r in results:
            all_years.update(r["returns"].keys())
        years = sorted(all_years)

        if results:
            self._set_cached_data(cache_key, {"sectors": results, "years": years}, expiry_hours=4)
        return {"sectors": results, "years": years}

    def get_etf_analysis(self, region: str = "US") -> dict:
        """
        Comprehensive ETF analysis for a given region.
        Returns ranked ETFs with metrics: 5Y CAGR, 1Y return, 3M return,
        volatility, Sharpe ratio, max drawdown, dividend yield.
        """
        cache_key = f"etf_analysis_{region}"
        cached = self._get_cached_data(cache_key)
        if cached:
            print(f"[DataManager] Loaded ETF Analysis ({region}) from DB Cache.")
            return cached

        import yfinance as yf_mod
        import numpy as np

        ETF_UNIVERSE = {
            "US": [
                {"ticker": "VOO", "name": "Vanguard S&P 500", "focus": "US Large Cap"},
                {"ticker": "QQQ", "name": "Invesco QQQ (NASDAQ 100)", "focus": "US Tech/Growth"},
                {"ticker": "VTI", "name": "Vanguard Total Stock Market", "focus": "US All Cap"},
                {"ticker": "IWM", "name": "iShares Russell 2000", "focus": "US Small Cap"},
                {"ticker": "VO", "name": "Vanguard Mid-Cap", "focus": "US Mid Cap"},
                {"ticker": "XLK", "name": "Technology Select SPDR", "focus": "US Technology"},
                {"ticker": "XLV", "name": "Health Care Select SPDR", "focus": "US Healthcare"},
                {"ticker": "XLF", "name": "Financial Select SPDR", "focus": "US Financials"},
                {"ticker": "XLE", "name": "Energy Select SPDR", "focus": "US Energy"},
                {"ticker": "XLI", "name": "Industrial Select SPDR", "focus": "US Industrials"},
                {"ticker": "VNQ", "name": "Vanguard Real Estate", "focus": "US Real Estate"},
                {"ticker": "GLD", "name": "SPDR Gold Shares", "focus": "Gold"},
                {"ticker": "BND", "name": "Vanguard Total Bond Market", "focus": "US Bonds"},
                {"ticker": "SCHD", "name": "Schwab US Dividend Equity", "focus": "US Dividend"},
                {"ticker": "VIG", "name": "Vanguard Dividend Appreciation", "focus": "US Dividend Growth"},
            ],
            "EU": [
                {"ticker": "VWRL.L", "name": "Vanguard FTSE All-World", "focus": "Global Equity"},
                {"ticker": "CSPX.L", "name": "iShares Core S&P 500 UCITS", "focus": "S&P 500 EUR"},
                {"ticker": "SWDA.L", "name": "iShares Core MSCI World", "focus": "Developed World"},
                {"ticker": "IS3N.DE", "name": "iShares Core MSCI EM IMI", "focus": "Emerging Markets"},
                {"ticker": "EXV8.DE", "name": "iShares STOXX 600 Technology", "focus": "EU Technology"},
                {"ticker": "EXV1.DE", "name": "iShares STOXX 600 Banks", "focus": "EU Banks"},
                {"ticker": "EXV4.DE", "name": "iShares STOXX 600 Health Care", "focus": "EU Healthcare"},
                {"ticker": "EXV6.DE", "name": "iShares STOXX 600 Oil & Gas", "focus": "EU Energy"},
                {"ticker": "EXV2.DE", "name": "iShares STOXX 600 Industrial", "focus": "EU Industrials"},
                {"ticker": "EXV5.DE", "name": "iShares STOXX 600 Automobiles", "focus": "EU Autos"},
                {"ticker": "IQQP.DE", "name": "iShares European Property", "focus": "EU Real Estate"},
                {"ticker": "SMCX.L", "name": "iShares MSCI Europe Small Cap", "focus": "EU Small Cap"},
                {"ticker": "WSML.L", "name": "iShares MSCI World Small Cap", "focus": "Global Small Cap"},
                {"ticker": "EUMD.L", "name": "iShares STOXX Europe Mid 200", "focus": "EU Mid Cap"},
            ],
            "India": [
                {"ticker": "NIFTYBEES.NS", "name": "Nippon India Nifty 50 BeES", "focus": "Nifty 50"},
                {"ticker": "JUNIORBEES.NS", "name": "Nippon India Nifty Next 50", "focus": "Next 50"},
                {"ticker": "BANKBEES.NS", "name": "Nippon India Bank BeES", "focus": "Banking"},
                {"ticker": "ITBEES.NS", "name": "Nippon India IT ETF", "focus": "IT Sector"},
                {"ticker": "PHARMABEES.NS", "name": "Nippon India Pharma ETF", "focus": "Pharma"},
                {"ticker": "GOLDBEES.NS", "name": "Nippon India Gold BeES", "focus": "Gold"},
                {"ticker": "SETFNIF50.NS", "name": "SBI Nifty 50 ETF", "focus": "Nifty 50"},
                {"ticker": "M100.NS", "name": "Motilal Oswal Midcap 100", "focus": "Midcap 100"},
                {"ticker": "SETFNIFBK.NS", "name": "SBI Nifty Bank ETF", "focus": "Banking"},
                {"ticker": "ICICIM150.NS", "name": "ICICI Pru Midcap 150", "focus": "Midcap 150"},
                {"ticker": "SILVERBEES.NS", "name": "Nippon India Silver ETF", "focus": "Silver"},
                {"ticker": "NV20IETF.NS", "name": "ICICI Pru NV20 ETF", "focus": "Value 20"},
            ],
        }

        etfs = ETF_UNIVERSE.get(region, ETF_UNIVERSE["US"])
        results = []

        for etf in etfs:
            try:
                t = yf_mod.Ticker(etf["ticker"])
                info = t.info or {}
                hist_5y = t.history(period="5y")
                hist_1y = t.history(period="1y")
                hist_3m = t.history(period="3mo")

                if hist_5y is None or hist_5y.empty or len(hist_5y) < 50:
                    continue

                current = float(hist_5y['Close'].iloc[-1])

                # 5Y CAGR
                start_5y = float(hist_5y['Close'].iloc[0])
                cagr_5y = round(((current / start_5y) ** (1 / 5) - 1) * 100, 2) if start_5y > 0 else None

                # 1Y Return
                return_1y = None
                if hist_1y is not None and len(hist_1y) > 10:
                    s1 = float(hist_1y['Close'].iloc[0])
                    return_1y = round((current - s1) / s1 * 100, 2) if s1 > 0 else None

                # 3M Return (Momentum)
                return_3m = None
                if hist_3m is not None and len(hist_3m) > 5:
                    s3 = float(hist_3m['Close'].iloc[0])
                    return_3m = round((current - s3) / s3 * 100, 2) if s3 > 0 else None

                # Daily returns for volatility & Sharpe
                daily_returns = hist_5y['Close'].pct_change().dropna()
                volatility = round(float(daily_returns.std() * np.sqrt(252) * 100), 2)

                # Sharpe Ratio (assuming 4% risk-free rate)
                annual_return = cagr_5y / 100 if cagr_5y else 0
                sharpe = round((annual_return - 0.04) / (volatility / 100), 2) if volatility > 0 else 0

                # Max Drawdown
                cumulative = (1 + daily_returns).cumprod()
                peak = cumulative.cummax()
                drawdown = ((cumulative - peak) / peak)
                max_drawdown = round(float(drawdown.min() * 100), 2)

                # Dividend Yield
                div_yield = info.get("yield") or info.get("dividendYield") or 0
                div_yield_pct = round(div_yield * 100, 2) if div_yield else 0

                # Expense ratio
                expense = info.get("annualReportExpenseRatio")
                expense_pct = round(expense * 100, 2) if expense else None

                results.append({
                    "ticker": etf["ticker"],
                    "name": etf["name"],
                    "focus": etf["focus"],
                    "price": round(current, 2),
                    "currency": info.get("currency", "USD"),
                    "cagr_5y": cagr_5y,
                    "return_1y": return_1y,
                    "return_3m": return_3m,
                    "volatility": volatility,
                    "sharpe": sharpe,
                    "max_drawdown": max_drawdown,
                    "dividend_yield": div_yield_pct,
                    "expense_ratio": expense_pct,
                })
                print(f"  [Analysis] {etf['ticker']}: CAGR={cagr_5y}%, Sharpe={sharpe}")

            except Exception as e:
                print(f"  [Analysis] Error {etf['ticker']}: {e}")

        if results:
            self._set_cached_data(cache_key, {
                "region": region,
                "etfs": results,
                "count": len(results),
            }, expiry_hours=12)
        return {
            "region": region,
            "etfs": results,
            "count": len(results),
        }

    def get_market_news(self, region: str = "US") -> list:
        """Fetches market news for a region using major index/ETF tickers."""
        cache_key = f"market_news_{region}"
        cached = self._get_cached_data(cache_key)
        if cached:
            print(f"[DataManager] Loaded Market News ({region}) from DB Cache.")
            return cached

        import yfinance as yf_mod

        NEWS_TICKERS = {
            "US": ["SPY", "QQQ", "XLK", "XLF", "XLE", "XLV", "GLD"],
            "EU": ["EWG", "EWQ", "EWU", "CSPX.L", "VWRL.L", "EXV8.DE"],
            "India": ["INDA", "INDY", "NIFTYBEES.NS", "BANKBEES.NS"],
        }

        tickers = NEWS_TICKERS.get(region, NEWS_TICKERS["US"])
        seen_titles = set()
        news_items = []

        for tick_symbol in tickers:
            try:
                t = yf_mod.Ticker(tick_symbol)
                for item in (t.news or []):
                    # New yfinance format: data nested under 'content'
                    content = item.get("content", item)
                    title = content.get("title", "")
                    if title in seen_titles or not title:
                        continue
                    seen_titles.add(title)

                    # Date
                    date_str = content.get("pubDate", content.get("displayTime", ""))
                    if date_str:
                        date_str = date_str[:16].replace("T", " ")

                    # Publisher
                    provider = content.get("provider", {})
                    publisher = provider.get("displayName", "") if isinstance(provider, dict) else str(provider)

                    # Link
                    canonical = content.get("canonicalUrl", {})
                    link = canonical.get("url", "") if isinstance(canonical, dict) else content.get("previewUrl", content.get("link", ""))

                    # Thumbnail
                    thumb = ""
                    thumb_data = content.get("thumbnail", {})
                    if thumb_data and isinstance(thumb_data, dict):
                        resolutions = thumb_data.get("resolutions", [])
                        if resolutions:
                            thumb = resolutions[0].get("url", "")

                    # Summary
                    summary = content.get("summary", "")

                    news_items.append({
                        "title": title,
                        "publisher": publisher,
                        "link": link,
                        "date": date_str,
                        "summary": summary,
                        "thumbnail": thumb,
                        "related": [],
                    })
            except Exception as e:
                print(f"[News] Error {tick_symbol}: {e}")

        # Sort by date descending
        news_items.sort(key=lambda x: x.get("date", ""), reverse=True)
        results = news_items[:30]
        if results:
            self._set_cached_data(cache_key, results, expiry_hours=1) # News expires quickly
        return results

    def get_allocation_advice(self) -> dict:
        """
        Compiles allocation strategies from world-class investors,
        computes a recommended average, and compares with user portfolio.
        """
        cache_key = "allocation_advice"
        cached = self._get_cached_data(cache_key)
        # We only cache if portfolio results haven't changed, but simpler to cache for a short time
        # or just skip DB cache for this since it depends on the USER's portfolio in the DB.
        # Actually, let's skip DB cache for allocation advice as it's computed from local DB anyway.
        
        from data.database import SessionLocal, PortfolioHolding

        # --- Famous Investor Allocation Models ---
        strategies = [
            {
                "name": "John Bogle (Vanguard Founder)",
                "philosophy": "Keep it simple. Low-cost index funds. Your age in bonds, rest in stocks.",
                "allocation": {
                    "US Equity": 40, "International Equity": 20, "Bonds": 30,
                    "Real Estate": 0, "Commodities/Gold": 0, "Cash": 10,
                },
            },
            {
                "name": "Ray Dalio (All-Weather Portfolio)",
                "philosophy": "Balance risk across economic environments. Protect against inflation, deflation, growth, and recession.",
                "allocation": {
                    "US Equity": 30, "International Equity": 0, "Bonds": 40,
                    "Real Estate": 0, "Commodities/Gold": 15, "Cash": 15,
                },
            },
            {
                "name": "Warren Buffett (90/10 Rule)",
                "philosophy": "Put 90% in a low-cost S&P 500 index fund and 10% in short-term government bonds.",
                "allocation": {
                    "US Equity": 70, "International Equity": 20, "Bonds": 10,
                    "Real Estate": 0, "Commodities/Gold": 0, "Cash": 0,
                },
            },
            {
                "name": "David Swensen (Yale Endowment Model)",
                "philosophy": "Diversify broadly across uncorrelated asset classes for long-term growth.",
                "allocation": {
                    "US Equity": 30, "International Equity": 15, "Bonds": 15,
                    "Real Estate": 20, "Commodities/Gold": 10, "Cash": 10,
                },
            },
            {
                "name": "Modern Balanced (Financial Planners Consensus)",
                "philosophy": "A balanced approach for working professionals: growth + stability + inflation hedge.",
                "allocation": {
                    "US Equity": 35, "International Equity": 15, "Bonds": 20,
                    "Real Estate": 10, "Commodities/Gold": 10, "Cash": 10,
                },
            },
        ]

        # --- Compute recommended average ---
        categories = ["US Equity", "International Equity", "Bonds", "Real Estate", "Commodities/Gold", "Cash"]
        recommended = {}
        for cat in categories:
            vals = [s["allocation"].get(cat, 0) for s in strategies]
            recommended[cat] = round(sum(vals) / len(vals), 1)

        # Normalize to 100%
        total = sum(recommended.values())
        if total != 100:
            recommended = {k: round(v / total * 100, 1) for k, v in recommended.items()}

        # --- Map ETF tickers to asset categories ---
        FOCUS_MAP = {
            "US Large Cap": "US Equity", "US Tech/Growth": "US Equity", "US All Cap": "US Equity",
            "US Small Cap": "US Equity", "US Mid Cap": "US Equity", "US Technology": "US Equity",
            "US Healthcare": "US Equity", "US Financials": "US Equity", "US Energy": "US Equity",
            "US Industrials": "US Equity", "US Dividend": "US Equity", "US Dividend Growth": "US Equity",
            "S&P 500": "US Equity", "NASDAQ 100": "US Equity", "Nifty 50": "International Equity",
            "Next 50": "International Equity", "Banking": "International Equity", "IT Sector": "International Equity",
            "Pharma": "International Equity", "Midcap 100": "International Equity", "Midcap 150": "International Equity",
            "Value 20": "International Equity",
            "Global Equity": "International Equity", "Developed World": "International Equity",
            "Emerging Markets": "International Equity", "EU Technology": "International Equity",
            "EU Banks": "International Equity", "EU Healthcare": "International Equity",
            "EU Energy": "International Equity", "EU Industrials": "International Equity",
            "EU Autos": "International Equity", "EU Small Cap": "International Equity",
            "Global Small Cap": "International Equity", "EU Mid Cap": "International Equity",
            "S&P 500 EUR": "International Equity",
            "Gold": "Commodities/Gold", "Silver": "Commodities/Gold",
            "US Bonds": "Bonds", "US Real Estate": "Real Estate", "EU Real Estate": "Real Estate",
        }

        # --- Get user's actual allocation ---
        user_allocation = {}
        has_portfolio = False
        try:
            session = SessionLocal()
            holdings = session.query(PortfolioHolding).all()
            total_invested = sum((h.lump_sum or 0) for h in holdings)
            if total_invested > 0:
                has_portfolio = True
                for h in holdings:
                    cat = FOCUS_MAP.get(h.name, "US Equity")  # fallback
                    # Also try matching by common patterns in name
                    name_lower = (h.name or "").lower()
                    if "gold" in name_lower:
                        cat = "Commodities/Gold"
                    elif "silver" in name_lower:
                        cat = "Commodities/Gold"
                    elif "bond" in name_lower:
                        cat = "Bonds"
                    elif "real estate" in name_lower or "reit" in name_lower or "property" in name_lower:
                        cat = "Real Estate"
                    elif any(x in name_lower for x in ["nifty", "india", "sensex", "bse", "pharma", "bank"]):
                        cat = "International Equity"
                    elif any(x in name_lower for x in ["europe", "eu ", "stoxx", "msci world", "all-world", "ftse"]):
                        cat = "International Equity"
                    elif any(x in name_lower for x in ["s&p 500", "s&p500", "nasdaq", "russell", "vanguard total"]):
                        cat = "US Equity"
                    amt = h.lump_sum or 0
                    user_allocation[cat] = user_allocation.get(cat, 0) + amt
                # Convert to percentages
                for k in user_allocation:
                    user_allocation[k] = round(user_allocation[k] / total_invested * 100, 1)
            session.close()
        except Exception as e:
            print(f"[Allocation] Error reading portfolio: {e}")

        # --- Generate suggestions ---
        suggestions = []
        if has_portfolio:
            for cat in categories:
                rec = recommended.get(cat, 0)
                actual = user_allocation.get(cat, 0)
                diff = actual - rec
                if diff > 10:
                    suggestions.append(f"⚠️ You're **overweight in {cat}** ({actual}% vs recommended {rec}%). Consider rebalancing to reduce concentration risk.")
                elif diff < -10:
                    suggestions.append(f"💡 You're **underweight in {cat}** ({actual}% vs recommended {rec}%). Adding exposure here could improve diversification.")
            if not suggestions:
                suggestions.append("✅ Your portfolio is well-diversified and closely matches the recommended allocation. Great job!")
        else:
            suggestions.append("💡 Add investment amounts (lump sum) to your Portfolio holdings to see a personalized comparison against the recommended allocation.")
            suggestions.append("📊 The recommended allocation below is an average of strategies from Bogle, Dalio, Buffett, Swensen, and modern financial planners.")

        return {
            "strategies": strategies,
            "recommended": recommended,
            "user_allocation": user_allocation if has_portfolio else None,
            "has_portfolio": has_portfolio,
            "suggestions": suggestions,
        }

    def seed_ticker_registry(self):
        """Populates the TickerRegistry with all ETFs/MFs/Indices from every page."""
        TICKERS = [
            # --- US Sector ETFs ---
            {"ticker": "XLK", "name": "Technology Select Sector SPDR", "category": "ETF", "sector": "Technology", "market": "US", "exchange": "NYSE"},
            {"ticker": "VGT", "name": "Vanguard Information Technology", "category": "ETF", "sector": "Technology", "market": "US", "exchange": "NYSE"},
            {"ticker": "XLF", "name": "Financial Select Sector SPDR", "category": "ETF", "sector": "Financials", "market": "US", "exchange": "NYSE"},
            {"ticker": "VFH", "name": "Vanguard Financials", "category": "ETF", "sector": "Financials", "market": "US", "exchange": "NYSE"},
            {"ticker": "XLV", "name": "Health Care Select Sector SPDR", "category": "ETF", "sector": "Healthcare", "market": "US", "exchange": "NYSE"},
            {"ticker": "VHT", "name": "Vanguard Health Care", "category": "ETF", "sector": "Healthcare", "market": "US", "exchange": "NYSE"},
            {"ticker": "XLY", "name": "Consumer Discretionary Select SPDR", "category": "ETF", "sector": "Consumer Discr.", "market": "US", "exchange": "NYSE"},
            {"ticker": "XLP", "name": "Consumer Staples Select SPDR", "category": "ETF", "sector": "Consumer Staples", "market": "US", "exchange": "NYSE"},
            {"ticker": "XLE", "name": "Energy Select Sector SPDR", "category": "ETF", "sector": "Energy", "market": "US", "exchange": "NYSE"},
            {"ticker": "XLB", "name": "Materials Select Sector SPDR", "category": "ETF", "sector": "Materials", "market": "US", "exchange": "NYSE"},
            {"ticker": "XLI", "name": "Industrial Select Sector SPDR", "category": "ETF", "sector": "Industrials", "market": "US", "exchange": "NYSE"},
            {"ticker": "XLU", "name": "Utilities Select Sector SPDR", "category": "ETF", "sector": "Utilities", "market": "US", "exchange": "NYSE"},
            {"ticker": "VNQ", "name": "Vanguard Real Estate", "category": "ETF", "sector": "Real Estate", "market": "US", "exchange": "NYSE"},
            {"ticker": "XLC", "name": "Communication Services Select SPDR", "category": "ETF", "sector": "Communication", "market": "US", "exchange": "NYSE"},
            # --- US Broad Market ---
            {"ticker": "SPY", "name": "SPDR S&P 500 ETF", "category": "ETF", "sector": "Broad Market", "market": "US", "exchange": "NYSE"},
            {"ticker": "VOO", "name": "Vanguard S&P 500 ETF", "category": "ETF", "sector": "Broad Market", "market": "US", "exchange": "NYSE"},
            {"ticker": "ACWI", "name": "iShares MSCI ACWI ETF", "category": "ETF", "sector": "Global Equity", "market": "Global", "exchange": "NASDAQ"},
            {"ticker": "VT", "name": "Vanguard Total World Stock ETF", "category": "ETF", "sector": "Global Equity", "market": "Global", "exchange": "NYSE"},
            {"ticker": "QQQ", "name": "Invesco QQQ Trust (NASDAQ 100)", "category": "ETF", "sector": "Broad Market", "market": "US", "exchange": "NASDAQ"},
            {"ticker": "VTI", "name": "Vanguard Total Stock Market", "category": "ETF", "sector": "Broad Market", "market": "US", "exchange": "NYSE"},
            {"ticker": "IWM", "name": "iShares Russell 2000 (Small Cap)", "category": "ETF", "sector": "Small Cap", "market": "US", "exchange": "NYSE"},
            {"ticker": "MDY", "name": "SPDR S&P MidCap 400", "category": "ETF", "sector": "Mid Cap", "market": "US", "exchange": "NYSE"},
            {"ticker": "IJR", "name": "iShares S&P Small-Cap", "category": "ETF", "sector": "Small Cap", "market": "US", "exchange": "NYSE"},
            {"ticker": "VB", "name": "Vanguard Small-Cap", "category": "ETF", "sector": "Small Cap", "market": "US", "exchange": "NYSE"},
            {"ticker": "VO", "name": "Vanguard Mid-Cap", "category": "ETF", "sector": "Mid Cap", "market": "US", "exchange": "NYSE"},
            # --- US Bond ETFs ---
            {"ticker": "BND", "name": "Vanguard Total Bond Market", "category": "ETF", "sector": "Fixed Income", "market": "US", "exchange": "NYSE"},
            {"ticker": "AGG", "name": "iShares Core US Aggregate Bond", "category": "ETF", "sector": "Fixed Income", "market": "US", "exchange": "NYSE"},
            {"ticker": "TLT", "name": "iShares 20+ Year Treasury", "category": "ETF", "sector": "Fixed Income", "market": "US", "exchange": "NYSE"},
            {"ticker": "SHY", "name": "iShares 1-3 Year Treasury", "category": "ETF", "sector": "Fixed Income", "market": "US", "exchange": "NYSE"},
            {"ticker": "LQD", "name": "iShares Investment Grade Corporate", "category": "ETF", "sector": "Fixed Income", "market": "US", "exchange": "NYSE"},
            {"ticker": "HYG", "name": "iShares High Yield Corporate", "category": "ETF", "sector": "Fixed Income", "market": "US", "exchange": "NYSE"},
            {"ticker": "VCSH", "name": "Vanguard Short-Term Corp Bond", "category": "ETF", "sector": "Fixed Income", "market": "US", "exchange": "NYSE"},
            {"ticker": "VCIT", "name": "Vanguard Intermediate-Term Corp Bond", "category": "ETF", "sector": "Fixed Income", "market": "US", "exchange": "NYSE"},
            # --- EU ETFs ---
            {"ticker": "EXV8.DE", "name": "iShares STOXX Europe 600 Technology", "category": "ETF", "sector": "Technology", "market": "EU", "exchange": "XETRA"},
            {"ticker": "EXV1.DE", "name": "iShares STOXX Europe 600 Banks", "category": "ETF", "sector": "Financials", "market": "EU", "exchange": "XETRA"},
            {"ticker": "EXV4.DE", "name": "iShares STOXX Europe 600 Health Care", "category": "ETF", "sector": "Healthcare", "market": "EU", "exchange": "XETRA"},
            {"ticker": "EXV5.DE", "name": "iShares STOXX Europe 600 Automobiles", "category": "ETF", "sector": "Autos", "market": "EU", "exchange": "XETRA"},
            {"ticker": "EXV7.DE", "name": "iShares STOXX Europe 600 Food & Beverage", "category": "ETF", "sector": "Consumer Staples", "market": "EU", "exchange": "XETRA"},
            {"ticker": "EXV6.DE", "name": "iShares STOXX Europe 600 Oil & Gas", "category": "ETF", "sector": "Energy", "market": "EU", "exchange": "XETRA"},
            {"ticker": "EXV3.DE", "name": "iShares STOXX Europe 600 Basic Resources", "category": "ETF", "sector": "Materials", "market": "EU", "exchange": "XETRA"},
            {"ticker": "EXV2.DE", "name": "iShares STOXX Europe 600 Industrial", "category": "ETF", "sector": "Industrials", "market": "EU", "exchange": "XETRA"},
            {"ticker": "EXV9.DE", "name": "iShares STOXX Europe 600 Utilities", "category": "ETF", "sector": "Utilities", "market": "EU", "exchange": "XETRA"},
            {"ticker": "IQQP.DE", "name": "iShares European Property Yield", "category": "ETF", "sector": "Real Estate", "market": "EU", "exchange": "XETRA"},
            {"ticker": "EXH8.DE", "name": "iShares STOXX Europe 600 Telecom", "category": "ETF", "sector": "Telecom", "market": "EU", "exchange": "XETRA"},
            {"ticker": "SMCX.L", "name": "iShares MSCI Europe Small Cap", "category": "ETF", "sector": "Small Cap", "market": "EU", "exchange": "LSE"},
            # --- Global ETFs ---
            {"ticker": "VWRL.L", "name": "Vanguard FTSE All-World UCITS", "category": "ETF", "sector": "Broad Market", "market": "Global", "exchange": "LSE"},
            {"ticker": "SWDA.L", "name": "iShares Core MSCI World", "category": "ETF", "sector": "Broad Market", "market": "Global", "exchange": "LSE"},
            {"ticker": "WSML.L", "name": "iShares MSCI World Small Cap", "category": "ETF", "sector": "Small Cap", "market": "Global", "exchange": "LSE"},
            {"ticker": "CSPX.L", "name": "iShares Core S&P 500 UCITS", "category": "ETF", "sector": "Broad Market", "market": "Global", "exchange": "LSE"},
            {"ticker": "IS3N.DE", "name": "iShares Core MSCI EM IMI", "category": "ETF", "sector": "Emerging Markets", "market": "Global", "exchange": "XETRA"},
            {"ticker": "EEMS", "name": "iShares MSCI EM Small-Cap", "category": "ETF", "sector": "Emerging Markets", "market": "Global", "exchange": "NYSE"},
            {"ticker": "VSS", "name": "Vanguard FTSE All-World ex-US Small-Cap", "category": "ETF", "sector": "Small Cap", "market": "Global", "exchange": "NYSE"},
            {"ticker": "SCZ", "name": "iShares MSCI EAFE Small-Cap", "category": "ETF", "sector": "Small Cap", "market": "Global", "exchange": "NYSE"},
            # --- Commodity ETFs ---
            {"ticker": "GLD", "name": "SPDR Gold Shares", "category": "ETF", "sector": "Commodity", "market": "US", "exchange": "NYSE"},
            {"ticker": "SLV", "name": "iShares Silver Trust", "category": "ETF", "sector": "Commodity", "market": "US", "exchange": "NYSE"},
            {"ticker": "USO", "name": "United States Oil Fund", "category": "ETF", "sector": "Commodity", "market": "US", "exchange": "NYSE"},
            {"ticker": "PPLT", "name": "abrdn Platinum Shares", "category": "ETF", "sector": "Commodity", "market": "US", "exchange": "NYSE"},
            {"ticker": "DBA", "name": "Invesco DB Agriculture Fund", "category": "ETF", "sector": "Commodity", "market": "US", "exchange": "NYSE"},
            # --- India ETFs ---
            {"ticker": "NIFTYBEES.NS", "name": "Nippon India Nifty 50 BeES", "category": "ETF", "sector": "Broad Market", "market": "India", "exchange": "NSE"},
            {"ticker": "BANKBEES.NS", "name": "Nippon India Bank BeES", "category": "ETF", "sector": "Financials", "market": "India", "exchange": "NSE"},
            {"ticker": "GOLDBEES.NS", "name": "Nippon India Gold BeES", "category": "ETF", "sector": "Commodity", "market": "India", "exchange": "NSE"},
            {"ticker": "M100.NS", "name": "Motilal Oswal Midcap 100 ETF", "category": "ETF", "sector": "Mid Cap", "market": "India", "exchange": "NSE"},
            {"ticker": "ITBEES.NS", "name": "Nippon India IT ETF", "category": "ETF", "sector": "Technology", "market": "India", "exchange": "NSE"},
            {"ticker": "PHARMABEES.NS", "name": "Nippon India Pharma ETF", "category": "ETF", "sector": "Healthcare", "market": "India", "exchange": "NSE"},
            {"ticker": "JUNIORBEES.NS", "name": "Nippon India Nifty Next 50 BeES", "category": "ETF", "sector": "Broad Market", "market": "India", "exchange": "NSE"},
            {"ticker": "SETFNIF50.NS", "name": "SBI Nifty 50 ETF", "category": "ETF", "sector": "Broad Market", "market": "India", "exchange": "NSE"},
            # --- User Specific ---
            {"ticker": "BG.VI", "name": "BAWAG Group AG", "category": "Stock", "sector": "Financials", "market": "EU", "exchange": "Vienna"},
            # --- Nifty Sectoral Indices ---
            {"ticker": "^CNXIT", "name": "Nifty IT", "category": "Index", "sector": "Technology", "market": "India", "exchange": "NSE"},
            {"ticker": "^CNXPHARMA", "name": "Nifty Pharma", "category": "Index", "sector": "Healthcare", "market": "India", "exchange": "NSE"},
            {"ticker": "^CNXAUTO", "name": "Nifty Auto", "category": "Index", "sector": "Auto", "market": "India", "exchange": "NSE"},
            {"ticker": "^CNXMETAL", "name": "Nifty Metal", "category": "Index", "sector": "Materials", "market": "India", "exchange": "NSE"},
            {"ticker": "^CNXFMCG", "name": "Nifty FMCG", "category": "Index", "sector": "Consumer Staples", "market": "India", "exchange": "NSE"},
            {"ticker": "^NSEBANK", "name": "Nifty Bank", "category": "Index", "sector": "Financials", "market": "India", "exchange": "NSE"},
            {"ticker": "^CNXENERGY", "name": "Nifty Energy", "category": "Index", "sector": "Energy", "market": "India", "exchange": "NSE"},
            {"ticker": "NIFTY_FIN_SERVICE.NS", "name": "Nifty Financial Services", "category": "Index", "sector": "Financials", "market": "India", "exchange": "NSE"},
            # --- Global Indices ---
            {"ticker": "^GSPC", "name": "S&P 500", "category": "Index", "sector": "Broad Market", "market": "US", "exchange": "NYSE"},
            {"ticker": "^DJI", "name": "Dow Jones Industrial", "category": "Index", "sector": "Broad Market", "market": "US", "exchange": "NYSE"},
            {"ticker": "^IXIC", "name": "NASDAQ Composite", "category": "Index", "sector": "Broad Market", "market": "US", "exchange": "NASDAQ"},
            {"ticker": "^FTSE", "name": "FTSE 100", "category": "Index", "sector": "Broad Market", "market": "EU", "exchange": "LSE"},
            {"ticker": "^GDAXI", "name": "DAX", "category": "Index", "sector": "Broad Market", "market": "EU", "exchange": "XETRA"},
            {"ticker": "^FCHI", "name": "CAC 40", "category": "Index", "sector": "Broad Market", "market": "EU", "exchange": "Paris"},
            {"ticker": "^NSEI", "name": "Nifty 50", "category": "Index", "sector": "Broad Market", "market": "India", "exchange": "NSE"},
            {"ticker": "^BSESN", "name": "Sensex", "category": "Index", "sector": "Broad Market", "market": "India", "exchange": "BSE"},
            {"ticker": "^N225", "name": "Nikkei 225", "category": "Index", "sector": "Broad Market", "market": "Global", "exchange": "Tokyo"},
            {"ticker": "^HSI", "name": "Hang Seng", "category": "Index", "sector": "Broad Market", "market": "Global", "exchange": "HKEX"},
        ]

        session = SessionLocal()
        try:
            count = 0
            for t in TICKERS:
                existing = session.query(TickerRegistry).filter_by(ticker=t["ticker"]).first()
                if not existing:
                    session.add(TickerRegistry(**t))
                    count += 1
            session.commit()
            print(f"[Seed] Added {count} new tickers to registry (total: {session.query(TickerRegistry).count()})")
        finally:
            session.close()

    def search_tickers(self, query: str) -> list:
        """Search ticker registry by name or ticker symbol."""
        session = SessionLocal()
        try:
            q = f"%{query}%"
            results = session.query(TickerRegistry).filter(
                (TickerRegistry.ticker.ilike(q)) | (TickerRegistry.name.ilike(q))
            ).limit(20).all()
            return [{
                "ticker": r.ticker,
                "name": r.name,
                "category": r.category,
                "sector": r.sector,
                "market": r.market,
            } for r in results]
        finally:
            session.close()

    def add_to_portfolio(self, ticker: str, name: str = "", lump_sum: float = 0, monthly_sip: float = 0, currency: str = "USD") -> dict:
        """Add a ticker to the portfolio."""
        session = SessionLocal()
        try:
            existing = session.query(PortfolioHolding).filter_by(ticker=ticker).first()
            if existing:
                return {"status": "exists", "message": f"{ticker} is already in portfolio"}
            
            # Lookup name from registry if not provided
            if not name:
                reg = session.query(TickerRegistry).filter_by(ticker=ticker).first()
                name = reg.name if reg else ticker

            holding = PortfolioHolding(
                ticker=ticker,
                name=name,
                lump_sum=lump_sum,
                monthly_sip=monthly_sip,
                currency=currency,
            )
            session.add(holding)
            session.commit()
            return {"status": "added", "ticker": ticker, "name": name}
        finally:
            session.close()

    def remove_from_portfolio(self, ticker: str) -> dict:
        """Remove a ticker from the portfolio."""
        session = SessionLocal()
        try:
            holding = session.query(PortfolioHolding).filter_by(ticker=ticker).first()
            if not holding:
                return {"status": "not_found", "message": f"{ticker} not in portfolio"}
            session.delete(holding)
            session.commit()
            return {"status": "removed", "ticker": ticker}
        finally:
            session.close()

    def update_portfolio_holding(self, ticker: str, lump_sum: float = None, monthly_sip: float = None) -> dict:
        """Update investment amounts for a portfolio holding."""
        session = SessionLocal()
        try:
            holding = session.query(PortfolioHolding).filter_by(ticker=ticker).first()
            if not holding:
                return {"status": "not_found"}
            if lump_sum is not None:
                holding.lump_sum = lump_sum
            if monthly_sip is not None:
                holding.monthly_sip = monthly_sip
            session.commit()
            return {"status": "updated", "ticker": ticker, "lump_sum": holding.lump_sum, "monthly_sip": holding.monthly_sip}
        finally:
            session.close()

    def get_dashboard_summary(self) -> dict:
        """
        Computes a live portfolio dashboard: total value, daily P&L,
        top/worst performers, asset allocation by category, and market pulse.
        """
        import yfinance as yf_mod
        from data.database import SessionLocal, PortfolioHolding

        session = SessionLocal()
        try:
            holdings = session.query(PortfolioHolding).all()
            if not holdings:
                return {
                    "total_value": 0, "daily_pnl": 0, "daily_pnl_pct": 0,
                    "holdings_count": 0, "top_performers": [], "worst_performers": [],
                    "allocation": [], "market_pulse": self._get_market_pulse(),
                }
        finally:
            session.close()

        performers = []
        allocation_map = {}  # category -> total invested
        total_invested = 0

        for h in holdings:
            try:
                t = yf_mod.Ticker(h.ticker)
                info = t.info or {}
                hist_1m = t.history(period="1mo")
                if hist_1m.empty:
                    continue

                current = float(hist_1m['Close'].iloc[-1])
                prev = float(hist_1m['Close'].iloc[-2]) if len(hist_1m) > 1 else current
                day_change_pct = round((current - prev) / prev * 100, 2) if prev else 0

                invested = h.lump_sum or 0
                total_invested += invested

                # Categorize holding
                quote_type = info.get("quoteType", "").upper()
                sector = info.get("sector", "")
                name_lower = (h.name or "").lower()
                if any(k in name_lower for k in ["bond", "treasury", "fixed income", "aggregate"]):
                    cat = "Bonds"
                elif any(k in name_lower for k in ["gold", "silver", "oil", "commodity", "platinum", "agriculture"]):
                    cat = "Commodities"
                elif any(k in name_lower for k in ["real estate", "reit", "property"]):
                    cat = "Real Estate"
                elif quote_type == "ETF":
                    cat = "ETF"
                else:
                    cat = "Stock"

                allocation_map[cat] = allocation_map.get(cat, 0) + invested

                # Get long-term metrics for scatter plot
                volatility = None
                ret_1y = None
                try:
                    hist_1y = t.history(period="1y")
                    if not hist_1y.empty:
                        daily_ret = hist_1y['Close'].pct_change().dropna()
                        volatility = round(float(daily_ret.std() * np.sqrt(252) * 100), 2)
                        s = float(hist_1y['Close'].iloc[0])
                        e = float(hist_1y['Close'].iloc[-1])
                        if s > 0:
                            ret_1y = round((e - s) / s * 100, 2)
                except:
                    pass

                currency = info.get("currency", h.currency or "USD")
                performers.append({
                    "ticker": h.ticker,
                    "name": h.name,
                    "price": round(current, 2),
                    "currency": currency,
                    "day_change": day_change_pct,
                    "invested": invested,
                    "volatility": volatility,
                    "return_1y": ret_1y
                })
            except Exception as e:
                print(f"[Dashboard] Error for {h.ticker}: {e}")

        # Sort for top/worst
        performers.sort(key=lambda x: x["day_change"], reverse=True)
        top_3 = performers[:3]
        worst_3 = list(reversed(performers[-3:])) if len(performers) >= 3 else list(reversed(performers))

        # Daily P&L (weighted by investment)
        daily_pnl = 0
        for p in performers:
            weight = p["invested"] / total_invested if total_invested > 0 else 0
            daily_pnl += p["day_change"] * weight
        daily_pnl = round(daily_pnl, 2)
        daily_pnl_abs = round(total_invested * daily_pnl / 100, 2) if total_invested > 0 else 0

        # Build allocation list
        allocation = []
        for cat, val in allocation_map.items():
            pct = round(val / total_invested * 100, 1) if total_invested > 0 else 0
            allocation.append({"category": cat, "value": val, "percent": pct})
        allocation.sort(key=lambda x: x["percent"], reverse=True)

        # Weighted expense ratio
        weighted_expense = 0
        valid_expense_weight = 0
        for p in performers:
            # We need to fetch expense ratio if not already in performers (it's not saved in DB)
            # For efficiency, we can just use the ones we found or assume 0 for stocks
            try:
                t = yf_mod.Ticker(p["ticker"])
                exp = t.info.get("annualReportExpenseRatio", 0) or 0
                weight = p["invested"] / total_invested if total_invested > 0 else 0
                weighted_expense += exp * weight
            except:
                pass

        # Get Health Score
        health = self.get_portfolio_health()

        return {
            "total_value": round(total_invested, 2),
            "daily_pnl": daily_pnl_abs,
            "daily_pnl_pct": daily_pnl,
            "holdings_count": len(performers),
            "top_performers": top_3,
            "worst_performers": worst_3,
            "allocation": allocation,
            "market_pulse": self._get_market_pulse(),
            "health_score": health["overall_score"],
            "health_metrics": health,
            "weighted_expense_ratio": round(weighted_expense * 100, 3)
        }

    def get_portfolio_health(self) -> dict:
        """
        Computes a comprehensive Portfolio Health Score (0-100).
        Based on Diversification, Sharpe Ratio (Risk-Adj Returns), and Drawdown.
        """
        risk = self.get_risk_analysis()
        
        # 1. Diversification (30%)
        div_score = risk.get("diversification_score", 0)
        
        # 2. Sharpe Ratio (30%) - Normalized (0.0=0, 2.0=100)
        sharpe = risk.get("sharpe_ratio", 0) or 0
        sharpe_score = max(0, min(100, (sharpe / 2.0) * 100))
        
        # 3. Drawdown (20%) - Normalized (0%=100, 30%=0)
        drawdown = abs(risk.get("max_drawdown", 0) or 0)
        drawdown_score = max(0, min(100, 100 - (drawdown / 30.0) * 100))
        
        # 4. Volatility (20%) - Normalized (5%=100, 25%=0)
        vol = risk.get("volatility", 0) or 15
        vol_score = max(0, min(100, 100 - ((vol - 5) / 20.0) * 100))
        
        overall = round((div_score * 0.3) + (sharpe_score * 0.3) + (drawdown_score * 0.2) + (vol_score * 0.2), 0)
        
        return {
            "overall_score": overall,
            "diversification": div_score,
            "risk_adjusted": round(sharpe_score, 0),
            "protection": round(drawdown_score, 0),
            "stability": round(vol_score, 0),
            "status": "Excellent" if overall >= 80 else "Good" if overall >= 60 else "Fair" if overall >= 40 else "Poor"
        }

    def _get_market_pulse(self) -> list:
        """Fetch quick-glance data for major indices."""
        import yfinance as yf_mod

        PULSE_TICKERS = [
            {"ticker": "^GSPC", "name": "S&P 500"},
            {"ticker": "^IXIC", "name": "NASDAQ"},
            {"ticker": "^VIX", "name": "VIX"},
            {"ticker": "^DJI", "name": "Dow Jones"},
        ]
        result = []
        for item in PULSE_TICKERS:
            try:
                t = yf_mod.Ticker(item["ticker"])
                hist = t.history(period="5d")
                if hist.empty:
                    continue
                current = float(hist['Close'].iloc[-1])
                prev = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current
                change = round((current - prev) / prev * 100, 2) if prev else 0
                result.append({
                    "name": item["name"],
                    "value": round(current, 2),
                    "change": change,
                })
            except Exception:
                pass
        return result

    def get_risk_analysis(self) -> dict:
        """
        Computes portfolio-level risk metrics from holdings:
        Beta vs S&P 500, Sharpe Ratio, Max Drawdown, Volatility,
        sector exposure, and a correlation mini-matrix.
        """
        import yfinance as yf_mod
        import numpy as np
        import pandas as pd
        from data.database import SessionLocal, PortfolioHolding

        session = SessionLocal()
        try:
            holdings = session.query(PortfolioHolding).all()
            if not holdings:
                return {
                    "beta": None, "sharpe_ratio": None, "max_drawdown": None,
                    "volatility": None, "sector_exposure": [], "correlation_matrix": {"labels": [], "matrix": []},
                    "holdings_count": 0,
                }
        finally:
            session.close()

        # Fetch 1Y daily returns for each holding + S&P 500
        returns_dict = {}
        weights = {}
        sectors = {}
        total_invested = 0

        for h in holdings:
            total_invested += (h.lump_sum or 0)

        for h in holdings:
            try:
                t = yf_mod.Ticker(h.ticker)
                info = t.info or {}
                hist = t.history(period="1y")
                if hist is not None and len(hist) > 20:
                    returns_dict[h.ticker] = hist['Close'].pct_change().dropna()
                    w = (h.lump_sum or 0) / total_invested if total_invested > 0 else 1.0 / len(holdings)
                    weights[h.ticker] = w
                    sectors[h.ticker] = info.get("sector", info.get("category", "Other")) or "Other"
            except Exception as e:
                print(f"[Risk] Error for {h.ticker}: {e}")

        if not returns_dict:
            return {
                "beta": None, "sharpe_ratio": None, "max_drawdown": None,
                "volatility": None, "sector_exposure": [], "correlation_matrix": {"labels": [], "matrix": []},
                "holdings_count": len(holdings),
            }

        # Fetch S&P 500 returns
        try:
            sp500 = yf_mod.Ticker("^GSPC")
            sp_hist = sp500.history(period="1y")
            sp_returns = sp_hist['Close'].pct_change().dropna() if sp_hist is not None and len(sp_hist) > 20 else None
        except Exception:
            sp_returns = None

        # Build aligned DataFrame
        df = pd.DataFrame(returns_dict)
        if df.empty:
            return {
                "beta": None, "sharpe_ratio": None, "max_drawdown": None,
                "volatility": None, "sector_exposure": [], "correlation_matrix": {"labels": [], "matrix": []},
                "holdings_count": len(holdings),
            }

        # Weighted portfolio return series
        # Fill NaNs with 0 for portfolio calculation so we can sum them, 
        # but only for days where at least one asset has data.
        weight_arr = np.array([weights.get(c, 0) for c in df.columns])
        weight_arr = weight_arr / weight_arr.sum()  # normalize
        
        portfolio_returns = (df.fillna(0).values * weight_arr).sum(axis=1)
        portfolio_series = pd.Series(portfolio_returns, index=df.index)

        # Annualized Volatility
        volatility = round(float(portfolio_series.std() * np.sqrt(252) * 100), 2)

        # Annualized Return
        annual_return = float(portfolio_series.mean() * 252)

        # Sharpe Ratio (risk-free rate ~4.3%)
        risk_free = 0.043
        sharpe = round((annual_return - risk_free) / (volatility / 100), 2) if volatility > 0 else None

        # Max Drawdown
        cumulative = (1 + portfolio_series).cumprod()
        peak = cumulative.cummax()
        drawdown = (cumulative - peak) / peak
        max_drawdown = round(float(drawdown.min() * 100), 2)

        # Portfolio Beta vs S&P 500
        beta = None
        if sp_returns is not None:
            # Align dates
            common_idx = portfolio_series.index.intersection(sp_returns.index)
            if len(common_idx) > 20:
                p_aligned = portfolio_series.loc[common_idx].values
                s_aligned = sp_returns.loc[common_idx].values
                cov = np.cov(p_aligned, s_aligned)[0][1]
                var_sp = np.var(s_aligned)
                if var_sp > 0:
                    beta = round(float(cov / var_sp), 2)

        # Sector Exposure
        sector_map = {}
        for h in holdings:
            sec = sectors.get(h.ticker, "Other")
            invested = h.lump_sum or 0
            sector_map[sec] = sector_map.get(sec, 0) + invested
        sector_exposure = []
        for sec, val in sector_map.items():
            pct = round(val / total_invested * 100, 1) if total_invested > 0 else 0
            sector_exposure.append({"sector": sec, "value": val, "percent": pct})
        sector_exposure.sort(key=lambda x: x["percent"], reverse=True)

        # Correlation mini-matrix (max 8 holdings)
        top_tickers = list(df.columns[:8])
        # Pairwise correlation avoids the "empty matrix" bug
        corr_df = df[top_tickers].corr(min_periods=5)
        
        # Replace remaining NaNs in matrix with 0 for safety
        corr_matrix_data = [[round(v, 3) if pd.notna(v) else 0 for v in row] for row in corr_df.values.tolist()]
        
        corr_matrix = {
            "labels": [t for t in top_tickers],
            "matrix": corr_matrix_data,
        }

        # Risk rating helpers
        def risk_label(val, thresholds, labels):
            for t, l in zip(thresholds, labels):
                if val <= t:
                    return l
            return labels[-1]

        beta_label = risk_label(abs(beta or 1), [0.8, 1.2, 1.5], ["Conservative", "Moderate", "Aggressive", "Very Aggressive"])
        sharpe_label = risk_label(-(sharpe or 0), [-2, -1, -0.5, 0], ["Excellent", "Good", "Fair", "Poor", "Negative"])
        drawdown_label = risk_label(abs(max_drawdown or 0), [10, 20, 35], ["Low", "Moderate", "High", "Severe"])

        # --- 1. Rolling Correlation (Portfolio average) ---
        rolling_corr_series = []
        if len(df.columns) >= 2:
            # Compute rolling correlation for all pairs and average them
            pairs_corr = []
            cols = df.columns
            for i in range(len(cols)):
                for j in range(i + 1, len(cols)):
                    c = df[cols[i]].rolling(window=30).corr(df[cols[j]])
                    pairs_corr.append(c)
            
            if pairs_corr:
                avg_rolling = pd.concat(pairs_corr, axis=1).mean(axis=1).dropna()
                # Sample for frontend
                for dt, val in avg_rolling.iloc[::5].items():
                    rolling_corr_series.append({"date": dt.strftime("%Y-%m-%d"), "value": round(float(val), 3)})

        # --- 2. Diversification Score ---
        # 100% score = 0 correlation. 0% score = 1.0 correlation.
        if len(corr_df) > 1:
            indices = np.triu_indices(len(corr_df), k=1)
            avg_corr = corr_df.values[indices].mean()
        else:
            avg_corr = 0
        corr_score = max(0, min(100, (1 - max(0, avg_corr)) * 100))
        
        # Sector bonus: more sectors = higher score
        unique_sectors = len(set(sectors.values()))
        sector_bonus = min(20, (unique_sectors / 5) * 20)
        
        div_score = round(min(100, (corr_score * 0.8) + sector_bonus), 0)

        return {
            "beta": beta,
            "beta_label": beta_label,
            "sharpe_ratio": sharpe,
            "sharpe_label": sharpe_label,
            "max_drawdown": max_drawdown,
            "drawdown_label": drawdown_label,
            "volatility": volatility,
            "annual_return": round(annual_return * 100, 2),
            "sector_exposure": sector_exposure,
            "correlation_matrix": corr_matrix,
            "rolling_correlation": rolling_corr_series,
            "diversification_score": div_score,
            "holdings_count": len(holdings),
        }

    def get_portfolio_data(self) -> list:
        """Fetches live data for all portfolio holdings from the database."""
        import yfinance as yf_mod

        session = SessionLocal()
        try:
            holdings = session.query(PortfolioHolding).all()
            if not holdings:
                return []
        finally:
            session.close()

        results = []
        for h in holdings:
            try:
                t = yf_mod.Ticker(h.ticker)
                info = t.info or {}
                hist_1m = t.history(period="1mo")
                hist_5y = t.history(period="5y")

                if hist_1m.empty:
                    continue

                current = round(float(hist_1m['Close'].iloc[-1]), 2)
                prev = float(hist_1m['Close'].iloc[-2]) if len(hist_1m) > 1 else current
                day_change = round((current - prev) / prev * 100, 2) if prev else 0

                # 5Y CAGR
                cagr_5y = None
                if hist_5y is not None and len(hist_5y) > 50:
                    s = float(hist_5y['Close'].iloc[0])
                    e = float(hist_5y['Close'].iloc[-1])
                    if s > 0:
                        cagr_5y = round(((e / s) ** (1 / 5) - 1) * 100, 2)

                # 1Y return
                hist_1y = t.history(period="1y")
                return_1y = None
                if hist_1y is not None and len(hist_1y) > 10:
                    s = float(hist_1y['Close'].iloc[0])
                    e = float(hist_1y['Close'].iloc[-1])
                    if s > 0:
                        return_1y = round((e - s) / s * 100, 2)

                high_52w = info.get("fiftyTwoWeekHigh")
                low_52w = info.get("fiftyTwoWeekLow")
                sparkline = hist_1m['Close'].tail(20).tolist()
                currency = info.get("currency", h.currency or "USD")

                results.append({
                    "ticker": h.ticker,
                    "name": h.name,
                    "price": current,
                    "currency": currency,
                    "day_change": day_change,
                    "return_1y": return_1y,
                    "cagr_5y": cagr_5y,
                    "high_52w": round(high_52w, 2) if high_52w else None,
                    "low_52w": round(low_52w, 2) if low_52w else None,
                    "sparkline": [round(s, 2) for s in sparkline],
                    "lump_sum": h.lump_sum or 0,
                    "monthly_sip": h.monthly_sip or 0,
                    "added_date": h.added_date.isoformat() if h.added_date else None,
                })

            except Exception as e:
                print(f"[Portfolio] Error for {h.ticker}: {e}")

        return results

    def get_ticker_detail(self, ticker: str) -> dict:
        """
        Fetches detail data for the expanded portfolio view.
        Returns 1M, 1Y returns, 5Y CAGR, Beta, Expense Ratio, Div Yield, and 5Y chart data.
        """
        import yfinance as yf
        try:
            t = yf.Ticker(ticker)
            info = t.info
            
            # Fetch histories
            hist_5y = t.history(period="5y")
            hist_1y = t.history(period="1y")
            hist_1m = t.history(period="1mo")
            
            # Calculate returns
            ret_1m = None
            if not hist_1m.empty and float(hist_1m['Close'].iloc[0]) > 0:
                s = float(hist_1m['Close'].iloc[0])
                e = float(hist_1m['Close'].iloc[-1])
                ret_1m = round((e - s) / s * 100, 2)
                
            ret_1y = None
            if not hist_1y.empty and float(hist_1y['Close'].iloc[0]) > 0:
                s = float(hist_1y['Close'].iloc[0])
                e = float(hist_1y['Close'].iloc[-1])
                ret_1y = round((e - s) / s * 100, 2)
                
            cagr_5y = None
            if not hist_5y.empty and float(hist_5y['Close'].iloc[0]) > 0:
                s = float(hist_5y['Close'].iloc[0])
                e = float(hist_5y['Close'].iloc[-1])
                # Approx 252 trading days/year
                years = len(hist_5y) / 252.0
                if years > 0:
                    cagr = ((e / s) ** (1 / years)) - 1
                    cagr_5y = round(cagr * 100, 2)
            
            chart_data = []
            if not hist_5y.empty:
                # Downsample to ~1 data point per week to save payload size
                resampled = hist_5y.resample('W').last().dropna()
                for idx, row in resampled.iterrows():
                    chart_data.append({
                        "date": idx.strftime("%Y-%m-%d"),
                        "price": round(float(row['Close']), 2)
                    })
            
            return {
                "return_1m": ret_1m,
                "return_1y": ret_1y,
                "cagr_5y": cagr_5y,
                "beta": info.get("beta"),
                "expense_ratio": info.get("expense_ratio", info.get("fund_expense_ratio")),
                "dividend_yield": info.get("dividendYield", info.get("yield")),
                "chart": chart_data
            }
        except Exception as e:
            print(f"[get_ticker_detail] Error for {ticker}: {e}")
            return None

    def get_legendary_portfolios(self) -> dict:
        """Returns deep-researched portfolio allocations of legendary investors with dynamic performance metrics."""
        cache_key = "legendary_portfolios"
        cached = self._get_cached_data(cache_key)
        if cached:
            print("[DataManager] Loaded Legendary Portfolios from DB Cache.")
            return cached

        import time
        import yfinance as yf
                
        base_allocations = {
            "USA": [
                {
                    "name": "Warren Buffett (Berkshire Focused)",
                    "description": "Inspired by the Oracle of Omaha's iconic high-conviction holdings. Focuses on consumer brand moats and technology leaders.",
                    "allocation": [
                        {"asset": "Consumer Staples (The Moat)", "ticker": "KO", "weight": 25},
                        {"asset": "Technology Pioneer", "ticker": "AAPL", "weight": 40},
                        {"asset": "Financial Services", "ticker": "BAC", "weight": 20},
                        {"asset": "Energy / Commodities", "ticker": "OXY", "weight": 10},
                        {"asset": "Cash Equivalents", "ticker": "BIL", "weight": 5}
                    ]
                },
                {
                    "name": "Ray Dalio (All Weather)",
                    "description": "Designed to survive any economic environment (inflation, deflation, growth, recession) by balancing risk across asset classes.",
                    "allocation": [
                        {"asset": "US Total Stock Market", "ticker": "VTI", "weight": 30},
                        {"asset": "Long-Term Treasuries", "ticker": "TLT", "weight": 40},
                        {"asset": "Intermediate Treasuries", "ticker": "IEI", "weight": 15},
                        {"asset": "Gold", "ticker": "GLD", "weight": 7.5},
                        {"asset": "Broad Commodities", "ticker": "GSG", "weight": 7.5}
                    ]
                },
                {
                    "name": "David Swensen (Yale Model)",
                    "description": "The 'Lazy Portfolio' version of the Yale Endowment approach, heavily diversified across asset classes including real estate.",
                    "allocation": [
                        {"asset": "US Total Stock Market", "ticker": "VTI", "weight": 30},
                        {"asset": "Real Estate (REITs)", "ticker": "VNQ", "weight": 20},
                        {"asset": "Intl Developed Stocks", "ticker": "VEU", "weight": 15},
                        {"asset": "Emerging Markets", "ticker": "VWO", "weight": 5},
                        {"asset": "Intermediate Treasuries", "ticker": "VGIT", "weight": 15},
                        {"asset": "TIPS (Inflation Protected)", "ticker": "VTIP", "weight": 15}
                    ]
                },
                {
                    "name": "John Bogle (Three-Fund)",
                    "description": "The classic Bogleheads strategy prioritizing maximal diversification and minimal management fees.",
                    "allocation": [
                        {"asset": "US Total Stock Market", "ticker": "VTI", "weight": 60},
                        {"asset": "Intl Total Stock Market", "ticker": "VXUS", "weight": 20},
                        {"asset": "Total US Bond Market", "ticker": "BND", "weight": 20}
                    ]
                }
            ],
            "Europe": [
                {
                    "name": "Terry Smith (Fundsmith Style)",
                    "description": "The 'English Warren Buffett'. Focuses on a concentrated portfolio of high-quality, resilient global businesses.",
                    "allocation": [
                        {"asset": "Global Quality Consumer Staples", "ticker": "KXI", "weight": 35},
                        {"asset": "Global Healthcare Equipment", "ticker": "IXJ", "weight": 30},
                        {"asset": "Global Tech (High ROCE)", "ticker": "IXN", "weight": 25},
                        {"asset": "Cash / Equivalents", "ticker": "BIL", "weight": 10}
                    ]
                },
                {
                    "name": "Permanent Portfolio (EU Variant)",
                    "description": "Harry Browne's strategy adjusted for the Eurozone, balancing growth and hedging against macro shocks.",
                    "allocation": [
                        {"asset": "European Equities", "ticker": "VGK", "weight": 25},
                        {"asset": "Long-Term Euro Bonds", "ticker": "IBZL.L", "weight": 25},
                        {"asset": "Cash (Euro Short-Term)", "ticker": "XEON.DE", "weight": 25},
                        {"asset": "Physical Gold", "ticker": "SGLN.L", "weight": 25}
                    ]
                }
            ],
            "India": [
                {
                    "name": "Coffee Can Portfolio (Saurabh Mukherjea)",
                    "description": "A 'buy and forget' approach targeting businesses with 10+ years of >15% revenue growth and >15% ROCE.",
                    "allocation": [
                        {"asset": "High-Quality Consumption", "ticker": "ASIANPAINT.NS", "weight": 30},
                        {"asset": "Private Financials", "ticker": "HDFCBANK.NS", "weight": 25},
                        {"asset": "Resilient Tech Services", "ticker": "TCS.NS", "weight": 20},
                        {"asset": "Oligopoly Niche Players", "ticker": "PIDILITIND.NS", "weight": 25}
                    ]
                },
                {
                    "name": "Rakesh Jhunjhunwala (Big Bull Style)",
                    "description": "Long-term concentrated bets on India's structural growth story, strong management, and turnaround candidates.",
                    "allocation": [
                        {"asset": "Consumer & Retail (Titan)", "ticker": "TITAN.NS", "weight": 40},
                        {"asset": "Pharma & Healthcare", "ticker": "LUPIN.NS", "weight": 20},
                        {"asset": "Financial Services", "ticker": "CRISIL.NS", "weight": 20},
                        {"asset": "Auto & Infra", "ticker": "TATAMOTORS.NS", "weight": 20}
                    ]
                },
                {
                    "name": "Nifty 50 Equal Weight",
                    "description": "A balanced indexing approach to capturing India's top 50 companies without over-concentration in top-heavy stocks.",
                    "allocation": [
                        {"asset": "Nifty 50 Equal Weight ETF", "ticker": "NIFTY50EQUAL.NS", "weight": 100}
                    ]
                }
            ]
        }
        
        try:
            # 1. Gather all unique tickers
            tickers = set()
            for region, ports in base_allocations.items():
                for p in ports:
                    for a in p['allocation']:
                        tickers.add(a['ticker'])
            tickers_list = list(tickers)
            
            # 2. Fetch bulk historical data
            hist_data = yf.download(tickers_list, period="5y", interval="1mo")['Adj Close']
            
            # 3. Fast fetch for dividend yields
            import concurrent.futures
            yields = {}
            def fetch_yield(t):
                try:
                    return t, (yf.Ticker(t).info.get("dividendYield", 0) or 0) * 100
                except:
                    return t, 0
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                results = list(executor.map(fetch_yield, tickers_list))
                for t, y in results:
                    yields[t] = y
                    
            # 4. Calculate metrics per portfolio
            for region, ports in base_allocations.items():
                for p in ports:
                    metrics = {"cagr_5y": None, "yield": 0, "chart": [], "sip_return": None}
                    weights = {a['ticker']: a['weight'] / 100 for a in p['allocation']}
                    
                    # Yield
                    metrics['yield'] = round(sum(weights[t] * yields.get(t, 0) for t in weights), 2)
                    
                    # History
                    valid_cols = [c for c in weights.keys() if c in hist_data.columns]
                    if valid_cols:
                        df = hist_data[valid_cols].ffill().bfill()
                        # Normalize to 1 at start
                        try:
                            norm_df = df / df.iloc[0]
                            port_series = sum(norm_df[t] * weights[t] for t in valid_cols if df[t].iloc[0] > 0)
                            
                            # CAGR
                            years = len(port_series) / 12  # approx 12 mo/yr
                            if years > 0 and port_series.iloc[-1] > 0:
                                cagr = ((port_series.iloc[-1] / port_series.iloc[0]) ** (1 / years) - 1) * 100
                                metrics['cagr_5y'] = round(cagr, 2)
                                
                            # Chart Data & SIP Calculation
                            # Assume $1000/mo SIP
                            sip_capital = 0
                            sip_value = 0
                            
                            for date, val in port_series.items():
                                series_val = float(val)
                                metrics['chart'].append({
                                    "date": date.strftime("%Y-%m-%d"),
                                    "value": round(series_val * 10000, 2) # Simulate $10k initial investment
                                })
                                # SIP logic
                                sip_capital += 1000
                                sip_value += 1000 # Add monthly
                                # Grow by monthly return
                                # Actually, easier: track units bought
                            
                            # Proper SIP calculation using price levels instead of simple growth
                            total_units = 0
                            for date, val in port_series.items():
                                price = float(val)
                                if price > 0:
                                    total_units += (1000 / price)
                                    
                            final_sip_value = total_units * float(port_series.iloc[-1])
                            total_invested = len(port_series) * 1000
                            
                            if total_invested > 0:
                                sip_ret = ((final_sip_value - total_invested) / total_invested) * 100
                                metrics['sip_return'] = round(sip_ret, 2)
                                
                        except Exception as e:
                            print(f"Error calculating portfolio {p['name']}: {e}")
                            
                    p['metrics'] = metrics
                    
            if base_allocations:
                self._set_cached_data(cache_key, base_allocations, expiry_hours=12)
            return base_allocations
            
        except Exception as e:
            print(f"[Legendary Portfolios] Data Fetch Error: {e}")
            # Fallback to static if failure
            return base_allocations

