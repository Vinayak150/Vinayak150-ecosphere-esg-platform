def normalize_email(email: str) -> str:
    return str(email).lower().strip()


def validate_password_strength(password: str) -> str:
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters")
    if password.lower() == password:
        raise ValueError("Password must contain at least one uppercase letter")
    if password.upper() == password:
        raise ValueError("Password must contain at least one lowercase letter")
    if not any(char.isdigit() for char in password):
        raise ValueError("Password must contain at least one digit")
    return password
