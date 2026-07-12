import enum

from app.shared.exceptions.base import ValidationError


def parse_enum_value[E: enum.Enum](
    value: str | None,
    enum_cls: type[E],
    field_name: str = "status",
) -> E | None:
    if value is None:
        return None
    try:
        return enum_cls(value)
    except ValueError as exc:
        raise ValidationError(f"Invalid {field_name}: {value}") from exc
