"""
us-stock-recommender 에이전트 진입점.

현재는 뼈대(skeleton) 단계로, 실제 뉴스 수집/분석/추천 로직은
docs/ROADMAP.md의 단계에 따라 이후 feature 브랜치에서 구현됩니다.
"""

import os

from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    embedding_model = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")
    print("us-stock-recommender agent starting...")
    print(f"embedding model: {embedding_model}")
    # TODO: 뉴스 수집 -> 분석 -> 추천으로 이어지는 LangGraph 워크플로우 연결
    # (docs/ROADMAP.md 1~4단계 참고)


if __name__ == "__main__":
    main()
