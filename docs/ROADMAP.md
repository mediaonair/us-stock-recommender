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
- 무료 뉴스 소스 연동: API 키 없이 사용 가능한 yfinance(Yahoo Finance) 종목 뉴스 사용
- 수집한 원문 뉴스를 저장/전달하는 파이프라인 구성

### 2단계 — 뉴스 분석 모듈 (`feature/news-analyzer`)
- LiteLLM을 통해 Gemini 계열 모델로 뉴스 내용 분석 (요약, 감성, 핵심 이슈 추출)
- `gemini-embedding-001`을 이용한 임베딩 생성 (저장소 연동은 이후 단계에서 진행)

### 3단계 — 종목 추천 로직 (`feature/stock-recommender`)
- 분석 결과(감성, 핵심 이슈)를 종목별로 집계해 점수/랭킹 산출 (1차: 감성 평균 × 언급량 가중치)
- 추천 결과 포맷 정의 (`StockRecommendation`)

### 4단계 — LangGraph 에이전트 워크플로우 통합 (`feature/langgraph-workflow`)
- `collect → analyze → recommend` 노드로 이어지는 LangGraph `StateGraph` 구성 (`src/workflow.py`)
- `AgentState`로 단계 간 상태 전달, 개별 단계 실패는 각 모듈에서 흡수해 전체 흐름은 항상 완주

### 5단계 — 인터페이스 / 실행 (`feature/api-interface`)
- FastAPI로 `/recommendations`, `/health` 조회 API 작성 (`src/api.py`)
- APScheduler로 주기 실행(기본 6시간 간격, `REFRESH_INTERVAL_HOURS`로 조정) 구현, 결과는 캐싱해 매 요청마다 재계산하지 않음

### 6단계 — 테스트 및 배포 준비 (`feature/testing-deployment`)
- `tests/`에 뉴스 수집/분석/추천/워크플로우 단위 테스트 작성 (외부 API는 mock 처리)
- GitHub Actions(`.github/workflows/test.yml`)로 push/PR 시 자동 테스트
- `docs/DEPLOYMENT.md`에 배포/운영 가이드(환경 변수, 실행 명령, 알려진 제약) 정리

### 7단계 — 웹 대시보드 (`feature/web-dashboard`)
- 별도 프론트엔드 빌드 없이 FastAPI가 정적 HTML+JS를 직접 응답하는 방식으로 `/` 대시보드 추가
- `/recommendations`를 주기적으로 fetch해 종목별 점수/감성/핵심 이슈/헤드라인을 카드로 표시

## 상태

- 0단계(프로젝트 기반 설정): 완료
- 1단계(뉴스 수집 모듈): 완료 — yfinance 기반 종목 뉴스 수집 구현
- 2단계(뉴스 분석 모듈): 완료 — LiteLLM + Gemini로 요약/감성/이슈 분석, gemini-embedding-001 임베딩 구현
- 3단계(종목 추천 로직): 완료 — 감성 평균 × 언급량 가중치 기반 1차 스코어링 구현
- 4단계(LangGraph 워크플로우 통합): 완료 — collect/analyze/recommend를 하나의 그래프로 연결
- 5단계(인터페이스 / 실행): 완료 — FastAPI 조회 API + APScheduler 주기 실행 구현
- 6단계(테스트 및 배포 준비): 완료 — 단위 테스트, CI, 배포 문서 정리
- 7단계(웹 대시보드): 완료 — `/`에서 추천 종목을 카드로 보여주는 대시보드 구현

## 향후 개선 아이디어

- 임베딩 결과를 실제 벡터 저장소(예: Chroma, pgvector)에 저장해 유사 뉴스 검색 지원
- 여러 인스턴스로 확장할 때를 대비한 스케줄러 분산 처리 (자세한 내용은 docs/DEPLOYMENT.md 참고)
- 추천 결과의 영속 저장(파일/DB) 및 이력 관리
- 관심 종목 목록을 설정 파일/DB로 분리해 운영 중 변경 가능하도록 개선
