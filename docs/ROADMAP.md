# 개발 로드맵

이 문서는 미국 주식 뉴스 분석·추천 에이전트의 개발 단계를 정의합니다. 각 단계는 Git Flow의
`feature/*` 브랜치 하나(또는 여러 개)에 대응하며, `develop`에서 분기하여 작업 후 `develop`으로
병합하는 것을 기본 흐름으로 합니다.

## 진행 방식

- 각 단계는 순서대로 진행하는 것을 기본으로 하되, 필요 시 순서를 조정할 수 있습니다.
- 하나의 단계 작업이 끝나면 해당 `feature/*` 브랜치를 `develop`에 병합하고, 다음 단계로 넘어갑니다.
- 이 문서는 프로젝트가 진행되며 계속 갱신됩니다.

## 단계

### 0단계 — 프로젝트 기반 설정 (`feature/project-skeleton`)
- 프로젝트 디렉토리 구조 정의 (`src/`, `docs/`, 등)
- `docker-compose.yml` 기본 골격 작성
- 의존성 관리 파일 작성 (LangGraph, LiteLLM 등 포함)
- `.env.example`로 필요한 환경 변수(Gemini API 키 등) 정의

### 1단계 — 뉴스 수집 모듈 (`feature/news-collector`)
- 미국 주식 관련 뉴스 소스 연동 (API 또는 크롤링)
- 수집한 원문 뉴스를 저장/전달하는 파이프라인 구성

### 2단계 — 뉴스 분석 모듈 (`feature/news-analyzer`)
- LiteLLM을 통해 Gemini 계열 모델로 뉴스 내용 분석 (요약, 감성/이슈 판단 등)
- `gemini-embedding-001`을 이용한 임베딩 생성 및 저장

### 3단계 — 종목 추천 로직 (`feature/stock-recommender`)
- 분석 결과를 바탕으로 종목별 점수/랭킹 산출
- 추천 결과 포맷 정의

### 4단계 — LangGraph 에이전트 워크플로우 통합 (`feature/langgraph-workflow`)
- 수집 → 분석 → 추천으로 이어지는 전체 흐름을 LangGraph 그래프로 구성
- 단계 간 상태(State) 정의 및 에러 처리

### 5단계 — 인터페이스 / 실행 (`feature/api-interface`)
- 추천 결과를 조회할 수 있는 API 또는 실행 스크립트 작성
- 주기 실행(스케줄링) 방식 결정

### 6단계 — 테스트 및 배포 준비 (`feature/testing-deployment`)
- 주요 모듈에 대한 테스트 작성
- Docker Compose 기반 배포 문서화, 운영 관련 정리

## 상태

현재 0단계(프로젝트 기반 설정) 진행 중입니다.
