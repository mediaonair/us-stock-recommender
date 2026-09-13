# 배포 / 운영 가이드

이 문서는 `us-stock-recommender`를 Docker Compose로 실행하고 운영할 때 참고할
내용을 정리합니다.

## 환경 변수

`.env.example`를 복사해 `.env`를 만들고 값을 채워넣습니다.

| 변수 | 설명 | 기본값 |
| --- | --- | --- |
| `GEMINI_API_KEY` | LiteLLM이 Gemini 계열 모델을 호출할 때 사용하는 API 키. 비어있으면 뉴스 분석/추천 단계는 빈 결과로 넘어갑니다. | (없음) |
| `GEMINI_MODEL` | 뉴스 분석에 사용할 베이스 모델 (LiteLLM 모델명 형식) | `gemini/gemini-2.5-flash-lite` |
| `EMBEDDING_MODEL` | 임베딩 생성에 사용할 모델 | `gemini/gemini-embedding-001` |
| `REFRESH_INTERVAL_HOURS` | 추천 결과를 몇 시간마다 재계산할지 | `6` |

## 실행

```bash
docker compose up --build -d   # 백그라운드 실행
docker compose logs -f agent   # 로그 확인
docker compose down            # 종료
```

서버가 뜨면 `http://localhost:8000`에서 API를 사용할 수 있습니다.

```bash
curl http://localhost:8000/health          # 헬스체크
curl http://localhost:8000/recommendations # 최신 추천 결과 조회
```

1회성으로 전체 파이프라인(수집  분석  추천)을 콘솔에서 바로 확인하려면:

```bash
docker compose exec agent python -m src.main
```

## 재시작 정책

`docker-compose.yml`의 `restart: unless-stopped` 설정으로, 컨테이너가 죽거나
호스트가 재부팅되어도 자동으로 다시 시작됩니다. 사용자가 직접 `docker compose down`
으로 내린 경우에는 자동으로 재시작되지 않습니다.

## 테스트

```bash
pip install -r requirements-dev.txt
pytest
```

`main`/`develop`에 push하거나 PR을 올리면 `.github/workflows/test.yml`을 통해
GitHub Actions에서도 자동으로 테스트가 실행됩니다.

## 모델 이름 관련 문제 해결

Gemini 모델은 종종 새 버전으로 교체되며 이전 모델이 예고 없이 사라지기도 합니다.
`분석 실패 ... 404 ... is not found for API version` 같은 에러가 보이면 `GEMINI_MODEL`에
지정한 모델이 더 이상 제공되지 않는 것이니, [Gemini API 모델 목록](https://ai.google.dev/gemini-api/docs/models)에서
현재 사용 가능한 모델(주로 `flash-lite`가 가장 저렴함)로 `.env`의 `GEMINI_MODEL` 값을 바꿔주면 됩니다.

## 알려진 제약 / 향후 개선 사항

- **스케줄러 중복 실행**: 현재 주기 실행(APScheduler)은 컨테이너(프로세스) 하나를
  기준으로 동작합니다. `docker compose up --scale agent=2`처럼 인스턴스를 여러 개
  띄우면 각 인스턴스가 독립적으로 스케줄러를 실행해 API 호출이 중복될 수 있으니,
  현재 단계에서는 `agent` 서비스를 1개만 실행하는 것을 전제로 합니다. 추후 여러
  인스턴스로 확장하려면 외부 스케줄러(예: 별도 워커 + 큐)나 분산 락 도입이 필요합니다.
- **임베딩 저장소 미연동**: 2단계에서 생성한 임베딩은 아직 별도 벡터 저장소에
  저장되지 않고 메모리상에서만 사용됩니다. 유사 뉴스 검색 등이 필요해지면 벡터 DB
  연동을 추가해야 합니다.
- **추천 결과 영속화 없음**: `/recommendations`의 결과는 프로세스 메모리에만
  캐싱되어 있어 컨테이너를 재시작하면 다음 주기까지 비어 있습니다. 필요하면
  파일/DB에 최신 결과를 저장하는 방식을 추가할 수 있습니다.
