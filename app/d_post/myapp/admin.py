from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser
from .models import Abonents, Status_history, Registers2
from django.utils.translation import ugettext_lazy as _


# Register your models here.

admin.site.register(Abonents)
admin.site.register(Status_history)
admin.site.register(Registers2)


class CustomUserAdmin(UserAdmin):
        fieldsets = (
            (None, {'fields': ('username', 'password')}),
            (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'fns_id')}),  # added "fns_id" field
            (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
            (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        )

#                    model,      class
admin.site.register(CustomUser, CustomUserAdmin)
