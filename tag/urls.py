from django.urls import path
import tag.views as tag

urlpatterns = [
    path('create_tag/', tag.create_tag, name='create_tag'),
    path('delete_tag/', tag.delete_tag, name='delete_tag'),
    path('get_tag_list/', tag.get_tag_list, name='get_tag_list'),
    path('get_post_list_by_tag/', tag.get_post_list_by_tag, name='get_post_list_by_tag'),
    path('search_tag_by_prefix/', tag.search_tag_by_prefix, name='search_tag_by_prefix'),
]
