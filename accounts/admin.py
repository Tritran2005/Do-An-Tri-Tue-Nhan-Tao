from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'company_name', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Thông tin phân quyền & hồ sơ', {'fields': ('role', 'phone_number', 'company_name')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Thông tin phân quyền & hồ sơ', {'fields': ('role', 'phone_number', 'company_name')}),
    )
