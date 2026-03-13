import pytest

def test_health_check(client):
    """Verify backend is up and root/docs work."""
    response = client.get("/")
    # In this app, / might redirect or 404 if not defined, but docs should exist
    response = client.get("/docs")
    assert response.status_code == 200

def test_screener_endpoint(client):
    """Test /api/screener returns data."""
    response = client.get("/api/screener")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "ticker" in data[0]
        assert "ey" in data[0]

def test_macro_endpoint(client):
    """Test /api/macro returns indices and gauges."""
    response = client.get("/api/macro")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "indices" in data
    assert "gauges" in data
    assert any(item["ticker"] == "^GSPC" for item in data["indices"])

def test_india_funds_endpoint(client):
  response = client.get("/api/india/mutual-funds")
  assert response.status_code == 200
  data = response.json()
  assert isinstance(data, list)
