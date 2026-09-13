"""
us-stock-recommender 에이전트 진입점.

수집 -> 분석 -> 추천으로 이어지는 전체 흐름을 LangGraph 워크플로우(src/workflow.py)로
실행합니다. (docs/ROADMAP.md 4단계)
"""

import os

from dotenv import load_dotenv

from src.workflow import run_workflow

load_dotenv()


def main() -> None:
    embedding_model = os.getenv("EMBEDDING_MODEL", "gemini/gemini-embedding-001")
    print("us-stock-recommender agent starting...")
    print(f"embedding model: {embedding_model}")

    if not os.getenv("GEMINI_API_KEY"):
        print(
            "GEMINI_API_KEY가 설정되어 있지 않아 뉴스 수집까지만 확인하고, "
            "분석/추천 단계는 빈 결과로 넘어갑니다."
        )

    state = run_workflow()

    news_items = state.get("news_items", [])
    print(f"수집된 뉴스: {len(news_items)}건")
    for item in news_items[:5]:
        print(f"- [{item.ticker}] {item.title} ({item.publisher})")

    analyses = state.get("analyses", [])
    if analyses:
        print(f"\n분석된 뉴스: {len(analyses)}건")
        for analysis in analyses:
            print(f"- [{analysis.ticker}] ({analysis.sentiment}) {analysis.summary}")
            print(f"  key_issues: {analysis.key_issues}")

    recommendations = state.get("recommendations", [])
    if recommendations:
        print(f"\n추천 종목 ({len(recommendations)}개, 점수 높은 순):")
        for rec in recommendations:
            print(
                f"- {rec.ticker}: score={rec.score} "
                f"(avg_sentiment={rec.average_sentiment}, news_count={rec.news_count})"
            )
            print(f"  key_issues: {rec.key_issues}")


if __name__ == "__main__":
    main()
