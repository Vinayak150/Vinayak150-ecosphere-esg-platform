from datetime import date, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import select

from app.auth.models import Department, Organization
from app.shared.models.base import EntityStatus


@pytest.fixture
def department_id(db_session) -> str:
    department = db_session.scalars(
        select(Department).where(Department.status == EntityStatus.ACTIVE).limit(1)
    ).first()
    if department is None:
        organization = db_session.scalars(select(Organization).limit(1)).first()
        assert organization is not None
        department = Department(
            organization_id=organization.id,
            slug="social-test-dept",
            name="Social Test Department",
            code="SOC",
            status=EntityStatus.ACTIVE,
        )
        db_session.add(department)
        db_session.flush()
    return str(department.id)


@pytest.fixture
def csr_activity_payload(department_id) -> dict:
    today = date.today()
    return {
        "title": "Community Tree Planting",
        "category": "Environment",
        "department_id": department_id,
        "description": "Plant trees in local communities",
        "start_date": (today - timedelta(days=1)).isoformat(),
        "end_date": (today + timedelta(days=30)).isoformat(),
        "points": 50,
        "evidence_required": True,
        "status": "ACTIVE",
    }


@pytest.fixture
def created_csr_activity(db_client, admin_tokens, csr_activity_payload) -> dict:
    response = db_client.post(
        "/api/v1/social/csr-activities",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
        json=csr_activity_payload,
    )
    assert response.status_code == 201
    return response.json()["data"]


def test_csr_activity_crud(db_client, admin_tokens, csr_activity_payload) -> None:
    create_response = db_client.post(
        "/api/v1/social/csr-activities",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
        json=csr_activity_payload,
    )
    assert create_response.status_code == 201
    activity = create_response.json()["data"]
    assert activity["title"] == "Community Tree Planting"

    list_response = db_client.get(
        "/api/v1/social/csr-activities?search=Tree",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
    )
    assert list_response.status_code == 200
    assert list_response.json()["data"]["pagination"]["total"] >= 1

    delete_response = db_client.delete(
        f"/api/v1/social/csr-activities/{activity['id']}",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
    )
    assert delete_response.status_code == 200


def test_participation_and_approval_flow(
    db_client, admin_tokens, created_csr_activity
) -> None:
    join_response = db_client.post(
        "/api/v1/social/participation",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
        json={
            "csr_activity_id": created_csr_activity["id"],
            "proof_file": "https://storage.example.com/proof.jpg",
        },
    )
    assert join_response.status_code == 201
    participation = join_response.json()["data"]
    assert participation["approval_status"] == "PENDING"

    approve_response = db_client.post(
        f"/api/v1/social/participation/{participation['id']}/approve",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
    )
    assert approve_response.status_code == 200
    approved = approve_response.json()["data"]
    assert approved["approval_status"] == "APPROVED"
    assert approved["points_earned"] == 50


def test_approval_rejected_without_proof(
    db_client, admin_tokens, department_id
) -> None:
    today = date.today()
    activity_response = db_client.post(
        "/api/v1/social/csr-activities",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
        json={
            "title": "Evidence Required Activity",
            "category": "Volunteering",
            "department_id": department_id,
            "start_date": (today - timedelta(days=1)).isoformat(),
            "end_date": (today + timedelta(days=10)).isoformat(),
            "points": 25,
            "evidence_required": True,
        },
    )
    activity_id = activity_response.json()["data"]["id"]

    join_response = db_client.post(
        "/api/v1/social/participation",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
        json={"csr_activity_id": activity_id},
    )
    participation_id = join_response.json()["data"]["id"]

    approve_response = db_client.post(
        f"/api/v1/social/participation/{participation_id}/approve",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
    )
    assert approve_response.status_code == 422


def test_social_analytics(db_client, admin_tokens, created_csr_activity) -> None:
    response = db_client.get(
        "/api/v1/social/analytics/dashboard",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
    )
    assert response.status_code == 200
    analytics = response.json()["data"]
    assert "social_score" in analytics
    assert Decimal(analytics["social_score"]) >= 0


def test_social_requires_authentication(client) -> None:
    response = client.get("/api/v1/social/csr-activities")
    assert response.status_code == 401
