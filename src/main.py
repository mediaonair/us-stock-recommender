"""
us-stock-recommender 에이전트 진입점.

현재는 2단계(뉴스 분석) 데모 단계로, 추천 로직은
docs/ROADMAP.md의 단계에 따라 이후 feature 브랜치에서 구현됩니다.
"""

import os

from dotenv import load_dotenv

from src.news_analyzer import analyze_news
from src.news_collector import collect_news

load_dotenv()

# 데모에서 실제로 LLM 분석/임베딩까지 돌려볼 뉴스 개수 (비용 절감을 위해 제한)
ANALYZE_LIMIT = 3


def main() -> None:
    embedding_model = os.getenv("EMBEDDING_MODEL", "gemini/gemini-embedding-001")
    print("us-stock-recommender agent starting...")
    print(f"embedding model: {embedding_model}")

    news_items = collect_news()
    print(f"수집된 뉴스: {len(news_items)}건")
    for item in news_items[:5]:
        print(f"- [{item.ticker}] {item.title} ({item.publisher})")

    if not os.getenv("GEMINI_API_KEY"):
        print(
            "GEMINI_API_KEY가 설정되어 있지 않아 뉴스 분석 단계는 건너뜁니다. "
            ".env에 키를 채워넣으면 분석까지 실행됩니다."
        )
        return

    analyses = analyze_news(news_items[:ANALYZE_LIMIT])
    print(f"\n분석된 뉴스: {len(analyses)}건")
    for analysis in analyses:
        print(f"- [{analysis.ticker}] ({analysis.sentiment}) {analysis.summary}")
        print(f"  key_issues: {analysis.key_issues}")
        print(f"  embedding dim: {len(analysis.embedding)}")

    # TODO: 분석 결과 -> 종목 추천으로 이어지는 LangGraph 워크플로우 연결
    # (docs/ROADMAP.md 3~4단계 참고)


if __name__ == "__main__":
    main()
