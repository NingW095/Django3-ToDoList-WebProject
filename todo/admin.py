from django.contrib import admin
from .models import Todo
# Register your models here.

class TodoAdmin(admin.ModelAdmin):
    readonly_fields = ('timestamp',)


admin.site.register(Todo, TodoAdmin)