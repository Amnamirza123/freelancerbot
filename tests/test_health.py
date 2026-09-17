"""
Phase 1 sanity test: does the server boot and respond?

Run with: pytest
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["app"] == "FreelancerBot"
    # database will be "not_configured" until .env has real Supabase creds,
    # "connected" once it does, or "error: ..." if creds are wrong.
    assert "database" in body


def test_root():
    response = client.get("/")
    assert response.status_code == 200
