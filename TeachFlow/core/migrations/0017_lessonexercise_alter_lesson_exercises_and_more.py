# Generated manually for the LessonExercise intermediate model.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            'core',
            '0016_alter_exercise_duration',
        ),
    ]

    operations = [
        # Cria primeiro o model intermediário que será responsável
        # pelo vínculo entre aulas e exercícios.
        migrations.CreateModel(
            name='LessonExercise',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'is_applied',
                    models.BooleanField(
                        default=False,
                        help_text=(
                            'Indica se o exercício foi efetivamente '
                            'aplicado nesta aula.'
                        ),
                        verbose_name='Aplicado',
                    ),
                ),
                (
                    'created_at',
                    models.DateTimeField(
                        auto_now_add=True,
                        verbose_name='Criado em',
                    ),
                ),
                (
                    'updated_at',
                    models.DateTimeField(
                        auto_now=True,
                        verbose_name='Atualizado em',
                    ),
                ),
                (
                    'exercise',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='lesson_exercises',
                        to='core.exercise',
                        verbose_name='Exercício',
                    ),
                ),
                (
                    'lesson',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='lesson_exercises',
                        to='core.lesson',
                        verbose_name='Aula',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Exercício da aula',
                'verbose_name_plural': 'Exercícios da aula',
                'ordering': [
                    'lesson',
                    'id',
                ],
            },
        ),

        # Remove a relação ManyToMany automática anterior.
        # Como o banco atual contém apenas dados de desenvolvimento,
        # os vínculos antigos podem ser descartados.
        migrations.RemoveField(
            model_name='lesson',
            name='exercises',
        ),

        # Recria o campo usando o model intermediário explícito.
        migrations.AddField(
            model_name='lesson',
            name='exercises',
            field=models.ManyToManyField(
                blank=True,
                related_name='lessons',
                through='core.LessonExercise',
                through_fields=(
                    'lesson',
                    'exercise',
                ),
                to='core.exercise',
            ),
        ),

        # Garante que o mesmo exercício não seja vinculado
        # duas vezes à mesma aula.
        migrations.AddConstraint(
            model_name='lessonexercise',
            constraint=models.UniqueConstraint(
                fields=(
                    'lesson',
                    'exercise',
                ),
                name='unique_lesson_exercise',
            ),
        ),
    ]