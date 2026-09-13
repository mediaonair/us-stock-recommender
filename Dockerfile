FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

EXPOSE 8000

# 기본 실행: 추천 결과 조회 API (내부적으로 주기 실행 스케줄러 포함)
# 1회성 CLI 데모 실행은 `docker compose exec agent python -m src.main`
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
