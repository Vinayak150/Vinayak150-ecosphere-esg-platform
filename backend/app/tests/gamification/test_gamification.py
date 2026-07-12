from datetime import date, timedelta

import pytest


@pytest.fixture
def challenge_payload() -> dict:
    return {
        "title": "Green Commute Challenge",
        "category": "Sustainability",
        "description": "Use public transport for 5 days",
        "xp": 100,
        "difficulty": "MEDIUM",
        "evidence_required": True,
        "deadline": (date.today() + timedelta(days=30)).isoformat(),
        "status": "ACTIVE",
    }


@pytest.fixture
def created_challenge(db_client, admin_tokens, challenge_payload) -> dict:
    response = db_client.post(
        "/api/v1/gamification/challenges",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
        json=challenge_payload,
    )
    assert response.status_code == 201
    return response.json()["data"]


def test_challenge_crud(db_client, admin_tokens, challenge_payload) -> None:
    create_response = db_client.post(
        "/api/v1/gamification/challenges",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
        json=challenge_payload,
    )
    assert create_response.status_code == 201
    challenge = create_response.json()["data"]
    assert challenge["title"] == "Green Commute Challenge"
    assert challenge["status"] == "ACTIVE"

    list_response = db_client.get(
        "/api/v1/gamification/challenges?search=Commute",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
    )
    assert list_response.status_code == 200
    assert list_response.json()["data"]["pagination"]["total"] >= 1

    update_response = db_client.put(
        f"/api/v1/gamification/challenges/{challenge['id']}",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
        json={"status": "COMPLETED"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["data"]["status"] == "COMPLETED"

    delete_response = db_client.delete(
        f"/api/v1/gamification/challenges/{challenge['id']}",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
    )
    assert delete_response.status_code == 200


def test_participation_lifecycle(db_client, admin_tokens, created_challenge) -> None:
    join_response = db_client.post(
        "/api/v1/gamification/participation",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
        json={"challenge_id": created_challenge["id"]},
    )
    assert join_response.status_code == 201
    participation = join_response.json()["data"]
    assert participation["approval_status"] == "PENDING"

    duplicate_response = db_client.post(
        "/api/v1/gamification/participation",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
        json={"challenge_id": created_challenge["id"]},
    )
    assert duplicate_response.status_code == 409

    submit_response = db_client.put(
        f"/api/v1/gamification/participation/{participation['id']}",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
        json={"progress": 100, "proof_file": "commute-receipt.pdf"},
    )
    assert submit_response.status_code == 200
    assert submit_response.json()["data"]["approval_status"] == "SUBMITTED"

    approve_response = db_client.post(
        f"/api/v1/gamification/participation/{participation['id']}/approve",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
    )
    assert approve_response.status_code == 200
    approved = approve_response.json()["data"]
    assert approved["approval_status"] == "APPROVED"
    assert approved["xp_awarded"] == created_challenge["xp"]


def test_badge_auto_unlock(db_client, admin_tokens, created_challenge) -> None:
    badge_response = db_client.post(
        "/api/v1/gamification/badges",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
        json={
            "name": "First Challenge",
            "description": "Complete your first challenge",
            "unlock_rule": {"rule": "approved_challenges", "threshold": 1},
            "icon": "star",
            "status": "ACTIVE",
        },
    )
    assert badge_response.status_code == 201

    join_response = db_client.post(
        "/api/v1/gamification/participation",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
        json={"challenge_id": created_challenge["id"]},
    )
    participation = join_response.json()["data"]

    db_client.put(
        f"/api/v1/gamification/participation/{participation['id']}",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
        json={"progress": 100, "proof_file": "proof.pdf"},
    )
    db_client.post(
        f"/api/v1/gamification/participation/{participation['id']}/approve",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
    )

    employee_badges_response = db_client.get(
        "/api/v1/gamification/employee-badges",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
    )
    assert employee_badges_response.status_code == 200
    badges = employee_badges_response.json()["data"]["data"]
    assert any(item["badge_name"] == "First Challenge" for item in badges)


def test_reward_redemption(db_client, admin_tokens, created_challenge) -> None:
    join_response = db_client.post(
        "/api/v1/gamification/participation",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
        json={"challenge_id": created_challenge["id"]},
    )
    participation = join_response.json()["data"]
    db_client.put(
        f"/api/v1/gamification/participation/{participation['id']}",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
        json={"progress": 100, "proof_file": "proof.pdf"},
    )
    db_client.post(
        f"/api/v1/gamification/participation/{participation['id']}/approve",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
    )

    reward_response = db_client.post(
        "/api/v1/gamification/rewards",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
        json={
            "name": "Eco Mug",
            "description": "Reusable company mug",
            "points_required": 50,
            "stock": 5,
            "status": "ACTIVE",
        },
    )
    assert reward_response.status_code == 201
    reward = reward_response.json()["data"]

    redeem_response = db_client.post(
        "/api/v1/gamification/rewards/redeem",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
        json={"reward_id": reward["id"]},
    )
    assert redeem_response.status_code == 201
    assert redeem_response.json()["data"]["redeemed_points"] == 50

    updated_reward = db_client.get(
        f"/api/v1/gamification/rewards/{reward['id']}",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
    )
    assert updated_reward.json()["data"]["stock"] == 4


def test_leaderboards(db_client, admin_tokens, created_challenge) -> None:
    company_response = db_client.get(
        "/api/v1/gamification/leaderboard/company",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
    )
    assert company_response.status_code == 200
    assert isinstance(company_response.json()["data"], list)

    department_response = db_client.get(
        "/api/v1/gamification/leaderboard/department",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
    )
    assert department_response.status_code == 200
    assert isinstance(department_response.json()["data"], list)


def test_analytics_dashboard(db_client, admin_tokens) -> None:
    response = db_client.get(
        "/api/v1/gamification/analytics/dashboard",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
    )
    assert response.status_code == 200
    analytics = response.json()["data"]
    assert "total_xp" in analytics
    assert "badge_distribution" in analytics
    assert "top_employees" in analytics
    assert "top_departments" in analytics


def test_dashboard_includes_gamification(db_client, admin_tokens) -> None:
    response = db_client.get(
        "/api/v1/dashboard",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert "topPerformers" in data
    assert "xpLeaderboard" in data
    assert "recentBadgeUnlocks" in data
    assert "challengeProgress" in data


def test_evidence_required_blocks_approval_without_proof(
    db_client, admin_tokens, challenge_payload
) -> None:
    challenge_payload["evidence_required"] = True
    create_response = db_client.post(
        "/api/v1/gamification/challenges",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
        json=challenge_payload,
    )
    challenge = create_response.json()["data"]

    join_response = db_client.post(
        "/api/v1/gamification/participation",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
        json={"challenge_id": challenge["id"]},
    )
    participation = join_response.json()["data"]

    submit_response = db_client.put(
        f"/api/v1/gamification/participation/{participation['id']}",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
        json={"progress": 100},
    )
    assert submit_response.status_code == 400

    approve_response = db_client.post(
        f"/api/v1/gamification/participation/{participation['id']}/approve",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
    )
    assert approve_response.status_code == 400
