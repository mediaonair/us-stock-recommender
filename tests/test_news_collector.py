from unittest.mock import MagicMock, patch

from src.news_collector import collect_news


def _make_ticker_mock(news_items: list[dict]) -> MagicMock:
    ticker_mock = MagicMock()
    ticker_mock.news = news_items
    return ticker_mock


@patch("src.news_collector.yf.Ticker")
def test_collect_news_normalizes_legacy_schema(mock_ticker_cls):
    mock_ticker_cls.return_value = _make_ticker_mock(
        [
            {
                "title": "Legacy headline",
                "link": "https://example.com/legacy",
                "publisher": "Example Wire",
                "providerPublishTime": 1700000000,
            }
        ]
    )

    items = collect_news(["AAA"])

    assert len(items) == 1
    assert items[0].title == "Legacy headline"
    assert items[0].ticker == "AAA"


@patch("src.news_collector.yf.Ticker")
def test_collect_news_normalizes_new_schema_with_content_wrapper(mock_ticker_cls):
    mock_ticker_cls.return_value = _make_ticker_mock(
        [
            {
                "content": {
                    "title": "New schema headline",
                    "canonicalUrl": {"url": "https://example.com/new"},
                    "provider": {"displayName": "Example Provider"},
                    "pubDate": "2024-01-01T00:00:00Z",
                }
            }
        ]
    )

    items = collect_news(["AAA"])

    assert len(items) == 1
    assert items[0].link == "https://example.com/new"
    assert items[0].publisher == "Example Provider"


@patch("src.news_collector.yf.Ticker")
def test_collect_news_deduplicates_by_link(mock_ticker_cls):
    duplicate_item = {
        "title": "Same story",
        "link": "https://example.com/dup",
        "publisher": "Wire",
        "providerPublishTime": 1700000000,
    }
    mock_ticker_cls.return_value = _make_ticker_mock([duplicate_item, duplicate_item])

    items = collect_news(["AAA"])

    assert len(items) == 1


@patch("src.news_collector.yf.Ticker")
def test_collect_news_skips_items_without_link_or_title(mock_ticker_cls):
    mock_ticker_cls.return_value = _make_ticker_mock(
        [{"title": "", "link": "https://example.com/missing-title"}]
    )

    items = collect_news(["AAA"])

    assert items == []
