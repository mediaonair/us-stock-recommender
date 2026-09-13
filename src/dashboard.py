"""
`/recommendations` API 결과를 표/카드 형태로 보여주는 간단한 웹 대시보드.

서버 사이드 템플릿 엔진(Jinja2 등) 없이, 정적인 HTML 뼈대 안에 자바스크립트를
포함시켜 브라우저에서 `/recommendations`를 호출(fetch)해 렌더링하는 방식입니다.
별도 프론트엔드 빌드 과정이 필요 없어 Docker 이미지에 추가 의존성이 생기지 않습니다.
"""

from __future__ import annotations

DEFAULT_AUTO_REFRESH_SECONDS = 60


def render_dashboard(
    refresh_interval_hours: float, auto_refresh_seconds: int = DEFAULT_AUTO_REFRESH_SECONDS
) -> str:
    """대시보드 HTML 페이지를 생성합니다."""
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>US Stock Recommender</title>
<style>
  :root {{
    color-scheme: light dark;
    --bg: #0f172a;
    --card-bg: #1e293b;
    --text: #e2e8f0;
    --muted: #94a3b8;
    --border: #334155;
    --positive: #22c55e;
    --neutral: #94a3b8;
    --negative: #ef4444;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    padding: 24px 16px 48px;
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Pretendard, sans-serif;
  }}
  .wrap {{ max-width: 960px; margin: 0 auto; }}
  h1 {{ font-size: 1.5rem; margin-bottom: 4px; }}
  .meta {{ color: var(--muted); font-size: 0.85rem; margin-bottom: 24px; }}
  .error {{
    background: #7f1d1d;
    color: #fecaca;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 16px;
    font-size: 0.9rem;
  }}
  .empty {{ color: var(--muted); padding: 32px 0; text-align: center; }}
  .grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 16px;
  }}
  .card {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px;
  }}
  .card-header {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 8px;
  }}
  .ticker {{ font-size: 1.25rem; font-weight: 700; }}
  .score {{ font-size: 1.1rem; font-weight: 700; }}
  .score.positive {{ color: var(--positive); }}
  .score.neutral {{ color: var(--neutral); }}
  .score.negative {{ color: var(--negative); }}
  .sub {{ color: var(--muted); font-size: 0.85rem; margin-bottom: 12px; }}
  .badges {{ display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px; }}
  .badge {{
    background: rgba(148, 163, 184, 0.15);
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: 2px 10px;
    font-size: 0.75rem;
    color: var(--muted);
  }}
  .headlines {{ margin: 0; padding-left: 18px; font-size: 0.85rem; color: var(--text); }}
  .headlines li {{ margin-bottom: 4px; }}
  #status {{ color: var(--muted); font-size: 0.8rem; margin-top: 32px; text-align: center; }}
</style>
</head>
<body>
  <div class="wrap">
    <h1>US Stock Recommender</h1>
    <div class="meta">
      뉴스 기반 추천 종목 대시보드 &middot; {auto_refresh_seconds}초마다 자동 새로고침
      &middot; 서버는 {refresh_interval_hours}시간마다 추천을 다시 계산합니다.
    </div>
    <div id="content">
      <div class="empty">불러오는 중...</div>
    </div>
    <div id="status"></div>
  </div>

  <script>
    const AUTO_REFRESH_MS = {auto_refresh_seconds} * 1000;

    function scoreClass(score) {{
      if (score > 0.05) return "positive";
      if (score < -0.05) return "negative";
      return "neutral";
    }}

    function escapeHtml(str) {{
      const div = document.createElement("div");
      div.textContent = str ?? "";
      return div.innerHTML;
    }}

    function renderCard(rec) {{
      const badges = (rec.key_issues || [])
        .map((issue) => `<span class="badge">${{escapeHtml(issue)}}</span>`)
        .join("");
      const headlines = (rec.top_headlines || [])
        .map((title) => `<li>${{escapeHtml(title)}}</li>`)
        .join("");
      return `
        <div class="card">
          <div class="card-header">
            <span class="ticker">${{escapeHtml(rec.ticker)}}</span>
            <span class="score ${{scoreClass(rec.score)}}">${{rec.score.toFixed(2)}}</span>
          </div>
          <div class="sub">
            뉴스 ${{rec.news_count}}건 &middot; 평균 감성 ${{rec.average_sentiment.toFixed(2)}}
          </div>
          <div class="badges">${{badges}}</div>
          <ul class="headlines">${{headlines}}</ul>
        </div>
      `;
    }}

    async function loadRecommendations() {{
      const content = document.getElementById("content");
      const status = document.getElementById("status");
      try {{
        const res = await fetch("/recommendations");
        if (!res.ok) throw new Error(`HTTP ${{res.status}}`);
        const data = await res.json();
        const recs = data.recommendations || [];

        let html = "";
        if (data.last_error) {{
          html += `<div class="error">최근 갱신 중 오류: ${{escapeHtml(data.last_error)}}</div>`;
        }}
        if (recs.length === 0) {{
          html += `<div class="empty">아직 추천 결과가 없습니다. 잠시 후 다시 확인해주세요.</div>`;
        }} else {{
          html += `<div class="grid">${{recs.map(renderCard).join("")}}</div>`;
        }}
        content.innerHTML = html;

        const updated = data.last_updated
          ? new Date(data.last_updated).toLocaleString()
          : "아직 없음";
        status.textContent = `마지막 갱신: ${{updated}}`;
      }} catch (err) {{
        content.innerHTML = `<div class="error">추천 결과를 불러오지 못했습니다: ${{escapeHtml(err.message)}}</div>`;
      }}
    }}

    loadRecommendations();
    setInterval(loadRecommendations, AUTO_REFRESH_MS);
  </script>
</body>
</html>
"""
