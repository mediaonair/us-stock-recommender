from datetime import datetime, timezone
from unittest.mock import patch

from src.news_analyzer import NewsAnalysis
from src.news_collector import NewsItem
from src.stock_recommender import StockRecommendation
from src.workflow import run_workflow


def test_run_workflow_wires_collect_analyze_recommend_in_order():
    fake_news_item = NewsItem(
        ticker="AAA",
        title="t",
        link="l",
        publisher="p",
        published_at=datetime.now(tz=timezone.utc),
    )
    fake_analysis = NewsAnalysis(
        ticker="AAA", title="t", link="l", sentiment="positive"
    )
    fake_recommendation = StockRecommendation(
        ticker="AAA", score=1.0, news_count=1, average_sentiment=1.0
    )

    with (
        patch(
            "src.workflow.collect_news", return_value=[fake_news_item]
        ) as mock_collect,
        patch(
            "src.workflow.analyze_news", return_value=[fake_analysis]
        ) as mock_analyze,
        patch(
            "src.workflow.recommend_stocks", return_value=[fake_recommendation]
        ) as mock_recommend,
    ):
        state = run_workflow(tickers=["AAA"])

    mock_collect.assert_called_once_with(["AAA"])
    mock_analyze.assert_called_once()
    mock_recommend.assert_called_once()

    assert state["news_items"] == [fake_news_item]
    assert state["analyses"] == [fake_analysis]
    assert state["recommendations"] == [fake_recommendation]
