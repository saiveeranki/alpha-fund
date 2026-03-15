import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# Set up SQLite database in the current directory
DB_PATH = os.path.join(os.path.dirname(__file__), 'market_cache.db')
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
Base = declarative_base()

class Asset(Base):
    __tablename__ = 'assets'
    ticker = Column(String, primary_key=True)
    name = Column(String)
    sector = Column(String)
    exchange = Column(String)

class FinancialStatementCache(Base):
    __tablename__ = 'financial_statements'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String, index=True)
    date_recorded = Column(Date)
    source_api = Column(String)
    
    ebit = Column(Float)
    enterprise_value = Column(Float)
    current_assets = Column(Float, nullable=True)
    current_liabilities = Column(Float, nullable=True)
    total_assets = Column(Float, nullable=True)
    net_fixed_assets = Column(Float, nullable=True)

class TickerRegistry(Base):
    """Master list of all investable ETFs, Mutual Funds, and Indices."""
    __tablename__ = 'ticker_registry'
    ticker = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String)       # 'ETF', 'Mutual Fund', 'Index', 'Commodity'
    sector = Column(String)         # 'Technology', 'Financials', 'Broad Market', etc.
    market = Column(String)         # 'US', 'EU', 'India', 'Global'
    exchange = Column(String)       # 'NYSE', 'XETRA', 'NSE', 'LSE'

class PortfolioHolding(Base):
    """User's portfolio: each row is one holding with investment details."""
    __tablename__ = 'portfolio_holdings'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String, nullable=False, unique=True, index=True)
    name = Column(String)
    lump_sum = Column(Float, default=0)       # One-time investment amount
    monthly_sip = Column(Float, default=0)    # Monthly recurring investment
    currency = Column(String, default='USD')  # EUR, USD, GBP, INR
    added_date = Column(DateTime, default=datetime.utcnow)

class StockHistoryCache(Base):
    """Stores full historical price series for delta-merging."""
    __tablename__ = 'stock_history_cache'
    ticker = Column(String, primary_key=True)
    data = Column(String)  # JSON string of list of dicts: [{'date': '...', 'close': ...}]
    last_updated = Column(DateTime, default=datetime.utcnow)

class GenericCache(Base):
    """Generic cache for large API responses (stored as JSON)."""
    __tablename__ = 'generic_cache'
    key = Column(String, primary_key=True)
    data = Column(String)  # JSON string
    expiry = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow)

# Create all tables in the engine
Base.metadata.create_all(engine)

# Create a configured "Session" class
SessionLocal = sessionmaker(bind=engine)

def get_db_session():
    """Dependency to get the database session"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
