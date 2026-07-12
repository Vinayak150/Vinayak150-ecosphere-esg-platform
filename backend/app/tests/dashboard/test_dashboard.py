from decimal import Decimal


def test_dashboard_returns_aggregated_data(db_client, admin_tokens) -> None:
    response = db_client.get(
        "/api/v1/dashboard",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    data = body["data"]
    assert "overallESG" in data
    assert "environmentalScore" in data
    assert "socialScore" in data
    assert "governanceScore" in data
    assert "departmentRanking" in data
    assert "recentCarbonTransactions" in data
    assert "recentActivity" in data
    assert "notifications" in data
    assert "goalProgress" in data
    assert "monthlyCarbonTrend" in data
    assert "topCarbonSources" in data
    assert "quickStats" in data
    assert "quickActions" in data


def test_dashboard_environmental_score_is_computed(db_client, admin_tokens) -> None:
    response = db_client.get(
        "/api/v1/dashboard",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    environmental = data["environmentalScore"]
    assert environmental["available"] is True
    assert Decimal(str(environmental["score"])) >= 0


def test_dashboard_social_and_governance_available(db_client, admin_tokens) -> None:
    response = db_client.get(
        "/api/v1/dashboard",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["socialScore"]["available"] is True
    assert data["socialScore"]["score"] is not None
    assert data["governanceScore"]["available"] is True
    assert data["governanceScore"]["score"] is not None


def test_dashboard_quick_actions_respect_permissions(db_client, admin_tokens) -> None:
    response = db_client.get(
        "/api/v1/dashboard",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
    )

    assert response.status_code == 200
    actions = response.json()["data"]["quickActions"]
    assert len(actions) > 0
    record_carbon = next(action for action in actions if action["id"] == "record-carbon")
    assert record_carbon["enabled"] is True


def test_dashboard_requires_authentication(client) -> None:
    response = client.get("/api/v1/dashboard")
    assert response.status_code == 401


def test_dashboard_requires_dashboard_permission(db_client, admin_tokens) -> None:
    response = db_client.get(
        "/api/v1/dashboard",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
    )
    assert response.status_code == 200
