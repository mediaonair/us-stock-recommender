"""
LiteLLM + Gemini 계열 모델을 이용한 뉴스 분석 모듈.

수집된 뉴스(NewsItem)에 대해 투자자 관점의 요약/감성/핵심 이슈를 추출하고,
`gemini-embedding-001`로 임베딩 벡터를 생성합니다. 모델 이름은 환경 변수로
설정하며, LiteLLM을 통해 호출하므로 추후 다른 제공자 모델로도 쉽게
교체할 수 있습니다.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field

import litellm

from src.news_collector import NewsItem

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini/gemini-1.5-flash")
DEFAULT_EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "gemini/gemini-embedding-001")

_ANALYSIS_PROMPT = """\
다음은 미국 주식 관련 뉴스입니다. 투자자 관점에서 분석하고,
아래 JSON 형식으로만 답하세요 (다른 설명 없이 JSON만 출력).

{{
  "summary": "한두 문장 요약",
  "sentiment": "positive | neutral | negative",
  "key_issues": ["핵심 이슈/키워드", "..."]
}}

종목: {ticker}
제목: {title}
"""


@dataclass
class NewsAnalysis:
    ticker: str
    title: str
    link: str
    summary: str = ""
    sentiment: str = "neutral"
    key_issues: list[str] = field(default_factory=list)
    embedding: list[float] = field(default_factory=list)


def _call_llm(prompt: str, model: str) -> dict:
    response = litellm.completion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    content = response["choices"][0]["message"]["content"]
    return json.loads(content)


def embed_text(text: str, model: str | None = None) -> list[float]:
    """주어진 텍스트를 임베딩 모델(기본값: gemini-embedding-001)로 벡터화합니다."""
    model = model or DEFAULT_EMBEDDING_MODEL
    response = litellm.embedding(model=model, input=[text])
    return response["data"][0]["embedding"]


def analyze_news_item(item: NewsItem, model: str | None = None) -> NewsAnalysis:
    """뉴스 한 건을 요약/감성/핵심 이슈 분석하고 임베딩까지 생성합니다."""
    model = model or DEFAULT_MODEL
    prompt = _ANALYSIS_PROMPT.format(ticker=item.ticker, title=item.title)
    result = _call_llm(prompt, model)
    embedding = embed_text(f"[{item.ticker}] {item.title}")

    return NewsAnalysis(
        ticker=item.ticker,
        title=item.title,
        link=item.link,
        summary=result.get("summary", ""),
        sentiment=result.get("sentiment", "neutral"),
        key_issues=result.get("key_issues", []),
        embedding=embedding,
    )


def analyze_news(
    items: list[NewsItem], model: str | None = None
) -> list[NewsAnalysis]:
    """여러 뉴스를 분석합니다. 개별 항목 실패는 건너뛰고 나머지는 계속 진행합니다."""
    analyses: list[NewsAnalysis] = []
    for item in items:
        try:
            analyses.append(analyze_news_item(item, model=model))
        except Exception as exc:  # noqa: BLE001 - 개별 실패가 전체를 막지 않도록 함
            print(f"[news_analyzer] 분석 실패 ({item.ticker} - {item.title}): {exc}")
    return analyses
