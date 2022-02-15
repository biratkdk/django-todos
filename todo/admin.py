from django.contrib import admin
from .models import Todo


class TodoAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'owner',
        'priority',
        'due_date',
        'is_completed',
        'completed_at',
        'created_at',
    )
    search_fields = ('title', 'description', 'owner__username', 'owner__email')
    list_filter = ('priority', 'is_completed', 'due_date', 'created_at')
    list_per_page = 25
    ordering = ('is_completed', 'due_date', '-created_at')


admin.site.register(Todo, TodoAdmin)
