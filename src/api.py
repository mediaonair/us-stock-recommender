"""
추천 결과를 조회할 수 있는 API 및 주기 실행(스케줄링) 인터페이스.

APScheduler로 일정 주기(REFRESH_INTERVAL_HOURS)마다 LangGraph 워크플로우
(src/workflow.py)를 실행해 추천 결과를 갱신하고, FastAPI로 그 결과를 조회할 수
있는 엔드포인트를 제공합니다. 매 요청마다 LLM을 호출하지 않도록 결과를 메모리에
캐싱합니다.
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from dataclasses import asdict
from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI

from src.workflow import run_workflow

# 몇 시간마다 추천 결과를 새로 계산할지 (기본값: 6시간)
REFRESH_INTERVAL_HOURS = float(os.getenv("REFRESH_INTERVAL_HOURS", "6"))

_state: dict = {
    "recommendations": [],
    "last_updated": None,
    "last_error": None,
}

_scheduler = BackgroundScheduler()


def refresh_recommendations() -> None:
    """워크플로우를 실행해 최신 추천 결과를 캐시에 저장합니다."""
    try:
        result = run_workflow()
        recommendations = result.get("recommendations", [])
        _state["recommendations"] = [asdict(rec) for rec in recommendations]
        _state["last_updated"] = datetime.now(tz=timezone.utc).isoformat()
        _state["last_error"] = None
    except Exception as exc:  # noqa: BLE001 - 스케줄러/서버가 죽지 않도록 함
        _state["last_error"] = str(exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    refresh_recommendations()  # 서버 시작 시 1회 즉시 실행
    _scheduler.add_job(
        refresh_recommendations,
        "interval",
        hours=REFRESH_INTERVAL_HOURS,
        id="refresh_recommendations",
    )
    _scheduler.start()
    yield
    _scheduler.shutdown()


app = FastAPI(title="us-stock-recommender", lifespan=lifespan)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/recommendations")
def get_recommendations() -> dict:
    """가장 최근에 계산된 추천 결과를 반환합니다 (요청마다 재계산하지 않음)."""
    return {
        "recommendations": _state["recommendations"],
        "last_updated": _state["last_updated"],
        "last_error": _state["last_error"],
        "refresh_interval_hours": REFRESH_INTERVAL_HOURS,
    }
