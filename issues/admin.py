from django.contrib import admin
from .models import JiraSetting


@admin.register(JiraSetting)
class JiraSettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'value')
    search_fields = ('key',)
