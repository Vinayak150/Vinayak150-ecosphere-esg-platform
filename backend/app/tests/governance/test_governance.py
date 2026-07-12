from datetime import date, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import select

from app.auth.models import Department, Employee, Organization
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
            slug="governance-test-dept",
            name="Governance Test Department",
            code="GOV",
            status=EntityStatus.ACTIVE,
        )
        db_session.add(department)
        db_session.flush()
    return str(department.id)


@pytest.fixture
def employee_id(db_session) -> str:
    employee = db_session.scalars(
        select(Employee).where(Employee.status == EntityStatus.ACTIVE).limit(1)
    ).first()
    assert employee is not None
    return str(employee.id)


@pytest.fixture
def policy_payload() -> dict:
    return {
        "title": "Code of Conduct",
        "version": "1.0",
        "description": "Employee code of conduct policy",
        "effective_date": date.today().isoformat(),
        "status": "ACTIVE",
    }


@pytest.fixture
def created_policy(db_client, admin_tokens, policy_payload) -> dict:
    response = db_client.post(
        "/api/v1/governance/policies",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
        json=policy_payload,
    )
    assert response.status_code == 201
    return response.json()["data"]


def test_policy_crud(db_client, admin_tokens, policy_payload) -> None:
    create_response = db_client.post(
        "/api/v1/governance/policies",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
        json=policy_payload,
    )
    assert create_response.status_code == 201
    policy = create_response.json()["data"]
    assert policy["title"] == "Code of Conduct"

    list_response = db_client.get(
        "/api/v1/governance/policies?search=Conduct",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
    )
    assert list_response.status_code == 200
    assert list_response.json()["data"]["pagination"]["total"] >= 1

    delete_response = db_client.delete(
        f"/api/v1/governance/policies/{policy['id']}",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
    )
    assert delete_response.status_code == 200


def test_policy_acknowledgement(db_client, admin_tokens, created_policy) -> None:
    response = db_client.post(
        "/api/v1/governance/policy-acknowledgements",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
        json={"policy_id": created_policy["id"]},
    )
    assert response.status_code == 201
    acknowledgement = response.json()["data"]
    assert acknowledgement["status"] == "ACKNOWLEDGED"
    assert acknowledgement["acknowledged_at"] is not None


def test_audit_crud(
    db_client, admin_tokens, department_id, employee_id
) -> None:
    payload = {
        "department_id": department_id,
        "title": "Q1 Safety Audit",
        "auditor_id": employee_id,
        "audit_date": date.today().isoformat(),
        "status": "PLANNED",
    }
    create_response = db_client.post(
        "/api/v1/governance/audits",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
        json=payload,
    )
    assert create_response.status_code == 201
    audit = create_response.json()["data"]

    complete_response = db_client.put(
        f"/api/v1/governance/audits/{audit['id']}",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
        json={"status": "COMPLETED"},
    )
    assert complete_response.status_code == 200
    assert complete_response.json()["data"]["status"] == "COMPLETED"


def test_compliance_issue_lifecycle(
    db_client, admin_tokens, employee_id
) -> None:
    create_response = db_client.post(
        "/api/v1/governance/compliance-issues",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
        json={
            "owner_id": employee_id,
            "severity": "HIGH",
            "description": "Missing safety documentation",
            "due_date": (date.today() + timedelta(days=14)).isoformat(),
        },
    )
    assert create_response.status_code == 201
    issue = create_response.json()["data"]
    assert issue["status"] == "OPEN"

    close_response = db_client.post(
        f"/api/v1/governance/compliance-issues/{issue['id']}/close",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
    )
    assert close_response.status_code == 200
    assert close_response.json()["data"]["status"] == "CLOSED"


def test_overdue_issue_flagged(db_client, admin_tokens, employee_id) -> None:
    create_response = db_client.post(
        "/api/v1/governance/compliance-issues",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
        json={
            "owner_id": employee_id,
            "severity": "CRITICAL",
            "description": "Expired certification",
            "due_date": (date.today() - timedelta(days=3)).isoformat(),
        },
    )
    assert create_response.status_code == 201
    issue_id = create_response.json()["data"]["id"]

    get_response = db_client.get(
        f"/api/v1/governance/compliance-issues/{issue_id}",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
    )
    assert get_response.status_code == 200
    overdue_issue = get_response.json()["data"]
    assert overdue_issue["status"] == "OVERDUE"


def test_governance_analytics(db_client, admin_tokens, created_policy) -> None:
    response = db_client.get(
        "/api/v1/governance/analytics/dashboard",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
    )
    assert response.status_code == 200
    analytics = response.json()["data"]
    assert "governance_score" in analytics
    assert "compliance_rate" in analytics
    assert "open_issues" in analytics
    assert "overdue_issues" in analytics
    assert "policy_completion" in analytics
    assert Decimal(analytics["governance_score"]) >= 0


def test_dashboard_includes_governance_score(db_client, admin_tokens) -> None:
    response = db_client.get(
        "/api/v1/dashboard",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["governanceScore"]["available"] is True
    assert data["governanceScore"]["score"] is not None


def test_governance_requires_authentication(client) -> None:
    response = client.get("/api/v1/governance/policies")
    assert response.status_code == 401
