from abc import ABC, abstractmethod
from typing import Optional
from data.models import FinancialMetrics
from datetime import date

class BaseFinancialProvider(ABC):
    """
    Abstract Base Class that all financial API providers must implement.
    This guarantees that the Magic Formula engine always receives standardized data.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    @abstractmethod
    def fetch_metrics(self, ticker_symbol: str) -> Optional[FinancialMetrics]:
        """
        Fetch data from the REST API and return it as a validated Pydantic model.
        Returns None if data cannot be fetched or is wholly incomplete.
        """
        pass
        
    @abstractmethod
    def fetch_history(self, ticker_symbol: str, period: str) -> Optional[list[dict]]:
        """
        Fetch historical price data for the specified period ("1mo", "1y", "5y", "max").
        Should return a list of dictionaries with "date" and "close" keys.
        """
        pass
        
    def get_provider_name(self) -> str:
         return self.__class__.__name__
