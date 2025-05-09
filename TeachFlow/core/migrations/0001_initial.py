# Generated by Django 5.2 on 2025-04-25 02:20

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminActionLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('create', 'Criação'), ('update', 'Atualização'), ('delete', 'Exclusão'), ('other', 'Outro')], max_length=100, verbose_name='Ação')),
                ('model_name', models.CharField(max_length=100, verbose_name='Modelo afetado')),
                ('object_id', models.IntegerField(verbose_name='ID do Objeto')),
                ('details', models.JSONField(blank=True, null=True, verbose_name='Detalhes (JSON)')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='Data/Hora')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Usuário')),
            ],
            options={
                'verbose_name': 'Log de Ação',
                'verbose_name_plural': 'Logs de Ações',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='ClassGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('year', models.IntegerField(default=2025)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='class_groups', to='accounts.teacher')),
            ],
        ),
        migrations.CreateModel(
            name='LearningObjective',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='learning_objectives', to='accounts.teacher')),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('notes', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('class_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='students', to='core.classgroup')),
            ],
            options={
                'ordering': ['last_name', 'first_name'],
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('color', models.CharField(default='#007bff', max_length=7)),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tags', to='accounts.teacher')),
            ],
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('performance_notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('class_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lessons', to='core.classgroup')),
                ('objectives', models.ManyToManyField(blank=True, related_name='lessons', to='core.learningobjective')),
                ('tags', models.ManyToManyField(blank=True, related_name='lessons', to='core.tag')),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
        migrations.AddField(
            model_name='learningobjective',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='objectives', to='core.tag'),
        ),
        migrations.CreateModel(
            name='FutureIdea',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('class_group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='future_ideas', to='core.classgroup')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='future_ideas', to='accounts.teacher')),
                ('tags', models.ManyToManyField(blank=True, related_name='future_ideas', to='core.tag')),
            ],
        ),
        migrations.CreateModel(
            name='Exercise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('duration', models.IntegerField(blank=True, help_text='Duration in minutes', null=True)),
                ('materials', models.TextField(blank=True)),
                ('objectives', models.ManyToManyField(blank=True, related_name='exercises', to='core.learningobjective')),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exercises', to='core.lesson')),
                ('tags', models.ManyToManyField(blank=True, related_name='exercises', to='core.tag')),
            ],
        ),
    ]
