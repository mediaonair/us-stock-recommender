from unittest.mock import patch

from fastapi.testclient import TestClient

from src.stock_recommender import StockRecommendation


def _fake_workflow_result():
    return {
        "recommendations": [
            StockRecommendation(
                ticker="AAA",
                score=0.5,
                news_count=2,
                average_sentiment=0.5,
                key_issues=["ai"],
                top_headlines=["headline"],
            )
        ]
    }


def test_api_endpoints():
    with patch("src.api.run_workflow", return_value=_fake_workflow_result()):
        from src.api import app

        with TestClient(app) as client:
            health_response = client.get("/health")
            recommendations_response = client.get("/recommendations")
            dashboard_response = client.get("/")

    assert health_response.status_code == 200
    assert health_response.json() == {"status": "ok"}

    assert recommendations_response.status_code == 200
    rec_body = recommendations_response.json()
    assert rec_body["recommendations"][0]["ticker"] == "AAA"
    assert rec_body["last_error"] is None

    assert dashboard_response.status_code == 200
    assert "text/html" in dashboard_response.headers["content-type"]
    assert "US Stock Recommender" in dashboard_response.text
