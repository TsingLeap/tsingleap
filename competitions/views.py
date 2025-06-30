import json
import random

from django.shortcuts import render
from django.db.models import Max, Q
from django.http import HttpRequest
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from users.models import User
from .models import Competition, Focus, Like, Participant
from tag.models import Tag
from settings.models import UserPermission
from utils.utils_require import check_require, require, ErrorCode
from utils.utils_params import get_user, get_post, get_comment, get_report, get_tag
from utils.utils_request import BAD_METHOD, request_success, request_failed
from utils.utils_competition import MAX_COMPETITION_LIST_LENGTH, TAG_NUM_LIMIT

ERROR_COMPETITION_NOT_FOUND = "Competition not found."
ERROR_PARTICIPANT_NOT_FOUND = "Participant not found."

# 创建赛事
@check_require
def create_competition(req: HttpRequest):
    if req.method != 'POST':
        return BAD_METHOD

    body = json.loads(req.body.decode("utf-8")) if req.body else {}

    name = require(body, "name", "string")
    sport = require(body, "sport", "string")
    is_finished = require(body, "is_finished", "bool")
    time_begin_str = require(body, "time_begin", "string")
    tag_ids = require(body, "tag_ids", "list")

    dt = parse_datetime(time_begin_str)
    if dt is not None and timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.get_current_timezone())

    tags_qs = Tag.objects.filter(id__in=tag_ids)
    tags = []
    for tag in tags_qs:
        if not tag.is_competition_tag:
            return request_success({
                "code": 1111,
                "msg": f"Tag {tag.name} is not a competition tag.",
            })
        tags.append(tag)
    if len(tags) > TAG_NUM_LIMIT:
        return request_success({
            "code": 1112,
            "msg": f"Competition can only have {TAG_NUM_LIMIT} tags.",
        })

    competition = Competition.objects.create(
        name=name,
        sport=sport,
        is_finished=is_finished,
        time_begin=dt,
    )
    competition.tags.set(tags)

    return request_success({
        "code": 0,
        "msg": f"Competition {competition.id} created successfully.",
        "data": {
            "id": competition.id,
            "name": competition.name,
            "sport": competition.sport,
            "is_finished": competition.is_finished,
            "time_begin": competition.time_begin.isoformat() if competition.time_begin else None,
            "created_at": competition.created_at.isoformat() if competition.created_at else None,
            "updated_at": competition.updated_at.isoformat() if competition.updated_at else None,
        },
    })

def filter_competition(user_id, tag_list, search_text, before_time, before_id, is_finished, filter_focus):
    qs = Competition.objects.all()
    if filter_focus:
        focus_list = Focus.objects.filter(user__id=user_id).values("competition__id").distinct()
        competition_ids = [item["competition__id"] for item in focus_list]
        qs = qs.filter(id__in=competition_ids, is_finished=is_finished)
    else:
        qs = qs.filter(is_finished=is_finished)

    for tag_id in tag_list:
        qs = qs.filter(tags__id=tag_id)

    if search_text:
        qs = qs.filter(Q(name__icontains=search_text) | Q(sport__icontains=search_text) | Q(participants__name__icontains=search_text))
    qs = qs.distinct()

    if before_time != "" and before_id != -1:
        dt = parse_datetime(before_time)
        if dt is not None and timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.get_current_timezone())
        if is_finished:
            qs = qs.filter(Q(time_begin__lt=dt) | (Q(time_begin=dt) & Q(id__lt=before_id)))
        else:
            qs = qs.filter(Q(time_begin__gt=dt) | (Q(time_begin=dt) & Q(id__gt=before_id)))

    return qs

#动态拉取赛事
@check_require
def get_competition_list(req: HttpRequest):
    if req.method != 'POST':
        return BAD_METHOD
    
    body = json.loads(req.body.decode("utf-8")) if req.body else {}
    
    user_id = require(body, "user_id", "int")
    tag_list = require(body, "tag_list", "list")
    search_text = require(body, "search_text", "string")
    before_time = require(body, "before_time", "string")
    before_id = require(body, "before_id", "int")
    is_finished = require(body, "is_finished", "bool")
    filter_focus = require(body, "filter_focus", "bool")

    qs = filter_competition(user_id, tag_list, search_text, before_time, before_id, is_finished, filter_focus)
    competitions = qs.order_by('-time_begin', '-id')[:MAX_COMPETITION_LIST_LENGTH] if is_finished else qs.order_by('time_begin', 'id')[:MAX_COMPETITION_LIST_LENGTH]

    focus_ids = set(Focus.objects.filter(user_id=user_id).values_list('competition_id', flat=True))
    competition_list = [
        {
            "id": comp.id,
            "name": comp.name,
            "sport": comp.sport,
            "is_finished": comp.is_finished,
            "is_focus": comp.id in focus_ids,
            "time_begin": comp.time_begin.isoformat() if comp.time_begin else None,
            "created_at": comp.created_at.isoformat() if comp.created_at else None,
            "updated_at": comp.updated_at.isoformat() if comp.updated_at else None,
        } for comp in competitions
    ]

    if not competition_list:
        return request_success({
            "code": 1100,
            "msg": "No competitions found.",
            "data": {
                "competition_list": [],
                "before_time": None,
                "before_id": None,
            },
        })

    return request_success({
        "code": 0,
        "msg": "Competition list retrieved successfully.",
        "data": {
            "competition_list": competition_list,
        },
    })

# 获取赛事详情
@check_require
def get_competition_info(req: HttpRequest):
    if req.method != 'GET':
        return BAD_METHOD

    body = req.GET
    competition_id = require(body, "id", "int")
    competition = Competition.objects.filter(id=competition_id).first()

    if not competition:
        return request_success({
            "code": 1101,
            "msg": ERROR_COMPETITION_NOT_FOUND,
            "data": {"competition": None},
        })

    return request_success({
        "code": 0,
        "msg": "Competition info retrieved successfully.",
        "data": {
            "competition": {
                "id": competition.id,
                "name": competition.name,
                "sport": competition.sport,
                "is_finished": competition.is_finished,
                "time_begin": competition.time_begin.isoformat() if competition.time_begin else None,
                "created_at": competition.created_at.isoformat() if competition.created_at else None,
                "updated_at": competition.updated_at.isoformat() if competition.updated_at else None,
            }
        },
    })

# 更新赛事
@check_require
def update_competition(req: HttpRequest):
    if req.method != 'POST':
        return BAD_METHOD

    body = json.loads(req.body.decode("utf-8")) if req.body else {}
    competition_id = require(body, "id", "int")

    competition = Competition.objects.filter(id=competition_id).first()
    if not competition:
        return request_success({
            "code": 1102,
            "msg": ERROR_COMPETITION_NOT_FOUND,
            "data": {"competition": None},
        })

    name = require(body, "name", "string")
    sport = require(body, "sport", "string")
    is_finished = require(body, "is_finished", "bool")
    time_begin_str = require(body, "time_begin", "string")
    tag_ids = require(body, "tag_ids", "list")

    dt = parse_datetime(time_begin_str)
    if dt is not None and timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.get_current_timezone())

    tags_qs = Tag.objects.filter(id__in=tag_ids)
    tags = []
    for tag in tags_qs:
        if not tag.is_competition_tag:
            return request_success({
                "code": 1113,
                "msg": f"Tag {tag.name} is not a competition tag.",
            })
        tags.append(tag)
    if len(tags) > TAG_NUM_LIMIT:
        return request_success({
            "code": 1114,
            "msg": f"Competition can only have {TAG_NUM_LIMIT} tags.",
        })

    competition.name = name
    competition.sport = sport
    competition.is_finished = is_finished
    competition.time_begin = dt
    competition.tags.set(tags) 
    competition.save()

    return request_success({
        "code": 0,
        "msg": f"Competition {competition_id} updated successfully.",
        "data": {
            "competition": {
                "id": competition.id,
                "name": competition.name,
                "sport": competition.sport,
                "is_finished": competition.is_finished,
                "time_begin": competition.time_begin.isoformat() if competition.time_begin else None,
                "created_at": competition.created_at.isoformat() if competition.created_at else None,
                "updated_at": competition.updated_at.isoformat() if competition.updated_at else None,
            }
        },
    })

# 删除赛事
@check_require
def delete_competition(req: HttpRequest):
    if req.method != 'POST':
        return BAD_METHOD

    body = json.loads(req.body.decode("utf-8")) if req.body else {}
    competition_id = require(body, "id", "int")
    competition = Competition.objects.filter(id=competition_id).first()

    if not competition:
        return request_success({
            "code": 1103,
            "msg": ERROR_COMPETITION_NOT_FOUND,
        })

    competition.delete()
    permissions = UserPermission.objects.filter(permission="match.update_match_info", permission_info=str(competition_id))
    permissions.delete()

    return request_success({
        "code": 0,
        "msg": f"Competition {competition_id} deleted successfully.",
    })

# 增加参赛者
def add_participant(req: HttpRequest):
    if req.method != 'POST':
        return BAD_METHOD
    
    body = json.loads(req.body.decode("utf-8")) if req.body else {}
    competition_id = require(body, "competition_id", "int")
    participants = require(body, "participants", "list")

    competition = Competition.objects.filter(id=competition_id).first()
    if not competition:
        return request_success({
            "code": 1118,
            "msg": ERROR_COMPETITION_NOT_FOUND,
        })
    
    for item in participants:
        if "name" not in item or "score" not in item:
            return request_success({
                "code": 1119,
                "msg": "Participant data is missing name or score.",
            })
    for item in participants:
        participant_name = item["name"]
        participant_score = item["score"]
        participant = Participant.objects.create(name=participant_name, score=participant_score)
        competition.participants.add(participant)

    return request_success({
        "code": 0,
        "msg": f"Participant {participant_name} added to competition {competition_id}."
    })

# 删除参赛者
def delete_participant(req: HttpRequest):
    if req.method != 'POST':
        return BAD_METHOD
    
    body = json.loads(req.body.decode("utf-8")) if req.body else {}
    participant_ids = require(body, "participant_ids", "list")

    Participant.objects.filter(id__in=participant_ids).delete() 

    return request_success({
        "code": 0,
        "msg": f"Participants removed successfully."
    })

# 修改参赛者信息
def update_participant(req: HttpRequest):
    if req.method != 'POST':
        return BAD_METHOD
    
    body = json.loads(req.body.decode("utf-8")) if req.body else {}
    participants = require(body, "participants", "list")
    
    for item in participants:
        if "id" not in item or "name" not in item or "score" not in item:
            return request_success({
                "code": 1124,
                "msg": "Participant data is missing id, name or score.",
            })
        
    participant_ids = [item["id"] for item in participants]
    db_participants = Participant.objects.in_bulk(participant_ids)

    for item in participants:
        participant = db_participants[item["id"]]
        participant.name = item["name"]
        participant.score = item["score"]
        participant.save()

    return request_success({
        "code": 0,
        "msg": f"Participants updated successfully."
    })

# 获得参赛者列表
def get_participant_list(req: HttpRequest):
    if req.method != 'GET':
        return BAD_METHOD
    
    body = req.GET
    user_id = require(body, "user_id", "int")
    competition_id = require(body, "competition_id", "int")
    
    competition = Competition.objects.filter(id=competition_id).first()
    if not competition:
        return request_success({
            "code": 1120,
            "msg": ERROR_COMPETITION_NOT_FOUND,
            "data": {"participant_list": []},
        })

    like_ids = set(Like.objects.filter(user_id=user_id).values_list('participant_id', flat=True))
    participant_list = competition.participants.all()
    participant_list = [
        {
            "id": participant.id,
            "name": participant.name,
            "score": participant.score,
            "like": participant.id in like_ids,
            "like_count": Like.objects.filter(participant_id=participant.id).count(),
        } for participant in participant_list
    ]

    return request_success({
        "code": 0,
        "msg": "Participant list retrieved successfully.",
        "data": {"participant_list": participant_list},
    })

# 获取赛事管理员
@check_require
def get_competition_admin_list(req: HttpRequest):
    if req.method != 'GET':
        return BAD_METHOD

    body = req.GET
    competition_id = require(body, "id", "int")
    competition = Competition.objects.filter(id=competition_id).first()

    if not competition:
        return request_success({
            "code": 1104,
            "msg": ERROR_COMPETITION_NOT_FOUND,
            "data": {"admin_list": []},
        })

    admin_list = UserPermission.objects.filter(
        permission="match.update_match_info", permission_info=str(competition_id)
    ).values("user__username", "user__nickname").distinct()

    admin_list = [
        {
            "username": item["user__username"],
            "nickname": item["user__nickname"],
        } for item in admin_list
    ]

    return request_success({
        "code": 0,
        "msg": "Competition admin list retrieved successfully.",
        "data": {"admin_list": admin_list},
    })

#添加关注
@check_require
def add_competition_focus(req: HttpRequest):
    if req.method != 'POST':
        return BAD_METHOD

    body = json.loads(req.body.decode("utf-8")) if req.body else {}
    competition_id = require(body, "competition_id", "int")
    user_id = require(body, "user_id", "int")

    competition = Competition.objects.filter(id=competition_id).first()
    if not competition:
        return request_success({
            "code": 1105,
            "msg": ERROR_COMPETITION_NOT_FOUND,
        })

    if Focus.objects.filter(user__id=user_id, competition__id=competition_id).exists():
        return request_success({
            "code": 1106,
            "msg": "User already follows this competition.",
        })

    user = User.objects.filter(id=user_id).first()
    Focus.objects.create(user=user, competition=competition)

    return request_success({
        "code": 0,
        "msg": f"User {user_id} added to focus for competition {competition_id}.",
    })

#取消关注
@check_require
def del_competition_focus(req: HttpRequest):
    if req.method != 'POST':
        return BAD_METHOD

    body = json.loads(req.body.decode("utf-8")) if req.body else {}
    competition_id = require(body, "competition_id", "int")
    user_id = require(body, "user_id", "int")

    competition = Competition.objects.filter(id=competition_id).first()
    if not competition:
        return request_success({
            "code": 1107,
            "msg": ERROR_COMPETITION_NOT_FOUND,
        })

    # Check if the user is already a focus
    focus = Focus.objects.filter(user__id=user_id, competition__id=competition_id).first()
    if not focus:
        return request_success({
            "code": 1108,
            "msg": "User does not follow this competition.",
        })

    # Delete focus
    focus.delete()

    return request_success({
        "code": 0,
        "msg": f"User {user_id} removed from focus for competition {competition_id}.",
    })

#通过赛事id获取标签列表
@check_require
def get_tag_list_by_competition(req: HttpRequest):
    if req.method != 'GET':
        return BAD_METHOD

    body = req.GET
    competition_id = require(body, "competition_id", "int")
    competition = Competition.objects.filter(id=competition_id).first()

    if not competition:
        return request_success({
            "code": 1109,
            "msg": ERROR_COMPETITION_NOT_FOUND,
            "data": {"tag_list": []},
        })

    tag_list = competition.tags.all()
    tag_list = [
        {
            "id": tag.id,
            "name": tag.name,
            "tag_type": tag.tag_type,
            "is_post_tag": tag.is_post_tag,
            "is_competition_tag": tag.is_competition_tag
        } for tag in tag_list
    ]

    priority = {
        "sports": 0,
        "department": 1,
        "evemt": 2,
    }
    tag_list.sort(key=lambda t: (priority.get(t["tag_type"], 99), t["id"]))

    return request_success({
        "code": 0,
        "msg": "Tag list retrieved successfully.",
        "data": {"tag_list": tag_list},
    })

# 点赞选手
def like_participant(req: HttpRequest):
    if req.method != "POST":
        return BAD_METHOD
    
    body = json.loads(req.body.decode("utf-8")) if req.body else {}
    user_id = require(body, "user_id", "int")
    participant_id = require(body, "participant_id", "int")
    
    participant= Participant.objects.filter(id=participant_id).first()
    if not participant:
        return request_success({
            "code": 1115,
            "msg": ERROR_PARTICIPANT_NOT_FOUND
        })
    user = User.objects.filter(id=user_id).first()
    if not user:
        return request_success({
            "code": 1116,
            "msg": "User not found.",
        })
    like_obj = Like.objects.filter(user_id=user_id, participant_id=participant_id).first()
    if like_obj:
        return request_success({
            "code": 1117,
            "msg": "User has already liked this competition.",
        })
    
    
    Like.objects.create(user=user, participant=participant)
    return request_success({
        "code": 0,
        "msg": "Participant liked successfully.",
    })

# 取消点赞选手
def unlike_participant(req: HttpRequest):
    if req.method != "POST":
        return BAD_METHOD
    
    body = json.loads(req.body.decode("utf-8")) if req.body else {}
    user_id = require(body, "user_id", "int")
    participant_id = require(body, "participant_id", "int")
    
    participant= Participant.objects.filter(id=participant_id).first()
    if not participant:
        return request_success({
            "code": 1121,
            "msg": ERROR_PARTICIPANT_NOT_FOUND
        })
    user = User.objects.filter(id=user_id).first()
    if not user:
        return request_success({
            "code": 1122,
            "msg": "User not found.",
        })
    
    like_obj = Like.objects.filter(user_id=user_id, participant_id=participant_id).first()
    if not like_obj:
        return request_success({
            "code": 1123,
            "msg": "User has not liked this competition.",
        })
    
    like_obj.delete()
    return request_success({
        "code": 0,
        "msg": "Participant unliked successfully.",
    })

# 获得点赞个数
def get_like_count(req: HttpRequest):
    if req.method != "GET":
        return BAD_METHOD
    
    body = req.GET
    user_id = require(body, "user_id", "int")
    participant_id = require(body, "participant_id", "int")
    
    participant= Participant.objects.filter(id=participant_id).first()
    if not participant:
        return request_success({
            "code": 1125,
            "msg": ERROR_PARTICIPANT_NOT_FOUND
        })
    
    like_count = Like.objects.filter(participant_id=participant_id).count()
    
    return request_success({
        "code": 0,
        "msg": "Like count retrieved successfully.",
        "data": {
            "is_like": Like.objects.filter(user_id=user_id, participant_id=participant_id).exists(),
            "like_count": like_count
        }
    })