from pydantic import BaseModel
from typing import Optional
from datetime import date

class FinancialMetrics(BaseModel):
    """
    Standardized internal model for financial metrics regardless of the API source.
    """
    ticker: str
    date_recorded: date
    source_api: str
    
    # Core Magic Formula Metrics
    ebit: Optional[float] = None
    enterprise_value: Optional[float] = None
    current_assets: Optional[float] = None
    current_liabilities: Optional[float] = None
    total_assets: Optional[float] = None
    net_fixed_assets: Optional[float] = None
    
    # Calculated properties
    @property
    def net_working_capital(self) -> Optional[float]:
        if self.current_assets is not None and self.current_liabilities is not None:
            return self.current_assets - self.current_liabilities
        return None
        
    @property
    def earnings_yield(self) -> Optional[float]:
        if self.enterprise_value and self.ebit is not None:
            return self.ebit / self.enterprise_value
        return None
        
    @property
    def roc(self) -> Optional[float]:
        nwc = self.net_working_capital
        if self.ebit is not None and nwc is not None and self.net_fixed_assets is not None:
            denominator = nwc + self.net_fixed_assets
            if denominator != 0:
                return self.ebit / denominator
        return None
