# us-stock-recommender

미국 주식 관련 뉴스를 수집·분석하여 유망 종목을 추천하는 에이전트 프로젝트입니다.

## 개요

- 미국 주식 시장의 뉴스를 자동으로 수집하고 분석합니다.
- 분석 결과를 바탕으로 관심을 가질 만한 종목을 추천합니다.
- 전체 서비스는 Docker Compose 기반으로 구성되어, 로컬/서버 환경에서 동일하게 실행할 수 있습니다.

## 기술 스택 / 실행 환경

- **Docker Compose**: 각 컴포넌트(뉴스 수집, 분석, 추천 등)를 컨테이너 단위로 구성하여 관리합니다.
- **AI 에이전트 오픈소스**: 자체 구현 대신 검증된 오픈소스 프레임워크를 적극 활용합니다.
  - [LangGraph](https://github.com/langchain-ai/langgraph): 뉴스 수집 → 분석 → 종목 추천으로 이어지는 에이전트 워크플로우를 그래프 형태로 구성하고 상태를 관리합니다.
  - [LiteLLM](https://github.com/BerriAI/litellm): 여러 LLM 제공자(OpenAI, Anthropic 등)를 하나의 인터페이스로 호출할 수 있도록 추상화하여, 모델 교체·비용 관리를 유연하게 합니다.
- **LLM / 임베딩 모델**: 비용 효율을 고려해 기본 모델은 Gemini 계열을 사용합니다.
  - 베이스 모델: Gemini 계열 (LiteLLM을 통해 호출)
  - 임베딩: `gemini-embedding-001`
- **뉴스 수집**: 별도 API 키가 필요 없는 무료 소스인 [yfinance](https://github.com/ranaroussi/yfinance)(Yahoo Finance)를 사용합니다.
- 세부 서비스 구성 및 아키텍처는 프로젝트가 진행되며 이 문서에 추가될 예정입니다.

## 브랜치 전략 (Git Flow)

이 프로젝트는 [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/) 전략을 따릅니다.

- `main`: 배포 가능한 안정 버전을 유지하는 브랜치입니다.
- `develop`: 다음 릴리스를 준비하는 개발 기본 브랜치입니다. 모든 기능 개발은 이 브랜치를 기준으로 진행됩니다.
- `feature/*`: 개별 기능 개발 브랜치입니다. `develop`에서 분기하여 작업 후 `develop`으로 병합합니다.
- `release/*`: 릴리스 준비 브랜치입니다. `develop`에서 분기하여 최종 점검 후 `main`과 `develop`에 병합합니다.
- `hotfix/*`: 운영 중 긴급 수정을 위한 브랜치입니다. `main`에서 분기하여 수정 후 `main`과 `develop`에 병합합니다.

## 시작하기

```bash
cp .env.example .env  # GEMINI_API_KEY 등 값 채워넣기
docker compose up --build
```

## 개발 로드맵

단계별 개발 계획은 [docs/ROADMAP.md](./docs/ROADMAP.md)를 참고하세요.

## 프로젝트 상태

현재 4단계(LangGraph 워크플로우 통합) 진행 중입니다. 자세한 내용은 [docs/ROADMAP.md](./docs/ROADMAP.md)를 참고하세요.
