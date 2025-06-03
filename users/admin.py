from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django import forms
from .models import User


class UserChangeForm(forms.ModelForm):
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(render_value=True),
        required=False,
        help_text="Enter a new password to change it. Leave blank to keep the current password."
    )

    class Meta:
        model = User
        fields = '__all__'

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            return password  # return raw password to be hashed in save()
        return self.instance.password  # return current hashed password if blank

    def save(self, commit=True):
        user = super().save(commit=False)
        raw_password = self.cleaned_data.get('password')
        if raw_password and raw_password != user.password:
            user.set_password(raw_password)  # hash new password
        if commit:
            user.save()
        return user


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    form = UserChangeForm
    model = User

    list_display = ('email', 'user_name', 'is_staff', 'is_active', 'is_verified')
    list_filter = ('is_staff', 'is_active', 'is_verified')
    search_fields = ('email', 'user_name', 'first_name', 'last_name')
    ordering = ('email',)

    readonly_fields = ('date_joined', 'last_login')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('user_name', 'first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Verification', {'fields': ('is_verified', 'otp', 'otp_created_at')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'is_staff', 'is_active')}
        ),
    )
