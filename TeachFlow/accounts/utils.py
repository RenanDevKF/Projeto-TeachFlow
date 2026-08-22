import re

def normalize_username(value):
    return (value or '').strip().lower()


def normalize_email(value):
    return (value or '').strip().lower()

def validate_username(value):
    username = normalize_username(value)

    if not re.fullmatch(r'[\w.-]+', username, flags=re.UNICODE):
        return 'Use apenas letras, números, ponto, hífen e sublinhado.'

    return None