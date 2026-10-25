from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Subscription, Teacher


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    list_display = (
        'email',
        'username',
        'first_name',
        'last_name',
        'email_verified_at',
        'is_active',
        'is_staff',
        'is_teacher',
    )

    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)

    readonly_fields = ('last_login', 'date_joined', 'email_verified_at')

    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Informações Pessoais', {'fields': ('first_name', 'last_name')}),
        ('Verificação', {'fields': ('email_verified_at',)}),
        (
            'Permissões',
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                )
            },
        ),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'email',
                    'username',
                    'first_name',
                    'last_name',
                    'password1',
                    'password2',
                ),
            },
        ),
    )


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_name', 'subject_area')
    search_fields = (
        'user__email',
        'user__username',
        'display_name',
        'subject_area',
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'is_active', 'external_id')
    search_fields = ('user__email', 'user__username', 'external_id')
    list_filter = ('plan', 'is_active')