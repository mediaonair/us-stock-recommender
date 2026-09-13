from src.dashboard import render_dashboard


def test_render_dashboard_includes_key_elements():
    html = render_dashboard(refresh_interval_hours=6, auto_refresh_seconds=30)

    assert "<html" in html
    assert "US Stock Recommender" in html
    assert "/recommendations" in html
    assert "30 * 1000" in html
    assert "6시간마다" in html
