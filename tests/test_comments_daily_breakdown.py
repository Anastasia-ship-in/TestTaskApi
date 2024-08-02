def test_comments_daily_breakdown(client, token):
    response = client.get(
        "/api/comments-daily-breakdown?date_from=2020-02-02&date_to=2022-02-15",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "date" in response.json()[0]
    assert "total_comments" in response.json()[0]
    assert "blocked_comments" in response.json()[0]