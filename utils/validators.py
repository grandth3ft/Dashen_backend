import re

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_valid_email(email):
    return bool(email) and bool(EMAIL_REGEX.match(email))


def is_valid_password(password):
    return bool(password) and len(password) >= 6
