"""
무료 뉴스 소스를 이용한 미국 주식 뉴스 수집 모듈.

별도 API 키 없이 사용할 수 있는 yfinance(Yahoo Finance)의 종목별 뉴스를
1단계 뉴스 소스로 사용합니다. 추후 소스를 추가/교체할 수 있도록
`collect_news` 하나의 진입점으로 정리했습니다.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import yfinance as yf

# 기본 관심 종목 (추후 설정 파일/DB로 분리 예정)
DEFAULT_TICKERS = ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN"]


@dataclass
class NewsItem:
    ticker: str
    title: str
    link: str
    publisher: str
    published_at: datetime


def _parse_published_at(content: dict) -> datetime:
    """yfinance 응답 스키마 변화에 대응해 발행 시각을 최대한 파싱합니다."""
    timestamp = content.get("providerPublishTime")
    if timestamp:
        return datetime.fromtimestamp(timestamp, tz=timezone.utc)

    pub_date = content.get("pubDate")
    if pub_date:
        try:
            return datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
        except ValueError:
            pass

    return datetime.now(tz=timezone.utc)


def _normalize(ticker: str, raw_item: dict) -> NewsItem | None:
    """yfinance 구버전/신버전 응답 스키마를 모두 지원하도록 정규화합니다."""
    content = raw_item.get("content", raw_item)

    link = (
        content.get("link")
        or (content.get("canonicalUrl") or {}).get("url")
        or (content.get("clickThroughUrl") or {}).get("url")
    )
    title = content.get("title")
    if not link or not title:
        return None

    publisher = content.get("publisher") or (content.get("provider") or {}).get(
        "displayName", ""
    )

    return NewsItem(
        ticker=ticker,
        title=title,
        link=link,
        publisher=publisher,
        published_at=_parse_published_at(content),
    )


def collect_news(tickers: list[str] | None = None) -> list[NewsItem]:
    """지정한 종목들의 최신 뉴스를 수집합니다. 링크 기준으로 중복은 제거합니다."""
    tickers = tickers or DEFAULT_TICKERS
    seen_links: set[str] = set()
    items: list[NewsItem] = []

    for ticker in tickers:
        raw_news = yf.Ticker(ticker).news or []
        for raw_item in raw_news:
            news_item = _normalize(ticker, raw_item)
            if news_item is None or news_item.link in seen_links:
                continue
            seen_links.add(news_item.link)
            items.append(news_item)

    items.sort(key=lambda item: item.published_at, reverse=True)
    return items
