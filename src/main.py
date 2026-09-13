"""
us-stock-recommender 에이전트 진입점.

현재는 1단계(뉴스 수집) 데모 단계로, 분석/추천 로직은
docs/ROADMAP.md의 단계에 따라 이후 feature 브랜치에서 구현됩니다.
"""

import os

from dotenv import load_dotenv

from src.news_collector import collect_news

load_dotenv()


def main() -> None:
    embedding_model = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")
    print("us-stock-recommender agent starting...")
    print(f"embedding model: {embedding_model}")

    news_items = collect_news()
    print(f"수집된 뉴스: {len(news_items)}건")
    for item in news_items[:5]:
        print(f"- [{item.ticker}] {item.title} ({item.publisher})")

    # TODO: 뉴스 분석 -> 종목 추천으로 이어지는 LangGraph 워크플로우 연결
    # (docs/ROADMAP.md 2~4단계 참고)


if __name__ == "__main__":
    main()
