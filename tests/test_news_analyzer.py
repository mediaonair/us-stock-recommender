import json
from datetime import datetime, timezone
from unittest.mock import patch

from src.news_analyzer import analyze_news, analyze_news_item, embed_text
from src.news_collector import NewsItem


def _news_item(ticker: str = "AAA") -> NewsItem:
    return NewsItem(
        ticker=ticker,
        title="Sample headline",
        link="https://example.com/a",
        publisher="Wire",
        published_at=datetime.now(tz=timezone.utc),
    )


def _mock_completion_response(payload: dict) -> dict:
    return {"choices": [{"message": {"content": json.dumps(payload)}}]}


def _mock_embedding_response(vector: list[float]) -> dict:
    return {"data": [{"embedding": vector}]}


@patch("src.news_analyzer.litellm.embedding")
@patch("src.news_analyzer.litellm.completion")
def test_analyze_news_item_parses_llm_response(mock_completion, mock_embedding):
    mock_completion.return_value = _mock_completion_response(
        {"summary": "요약", "sentiment": "positive", "key_issues": ["ai"]}
    )
    mock_embedding.return_value = _mock_embedding_response([0.1, 0.2, 0.3])

    result = analyze_news_item(_news_item())

    assert result.summary == "요약"
    assert result.sentiment == "positive"
    assert result.key_issues == ["ai"]
    assert result.embedding == [0.1, 0.2, 0.3]


@patch("src.news_analyzer.litellm.embedding")
def test_embed_text_returns_vector(mock_embedding):
    mock_embedding.return_value = _mock_embedding_response([1.0, 2.0])

    vector = embed_text("hello")

    assert vector == [1.0, 2.0]


@patch("src.news_analyzer.litellm.embedding")
@patch("src.news_analyzer.litellm.completion")
def test_analyze_news_skips_failed_items_instead_of_raising(
    mock_completion, mock_embedding
):
    mock_completion.side_effect = RuntimeError("boom")

    results = analyze_news([_news_item("AAA"), _news_item("BBB")])

    assert results == []
