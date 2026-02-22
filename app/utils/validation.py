import re

def check_strong_password(password):
    """
    Validates a password with these rules:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character"

    return True, "Password is valid"

def validate_phone(phone):
    """
    Validates a phone number:
    - Must contain only digits
    - Can optionally start with '+'
    - Length: 10-15 digits (common international range)
    """
    pattern = r"^\+?\d{10,15}$"
    if re.fullmatch(pattern, phone):
        return True, "Phone number is valid"
    else:
        return False, "Invalid phone number format"

def validate_name(name):
    if len(name) < 3:
        return False, "Name too short"
    return True, "Name is valid"