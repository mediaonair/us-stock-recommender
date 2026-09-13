# Changelog

이 프로젝트의 주요 변경 사항을 기록합니다.
형식은 [Keep a Changelog](https://keepachangelog.com/ko/1.0.0/)를 참고합니다.

## [0.1.0] - 2026-09-13

첫 정식 릴리스입니다. Git Flow에 따라 `develop`에서 준비된 아래 기능들을
`main`으로 병합했습니다.

### Added

- 뉴스 수집: `yfinance` 기반 무료 뉴스 수집 모듈 (`src/news_collector.py`)
- 뉴스 분석: LiteLLM + Gemini 계열 모델을 이용한 요약/감성/핵심 이슈 분석 및
  `gemini-embedding-001` 임베딩 생성 (`src/news_analyzer.py`)
- 종목 추천 로직: 감성 점수와 뉴스 볼륨을 반영한 스코어링 (`src/stock_recommender.py`)
- LangGraph 기반 수집 → 분석 → 추천 워크플로우 (`src/workflow.py`)
- FastAPI + APScheduler로 구성된 추천 결과 조회 API (`src/api.py`)
- 단위 테스트 스위트 및 GitHub Actions CI (`tests/`, `.github/workflows/test.yml`)
- Docker Compose 기반 배포 구성 (`Dockerfile`, `docker-compose.yml`)
- 프로젝트 문서: `README.md`, `docs/ROADMAP.md`, `docs/DEPLOYMENT.md`

### Fixed

- Gemini 모델 사용 중단(`gemini-1.5-flash` → `gemini-2.5-flash-lite` →
  `gemini-3.5-flash-lite`)에 따른 `GEMINI_MODEL` 기본값 갱신 및 대응 가이드 추가
