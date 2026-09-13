"""
us-stock-recommender 에이전트 진입점.

현재는 3단계(종목 추천) 데모 단계로, LangGraph 기반 전체 워크플로우 통합은
docs/ROADMAP.md의 4단계에서 이어집니다.
"""

import os

from dotenv import load_dotenv

from src.news_analyzer import analyze_news
from src.news_collector import collect_news
from src.stock_recommender import recommend_stocks

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
            "GEMINI_API_KEY가 설정되어 있지 않아 뉴스 분석/추천 단계는 건너뜁니다. "
            ".env에 키를 채워넣으면 끝까지 실행됩니다."
        )
        return

    analyses = analyze_news(news_items[:ANALYZE_LIMIT])
    print(f"\n분석된 뉴스: {len(analyses)}건")
    for analysis in analyses:
        print(f"- [{analysis.ticker}] ({analysis.sentiment}) {analysis.summary}")
        print(f"  key_issues: {analysis.key_issues}")
        print(f"  embedding dim: {len(analysis.embedding)}")

    recommendations = recommend_stocks(analyses)
    print(f"\n추천 종목 ({len(recommendations)}개, 점수 높은 순):")
    for rec in recommendations:
        print(
            f"- {rec.ticker}: score={rec.score} "
            f"(avg_sentiment={rec.average_sentiment}, news_count={rec.news_count})"
        )
        print(f"  key_issues: {rec.key_issues}")

    # TODO: 수집 -> 분석 -> 추천 전체 흐름을 LangGraph 그래프로 연결
    # (docs/ROADMAP.md 4단계 참고)


if __name__ == "__main__":
    main()
