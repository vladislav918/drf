from django.contrib import admin
from .models import User, PasswordReset


admin.site.register(User)


admin.site.register(PasswordReset)