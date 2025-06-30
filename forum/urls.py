from django.urls import path
import forum.views as forum

urlpatterns = [
    path('create_post/', forum.create_post, name='create_post'),
    path('create_post_with_tag/', forum.create_post_with_tag, name='create_post_with_tag'),
    path("get_tag_list_by_post_id/", forum.get_tag_list_by_post_id, name='get_tag_list_by_post_id'),
    path('posts/', forum.get_post_list, name='get_post_list'),
    path('search_post_by_keyword/', forum.search_post_by_keyword, name='search_post_by_keyword'),
    path('post_detail/', forum.get_post_detail_by_id, name='get_post_detail_by_id'),
    path('create_comment/', forum.create_comment_of_post, name='create_comment'),
    path('comments/', forum.get_comment_list_by_post_id, name='get_comment_list_by_post_id'),
    path('delete_post/', forum.delete_post, name='delete_post'),
    path('delete_comment/', forum.delete_comment, name='delete_comment'),
    path('create_comment_of_object/', forum.create_comment_of_object, name='create_comment_of_object'),
    path('comments_of_object/', forum.get_comment_list_of_object, name='get_comment_list_of_object'),
    path('add_tag_to_post/', forum.add_tag_to_post, name='add_tag_to_post'),
    path('remove_tag_from_post/', forum.remove_tag_from_post, name='remove_tag_from_post'),
    path('get_reply_list_of_comment/', forum.get_reply_list_of_comment, name='get_reply_list_of_comment'),
    path('get_comment_detail_by_id/', forum.get_comment_detail_by_id, name='get_comment_detail_by_id'),
    path('create_report/', forum.create_report, name='create_report'),
    path('modify_report_solved_state/', forum.modify_report_solved_state, name='modify_report_solved_state'),
    path('get_report_list/', forum.get_report_list, name='get_report_list'),
    path('delete_reported_object/', forum.delete_reported_object, name='delete_reported_object'),
    path('ban_reported_user/', forum.ban_reported_user, name='ban_reported_user'),
]