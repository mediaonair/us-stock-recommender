"""
분석된 뉴스(NewsAnalysis)를 바탕으로 종목별 추천 점수를 계산하는 모듈.

1차 버전은 단순한 규칙 기반 스코어링을 사용합니다.

- 감성(sentiment)을 점수화(positive=+1, neutral=0, negative=-1)해 종목별 평균을 냅니다.
- 같은 종목에 대한 뉴스가 많을수록(언급량) 신뢰도가 높다고 보고 가중치를 더하되,
  로그 스케일을 사용해 과도하게 커지지 않도록 합니다.

추후 LangGraph 워크플로우 통합, 최근성 가중치, 더 정교한 산식으로 대체/보완될 수 있습니다.
(docs/ROADMAP.md 4단계 참고)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from src.news_analyzer import NewsAnalysis

_SENTIMENT_SCORE = {"positive": 1.0, "neutral": 0.0, "negative": -1.0}


@dataclass
class StockRecommendation:
    ticker: str
    score: float
    news_count: int
    average_sentiment: float
    key_issues: list[str] = field(default_factory=list)
    top_headlines: list[str] = field(default_factory=list)


def _sentiment_to_score(sentiment: str) -> float:
    return _SENTIMENT_SCORE.get(sentiment, 0.0)


def recommend_stocks(
    analyses: list[NewsAnalysis], top_n: int | None = None
) -> list[StockRecommendation]:
    """종목별로 뉴스 분석 결과를 집계해 추천 점수 순으로 정렬해 반환합니다."""
    grouped: dict[str, list[NewsAnalysis]] = {}
    for analysis in analyses:
        grouped.setdefault(analysis.ticker, []).append(analysis)

    recommendations: list[StockRecommendation] = []
    for ticker, items in grouped.items():
        sentiment_scores = [_sentiment_to_score(item.sentiment) for item in items]
        average_sentiment = sum(sentiment_scores) / len(sentiment_scores)

        # 언급량이 많을수록 가중치를 조금 더 주되(신뢰도 반영), 로그 스케일로 과도한 쏠림을 방지
        volume_weight = math.log2(len(items) + 1)
        score = average_sentiment * volume_weight

        key_issues = sorted({issue for item in items for issue in item.key_issues})
        top_headlines = [item.title for item in items[:3]]

        recommendations.append(
            StockRecommendation(
                ticker=ticker,
                score=round(score, 4),
                news_count=len(items),
                average_sentiment=round(average_sentiment, 4),
                key_issues=key_issues,
                top_headlines=top_headlines,
            )
        )

    recommendations.sort(key=lambda rec: rec.score, reverse=True)
    return recommendations[:top_n] if top_n else recommendations
