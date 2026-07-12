from datetime import date
from decimal import Decimal

from app.shared.exceptions.base import BusinessRuleViolationError, ValidationError


def validate_positive_decimal(value: Decimal, field_name: str) -> Decimal:
    if value <= 0:
        raise ValidationError(f"{field_name} must be greater than zero")
    return value


def validate_future_deadline(deadline: date) -> date:
    if deadline <= date.today():
        raise BusinessRuleViolationError("Deadline must be in the future")
    return deadline


def calculate_emission(co2_factor: Decimal, quantity: Decimal) -> Decimal:
    validate_positive_decimal(co2_factor, "Emission factor")
    validate_positive_decimal(quantity, "Quantity")
    return (co2_factor * quantity).quantize(Decimal("0.0001"))


def validate_score_range(
    value: Decimal, field_name: str, maximum: Decimal = Decimal("100")
) -> Decimal:
    if value < 0 or value > maximum:
        raise ValidationError(f"{field_name} must be between 0 and {maximum}")
    return value
