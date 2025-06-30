from django.urls import path
import competitions.views as competitions

urlpatterns = [
    path('create_competition/', competitions.create_competition, name='create_competition'),
    path('get_competition_list/', competitions.get_competition_list, name='get_competition_list'),
    path('get_competition_info/', competitions.get_competition_info, name='get_competition_info'),
    path('update_competition/', competitions.update_competition, name='update_competition'),
    path('delete_competition/', competitions.delete_competition, name='delete_competition'),
    path('get_competition_admin_list/', competitions.get_competition_admin_list, name='get_competition_admin_list'),
    path('add_competition_focus/', competitions.add_competition_focus, name='add_competition_focus'),
    path('del_competition_focus/', competitions.del_competition_focus, name='del_competition_focus'),
    path('get_tag_list_by_competition/', competitions.get_tag_list_by_competition, name='get_tag_list_by_competition'),
    path('add_participant/', competitions.add_participant, name='add_participant'),
    path('delete_participant/', competitions.delete_participant, name='delete_participant'),
    path('get_participant_list/', competitions.get_participant_list, name='get_participant_list'),
    path('update_participant/', competitions.update_participant, name='update_participant'),
    path('like_participant/', competitions.like_participant, name='like_participant'),
    path('unlike_participant/', competitions.unlike_participant, name='unlike_participant'),
    path('get_like_count/', competitions.get_like_count, name='get_like_count'),
]