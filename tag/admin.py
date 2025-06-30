from django.contrib import admin

# Register your models here.
from .models import Tag

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'tag_type', 'is_post_tag', 'is_competition_tag')
    search_fields = ('name', 'tag_type')
    list_filter = ('tag_type', 'is_post_tag', 'is_competition_tag')