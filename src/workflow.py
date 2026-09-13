"""
수집 -> 분석 -> 추천으로 이어지는 전체 흐름을 LangGraph 그래프로 연결하는 모듈.

각 단계(0~3단계)에서 만든 함수를 그대로 노드로 사용하고, 상태(State)를 통해
데이터를 다음 노드로 전달합니다. 개별 단계의 실패(예: GEMINI_API_KEY 미설정)는
각 모듈에서 이미 안전하게 처리되므로, 워크플로우 자체는 항상 끝까지 실행됩니다.
"""

from __future__ import annotations

from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from src.news_analyzer import NewsAnalysis, analyze_news
from src.news_collector import NewsItem, collect_news
from src.stock_recommender import StockRecommendation, recommend_stocks

# 실제로 LLM 분석까지 돌려볼 뉴스 개수 (전체 수집 결과 중 앞에서부터 자름, 비용 절감을 위해 제한)
# 값이 너무 작으면(예: 3) 종목이 여러 개일 때 뒤쪽 종목은 분석 대상에 아예 들지 못할 수 있으니,
# 관심 종목 수 × 분석하고 싶은 종목당 뉴스 수를 고려해 조정한다. (기본 종목 5개 기준 15)
ANALYZE_LIMIT = 15


class AgentState(TypedDict, total=False):
    tickers: list[str] | None
    news_items: list[NewsItem]
    analyses: list[NewsAnalysis]
    recommendations: list[StockRecommendation]


def collect_node(state: AgentState) -> AgentState:
    news_items = collect_news(state.get("tickers"))
    return {"news_items": news_items}


def analyze_node(state: AgentState) -> AgentState:
    news_items = state.get("news_items", [])
    analyses = analyze_news(news_items[:ANALYZE_LIMIT])
    return {"analyses": analyses}


def recommend_node(state: AgentState) -> AgentState:
    analyses = state.get("analyses", [])
    recommendations = recommend_stocks(analyses)
    return {"recommendations": recommendations}


def build_workflow():
    """collect -> analyze -> recommend 순서로 이어지는 LangGraph 그래프를 컴파일합니다."""
    graph = StateGraph(AgentState)
    graph.add_node("collect", collect_node)
    graph.add_node("analyze", analyze_node)
    graph.add_node("recommend", recommend_node)

    graph.add_edge(START, "collect")
    graph.add_edge("collect", "analyze")
    graph.add_edge("analyze", "recommend")
    graph.add_edge("recommend", END)

    return graph.compile()


def run_workflow(tickers: list[str] | None = None) -> AgentState:
    """수집 -> 분석 -> 추천 전체 워크플로우를 실행하고 최종 상태를 반환합니다."""
    workflow = build_workflow()
    return workflow.invoke({"tickers": tickers})
