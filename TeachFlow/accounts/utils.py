def normalize_username(value):
    return (value or '').strip().lower()


def normalize_email(value):
    return (value or '').strip().lower()