from data.manager import DataManager
import json

def test_correlation():
    dm = DataManager()
    print("Testing Global Correlation Matrix...")
    global_corr = dm.get_correlation_matrix()
    print(f"Global Labels: {global_corr.get('labels')}")
    print(f"Matrix size: {len(global_corr.get('matrix', []))}")
    
    print("\nTesting Portfolio Risk Analysis (includes correlation)...")
    risk_analysis = dm.get_risk_analysis()
    portfolio_corr = risk_analysis.get('correlation_matrix', {})
    print(f"Portfolio Labels: {portfolio_corr.get('labels')}")
    print(f"Matrix size: {len(portfolio_corr.get('matrix', []))}")

if __name__ == "__main__":
    test_correlation()
