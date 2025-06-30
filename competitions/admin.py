from django.contrib import admin

from .models import Competition

@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'sport', 'time_begin', 'is_finished', 'created_at', 'updated_at')
    search_fields = ('id', 'name', 'sport')
    list_filter = ('is_finished',)
    filter_horizontal = ('tags', 'participants')
    ordering = ('-time_begin', '-id')
    list_per_page = 20