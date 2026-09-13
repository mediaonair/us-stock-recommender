import math

from src.news_analyzer import NewsAnalysis
from src.stock_recommender import recommend_stocks


def _analysis(ticker: str, sentiment: str, issues: list[str] | None = None) -> NewsAnalysis:
    return NewsAnalysis(
        ticker=ticker,
        title=f"{ticker} sample headline",
        link=f"https://example.com/{ticker}",
        summary="summary",
        sentiment=sentiment,
        key_issues=issues or [],
        embedding=[],
    )


def test_recommend_stocks_orders_by_score_desc():
    analyses = [
        _analysis("AAA", "positive"),
        _analysis("AAA", "positive"),
        _analysis("BBB", "negative"),
        _analysis("CCC", "neutral"),
    ]

    recommendations = recommend_stocks(analyses)
    tickers = [rec.ticker for rec in recommendations]

    assert tickers[0] == "AAA"
    assert tickers[-1] == "BBB"


def test_recommend_stocks_score_matches_expected_formula():
    analyses = [_analysis("AAA", "positive"), _analysis("AAA", "positive")]

    [rec] = recommend_stocks(analyses)

    expected_score = 1.0 * math.log2(2 + 1)
    assert rec.news_count == 2
    assert rec.average_sentiment == 1.0
    assert rec.score == round(expected_score, 4)


def test_recommend_stocks_collects_unique_sorted_key_issues():
    analyses = [
        _analysis("AAA", "positive", issues=["ai", "chip"]),
        _analysis("AAA", "neutral", issues=["chip", "supply"]),
    ]

    [rec] = recommend_stocks(analyses)

    assert rec.key_issues == ["ai", "chip", "supply"]


def test_recommend_stocks_respects_top_n():
    analyses = [_analysis("AAA", "positive"), _analysis("BBB", "positive")]

    recommendations = recommend_stocks(analyses, top_n=1)

    assert len(recommendations) == 1
