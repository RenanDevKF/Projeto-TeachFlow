def normalize_username(value):
    return (value or '').strip().lower()


def normalize_email(value):
    return (value or '').strip().lower()

def validate_username(value):
    username = normalize_username(value)

    if '@' in username:
        return 'O nome de usuário não pode conter @.'

    return None