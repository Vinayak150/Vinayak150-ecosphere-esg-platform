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
            slug="test-department",
            name="Test Department",
            code="TST",
            status=EntityStatus.ACTIVE,
        )
        db_session.add(department)
        db_session.flush()
    return str(department.id)


@pytest.fixture
def emission_factor_payload() -> dict:
    return {
        "name": "Grid Electricity",
        "source_type": "Energy",
        "unit": "kWh",
        "co2_factor": "0.4500",
        "description": "National grid emission factor",
        "status": "ACTIVE",
    }


@pytest.fixture
def created_emission_factor(db_client, admin_tokens, emission_factor_payload) -> dict:
    response = db_client.post(
        "/api/v1/environmental/emission-factors",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
        json=emission_factor_payload,
    )
    assert response.status_code == 201
    return response.json()["data"]


def test_list_departments(db_client, admin_tokens) -> None:
    response = db_client.get(
        "/api/v1/environmental/departments",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)


def test_emission_factor_crud(db_client, admin_tokens, emission_factor_payload) -> None:
    create_response = db_client.post(
        "/api/v1/environmental/emission-factors",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
        json=emission_factor_payload,
    )
    assert create_response.status_code == 201
    factor = create_response.json()["data"]
    assert factor["name"] == "Grid Electricity"
    assert Decimal(factor["co2_factor"]) == Decimal("0.4500")

    list_response = db_client.get(
        "/api/v1/environmental/emission-factors?search=Grid",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
    )
    assert list_response.status_code == 200
    listed = list_response.json()["data"]
    assert listed["pagination"]["total"] >= 1

    update_response = db_client.put(
        f"/api/v1/environmental/emission-factors/{factor['id']}",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
        json={"description": "Updated description"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["data"]["description"] == "Updated description"

    delete_response = db_client.delete(
        f"/api/v1/environmental/emission-factors/{factor['id']}",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
    )
    assert delete_response.status_code == 200


def test_emission_factor_requires_positive_co2(db_client, admin_tokens) -> None:
    response = db_client.post(
        "/api/v1/environmental/emission-factors",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
        json={
            "name": "Invalid Factor",
            "source_type": "Energy",
            "unit": "kWh",
            "co2_factor": "0",
        },
    )
    assert response.status_code == 400


def test_carbon_transaction_auto_calculates(
    db_client, admin_tokens, created_emission_factor, department_id
) -> None:
    payload = {
        "department_id": department_id,
        "emission_factor_id": created_emission_factor["id"],
        "activity_name": "Office electricity usage",
        "quantity": "100.0000",
        "unit": "kWh",
        "transaction_date": date.today().isoformat(),
    }
    response = db_client.post(
        "/api/v1/environmental/carbon-transactions",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
        json=payload,
    )
    assert response.status_code == 201
    transaction = response.json()["data"]
    expected = Decimal("0.4500") * Decimal("100.0000")
    assert Decimal(transaction["calculated_emission"]) == expected.quantize(Decimal("0.0001"))


def test_carbon_calculate_endpoint(
    db_client, admin_tokens, created_emission_factor
) -> None:
    response = db_client.post(
        "/api/v1/environmental/carbon-transactions/calculate",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
        json={
            "emission_factor_id": created_emission_factor["id"],
            "quantity": "50.0000",
        },
    )
    assert response.status_code == 200
    result = response.json()["data"]
    assert Decimal(result["calculated_emission"]) == Decimal("22.5000")


def test_environmental_goal_crud(db_client, admin_tokens, department_id) -> None:
    deadline = (date.today() + timedelta(days=90)).isoformat()
    create_response = db_client.post(
        "/api/v1/environmental/goals",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
        json={
            "department_id": department_id,
            "title": "Reduce emissions by 20%",
            "target_value": "1000.0000",
            "current_value": "250.0000",
            "deadline": deadline,
        },
    )
    assert create_response.status_code == 201
    goal = create_response.json()["data"]
    assert goal["status"] == "IN_PROGRESS"
    assert Decimal(goal["progress_percentage"]) == Decimal("25.00")

    update_response = db_client.put(
        f"/api/v1/environmental/goals/{goal['id']}",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
        json={"current_value": "1000.0000"},
    )
    assert update_response.status_code == 200
    updated = update_response.json()["data"]
    assert updated["status"] == "COMPLETED"
    assert Decimal(updated["progress_percentage"]) == Decimal("100")


def test_goal_rejects_past_deadline(db_client, admin_tokens, department_id) -> None:
    response = db_client.post(
        "/api/v1/environmental/goals",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
        json={
            "department_id": department_id,
            "title": "Invalid goal",
            "target_value": "100.0000",
            "deadline": (date.today() - timedelta(days=1)).isoformat(),
        },
    )
    assert response.status_code == 422


def test_product_esg_profile_crud(db_client, admin_tokens) -> None:
    create_response = db_client.post(
        "/api/v1/environmental/product-esg-profiles",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
        json={
            "product_name": "Eco Widget Pro",
            "carbon_score": "78.50",
            "recyclability": "92.00",
            "supplier_score": "85.00",
            "notes": "Sustainable packaging",
        },
    )
    assert create_response.status_code == 201
    profile = create_response.json()["data"]
    assert profile["product_name"] == "Eco Widget Pro"

    list_response = db_client.get(
        "/api/v1/environmental/product-esg-profiles?search=Eco",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
    )
    assert list_response.status_code == 200
    assert list_response.json()["data"]["pagination"]["total"] >= 1

    delete_response = db_client.delete(
        f"/api/v1/environmental/product-esg-profiles/{profile['id']}",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
    )
    assert delete_response.status_code == 200


def test_analytics_dashboard(
    db_client, admin_tokens, created_emission_factor, department_id
) -> None:
    db_client.post(
        "/api/v1/environmental/carbon-transactions",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
        json={
            "department_id": department_id,
            "emission_factor_id": created_emission_factor["id"],
            "activity_name": "Fleet fuel",
            "quantity": "200.0000",
            "unit": "kWh",
            "transaction_date": date.today().isoformat(),
        },
    )

    response = db_client.get(
        "/api/v1/environmental/analytics/dashboard",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
    )
    assert response.status_code == 200
    analytics = response.json()["data"]
    assert "department_carbon_totals" in analytics
    assert "monthly_carbon_trend" in analytics
    assert "top_carbon_sources" in analytics
    assert "goal_progress" in analytics
    assert Decimal(analytics["total_emissions"]) > 0


def test_environmental_requires_authentication(client) -> None:
    response = client.get("/api/v1/environmental/emission-factors")
    assert response.status_code == 401
