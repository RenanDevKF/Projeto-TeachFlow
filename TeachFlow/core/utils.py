import re

from .models import Tag


def normalize_tag_name(value):
    return ' '.join(str(value or '').split())


def validate_tag_name(value):
    name = normalize_tag_name(value)
    max_length = Tag._meta.get_field('name').max_length

    if not name:
        return 'Informe o nome da tag.'

    if len(name) < 2:
        return 'O nome deve possuir pelo menos 2 caracteres.'

    if len(name) > max_length:
        return f'O nome deve possuir no máximo {max_length} caracteres.'

    if not re.fullmatch(r'[\w\sÀ-ÿ\-]+', name):
        return 'Use apenas letras, números, espaços, hífens e underscores.'

    return None


def find_existing_tag(teacher, name):
    return Tag.objects.filter(
        teacher=teacher,
        name__iexact=normalize_tag_name(name),
    ).first()


def normalize_objective_title(value):
    return ' '.join(str(value or '').split())