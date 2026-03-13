import pytest
import os
import sys
from fastapi.testclient import TestClient

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api import app
from data.database import SessionLocal, Base, engine

@pytest.fixture(scope="session")
def db():
    # Setup test database (optional: use a separate test.db)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c
