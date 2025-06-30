import json, jinja2
from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpRequest, HttpResponse
from django.db.models import Q, Count, F

from users.models import User
from settings.models import UserPermission
from .models import Post, Comment, Report
from competitions.models import Competition
from tag.models import Tag, TagType
from django.contrib.contenttypes.models import ContentType
from utils.utils_request import BAD_METHOD, request_failed, request_success, return_field
from utils.utils_require import check_require, require, ErrorCode
from django.core.paginator import Paginator, EmptyPage
from utils import utils_time
from utils.utils_permission import has_permission, PERMISSION_FORUM_MANAGE_FORUM, PERMISSION_FORUM_POST, PERMISSION_FORUM_POST_HIGHLIGHT
from utils.utils_permission import add_permission, remove_permission
from utils.utils_forum import get_reply_list_by_dfs, get_post_info_by_paginator, get_comment_info_by_paginator, get_user_post_tag_from_body
from utils.utils_params import get_user, get_post, get_comment, get_report, get_tag, get_page_info

CONTENT_TYPE = {
    "Post" : Post,
    "Comment" : Comment,
    "Competition" : Competition
}
TAG_NUM_LIMIT = 5

@check_require
def create_post(req: HttpRequest):
    if req.method != 'POST':
        return BAD_METHOD
    body = json.loads(req.body.decode("utf-8")) if req.body else {}
    try:
        user = get_user(body, "username")
    except User.DoesNotExist:
        return request_success(ErrorCode.USER_DOES_NOT_EXIST)
    title = require(body, "title", "string")
    content = require(body, "content", "string")
    if not has_permission(user, PERMISSION_FORUM_POST) :
        return request_success(ErrorCode.NO_PERMISSION)
    if len(title) > 255:
        return request_success({
            "code": 1022,
            "msg": "Title is too long"
        })
    Post.objects.create(title=title, content=content, author=user, created_at=utils_time.get_timestamp())
    return request_success({
            "code": 0, 
            "msg": "Post created successfully"
        })

@check_require
def create_post_with_tag(req: HttpRequest):
    if req.method != 'POST':
        return BAD_METHOD
    body = json.loads(req.body.decode("utf-8")) if req.body else {}
    try:
        user = get_user(body, "username")
    except User.DoesNotExist:
        return request_success(ErrorCode.USER_DOES_NOT_EXIST)
    title = require(body, "title", "string")
    content = require(body, "content", "string")
    tag_ids = require(body, "tag_ids", "list")

    tag_ids = list(set(tag_ids))

    if not has_permission(user, PERMISSION_FORUM_POST) :
        return request_success(ErrorCode.NO_PERMISSION)
    if len(title) > 255:
        return request_success({
            "code": 1022,
            "msg": "Title is too long"
        })
    if len(tag_ids) > TAG_NUM_LIMIT:
        return request_success({
            "code": 1045,
            "msg": "Too many tags"
        })

    tags = list()
    for tag_id in tag_ids:
        try:
            tag = Tag.objects.get(id=tag_id)
        except Tag.DoesNotExist:
            return request_success({
                "code": 1046,
                "msg": f"Invalid tag id: {tag_id}"
            })
        if tag.is_post_tag == False:
            return request_success({
                "code": 1047,
                "msg": f"Tag {tag.name} is not a post tag"
            })
        if tag.tag_type == TagType.HIGHLIGHT and not has_permission(user, PERMISSION_FORUM_POST_HIGHLIGHT) :
            return request_success({
                "code": 1048,
                "msg": "No permission for highlight tag"
            })
        tags.append(tag)

    post = Post.objects.create(title=title, content=content, author=user, created_at=utils_time.get_timestamp())
    post.tags.set(tags)
    return request_success({
            "code": 0, 
            "msg": "Post created successfully"
        })

@check_require
def get_tag_list_by_post_id(req: HttpRequest):
    if req.method != 'GET':
        return BAD_METHOD
    try:
        post = get_post(req.GET, "post_id")
    except Post.DoesNotExist:
        return request_success(ErrorCode.POST_DOES_NOT_EXIST)
    tags = post.tags.all()
    return request_success({
        "code": 0,
        "data": [
            {
                "tag_id": tag.id,
                "tag_name": tag.name,
                "tag_type": tag.tag_type,
                "is_post_tag": tag.is_post_tag,
                "is_competition_tag": tag.is_competition_tag
            }
            for tag in tags
        ]
    })

@check_require
def add_tag_to_post(req: HttpRequest):
    if req.method != 'POST':
        return BAD_METHOD
    body = json.loads(req.body.decode("utf-8")) if req.body else {}

    user, post, tag, error = get_user_post_tag_from_body(body)
    if error:
        return request_success(error)

    if tag.is_post_tag == False:
        return request_success({
            "code": 1047,
            "msg": f"Tag {tag.name} is not a post tag"
        })
    if not (has_permission(user, PERMISSION_FORUM_MANAGE_FORUM) or post.author == user) :
        return request_success(ErrorCode.NO_PERMISSION)
    if tag.tag_type == TagType.HIGHLIGHT and not has_permission(user, PERMISSION_FORUM_POST_HIGHLIGHT) :
        return request_success({
            "code": 1048,
            "msg": "No permission for highlight tag"
        })
    if len(post.tags.all()) + 1 > TAG_NUM_LIMIT:
        return request_success({
            "code": 1045,
            "msg": "Too many tags"
        })
    post.tags.add(tag)
    post.save()
    return request_success({
        "code": 0,
        "msg": "Tag added to post successfully"
    })

@check_require
def remove_tag_from_post(req: HttpRequest):
    if req.method != 'POST':
        return BAD_METHOD
    body = json.loads(req.body.decode("utf-8")) if req.body else {}

    user, post, tag, error = get_user_post_tag_from_body(body)
    if error:
        return request_success(error)

    if tag not in post.tags.all():
        return request_success({
            "code": 1050,
            "msg": f"Tag is not in the post"
        })
    if not (has_permission(user, PERMISSION_FORUM_MANAGE_FORUM) or post.author == user) :
        return request_success(ErrorCode.NO_PERMISSION)
    post.tags.remove(tag)
    post.save()
    return request_success({
        "code": 0,
        "msg": "Tag removed from post successfully"
    })

@check_require
def delete_post(req: HttpRequest):
    if req.method != 'POST':
        return BAD_METHOD
    body = json.loads(req.body.decode("utf-8")) if req.body else {}

    try:
        user = get_user(body, "username")
        post = get_post(body, "post_id")
    except User.DoesNotExist:
        return request_success(ErrorCode.USER_DOES_NOT_EXIST)
    except Post.DoesNotExist:
        return request_success(ErrorCode.POST_DOES_NOT_EXIST)

    if not (has_permission(user, PERMISSION_FORUM_MANAGE_FORUM) or post.author == user) :
        return request_success(ErrorCode.NO_PERMISSION)
    post.delete()
    return request_success({
            "code": 0, 
            "msg": "Post deleted successfully"
        })

@check_require
def delete_comment(req: HttpRequest):
    if req.method != 'POST':
        return BAD_METHOD
    body = json.loads(req.body.decode("utf-8")) if req.body else {}
    try:
        user = get_user(body, "username")
        comment = get_comment(body, "comment_id")
    except User.DoesNotExist:
        return request_success(ErrorCode.USER_DOES_NOT_EXIST)
    except Comment.DoesNotExist:
        return request_success(ErrorCode.COMMENT_DOES_NOT_EXIST)

    if not (has_permission(user, PERMISSION_FORUM_MANAGE_FORUM) or comment.author == user) :
        return request_success(ErrorCode.NO_PERMISSION)
    comment.delete()
    return request_success({
        "code": 0,
        "msg": "Comment deleted successfully"
    })

@check_require
def get_post_list(req: HttpRequest):
    if req.method != 'GET':
        return BAD_METHOD
    tag_list = req.GET.getlist("tag_list")
    try:
        keyword = require(req.GET, "keyword", "string")
    except KeyError:
        keyword = ""
    page, page_size = get_page_info(req.GET)
    tag_list = list(set(tag_list))
    tag_num = len(tag_list)
    query_tags = Tag.objects.filter(id__in=tag_list)
    if tag_num == 0:
        posts = Post.objects.all()
    else:
        posts = (
            Post.objects
            .annotate(
                matching_tag_count = Count('tags', filter = Q(tags__in = query_tags), distinct=True)
            )
            .filter(matching_tag_count = tag_num)
        )
    posts = posts.filter(Q(title__icontains=keyword) | Q(content__icontains=keyword)).order_by('-created_at', '-post_id')
    paginator = Paginator(posts, page_size)
    try:
        return request_success({
            "code": 0,
            "data": get_post_info_by_paginator(paginator, page)
        })
    except EmptyPage:
        return request_success(ErrorCode.PAGE_OUT_OF_RANGE)

@check_require
def search_post_by_keyword(req: HttpRequest):
    if req.method != 'GET':
        return BAD_METHOD
    keyword = require(req.GET, "keyword", "string")
    page = require(req.GET, "page", "int")
    page_size = require(req.GET, "page_size", "int")

    posts = Post.objects.filter(Q(title__icontains=keyword) | Q(content__icontains=keyword)).order_by('-created_at', '-post_id')
    paginator = Paginator(posts, page_size)
    try:
        return request_success({
            "code": 0,
            "data": get_post_info_by_paginator(paginator, page)
        })
    except EmptyPage:
        return request_success(ErrorCode.PAGE_OUT_OF_RANGE)

@check_require
def get_comment_detail_by_id(req: HttpRequest):
    if req.method != 'GET':
        return BAD_METHOD
    try:
        comment = get_comment(req.GET, "comment_id")
    except Comment.DoesNotExist:
        return request_success(ErrorCode.COMMENT_DOES_NOT_EXIST)
    return request_success({
        "code": 0,
        "data": {
            "comment_id": comment.comment_id,
            "content": comment.content,
            "created_at": comment.created_at,
            "author": comment.author.username,
            "allow_reply": comment.allow_reply,
            "object_id": comment.object_id,
            "content_type": comment.content_type.model_class().__name__,
        }
    })

@check_require
def get_post_detail_by_id(req: HttpRequest):
    if req.method != 'GET':
        return BAD_METHOD
    try:
        post = get_post(req.GET, "post_id")
    except Post.DoesNotExist:
        return request_success(ErrorCode.POST_DOES_NOT_EXIST)
    return request_success({
        "code": 0,
        "data": {
            "post_id": post.post_id,
            "title": post.title,
            "content": post.content,
            "created_at": post.created_at,
            "author": post.author.username,
        }
    })

@check_require
def create_comment_of_post(req: HttpRequest):
    if req.method != 'POST':
        return BAD_METHOD
    body = json.loads(req.body.decode("utf-8")) if req.body else {}
    try:
        user = get_user(body, "username")
    except User.DoesNotExist:
        return request_success(ErrorCode.USER_DOES_NOT_EXIST)
    if not has_permission(user, PERMISSION_FORUM_POST) :
        return request_success(ErrorCode.NO_PERMISSION)
    try:
        post = get_post(body, "post_id")
    except Post.DoesNotExist:
        return request_success(ErrorCode.POST_DOES_NOT_EXIST)

    content = require(body, "content", "string")
    Comment.objects.create(content=content, 
                           author=user, 
                           content_object=post, 
                           created_at=utils_time.get_timestamp())
    return request_success({
        "code": 0,
        "msg": "Comment created successfully"
    })

@check_require
def get_comment_list_by_post_id(req: HttpRequest):
    if req.method != 'GET':
        return BAD_METHOD
    try:
        post = get_post(req.GET, "post_id")
    except Post.DoesNotExist:
        return request_success(ErrorCode.POST_DOES_NOT_EXIST)
    page, page_size = get_page_info(req.GET)
    comments = Comment.objects.filter(content_type=ContentType.objects.get_for_model(Post),
                                      object_id=post.post_id).order_by('-created_at', '-comment_id')
    paginator = Paginator(comments, page_size)
    try:
        return request_success({
            "code": 0,
            "data": get_comment_info_by_paginator(paginator, page)
        })
    except EmptyPage:
        return request_success(ErrorCode.PAGE_OUT_OF_RANGE)

@check_require
def create_comment_of_object(req: HttpRequest):
    if req.method != 'POST':
        return BAD_METHOD
    body = json.loads(req.body.decode("utf-8")) if req.body else {}
    content_type = require(body, "content_type", "string")
    object_id = require(body, "object_id", "int")
    content = require(body, "content", "string")
    allow_reply = require(body, "allow_reply", "bool")

    try:
        user = get_user(body, "username")
    except User.DoesNotExist:
        return request_success(ErrorCode.USER_DOES_NOT_EXIST)

    if not has_permission(user, PERMISSION_FORUM_POST) :
        return request_success(ErrorCode.NO_PERMISSION)

    if content_type not in CONTENT_TYPE.keys():
        return request_success(ErrorCode.INVALID_CONTENT_TYPE)

    content_type_model = CONTENT_TYPE.get(content_type)
    try:
        content_object = content_type_model.objects.get(pk=object_id)
    except content_type_model.DoesNotExist:
        return request_success(ErrorCode.OBJECT_DOES_NOT_EXIST)

    if content_type_model == Comment and content_object.allow_reply == False:
        return request_success({
            "code": 1033,
            "msg": "Object does not allow reply"
        })
    Comment.objects.create(content=content, 
                           author=user, 
                           content_object=content_object, 
                           created_at=utils_time.get_timestamp(),
                           allow_reply=allow_reply)
    return request_success({
        "code": 0,
        "msg": "Comment created successfully"
    })

@check_require
def get_comment_list_of_object(req: HttpRequest):
    if req.method != 'GET':
        return BAD_METHOD
    content_type = require(req.GET, "content_type", "string")
    object_id = require(req.GET, "object_id", "int")

    page, page_size = get_page_info(req.GET)

    if content_type not in CONTENT_TYPE.keys():
        return request_success(ErrorCode.INVALID_CONTENT_TYPE)
    content_type_model = CONTENT_TYPE.get(content_type)
    try:
        content_type_model.objects.get(pk=object_id)
    except content_type_model.DoesNotExist:
        return request_success(ErrorCode.OBJECT_DOES_NOT_EXIST)
    comments = Comment.objects.filter(content_type=ContentType.objects.get_for_model(content_type_model),
                                      object_id=object_id).order_by('-created_at', '-comment_id')
    paginator = Paginator(comments, page_size)
    try:
        return request_success({
            "code": 0,
            "data": get_comment_info_by_paginator(paginator, page)
        })
    except EmptyPage:
        return request_success(ErrorCode.PAGE_OUT_OF_RANGE)

def get_reply_list_of_comment(req: HttpRequest):
    if req.method != 'GET':
        return BAD_METHOD

    try:
        comment = get_comment(req.GET, "comment_id")
    except Comment.DoesNotExist:
        return request_success(ErrorCode.COMMENT_DOES_NOT_EXIST)

    reply_list = get_reply_list_by_dfs(comment)
    return request_success({
        "code": 0,
        "data": reply_list
    })

def create_report(req: HttpRequest):
    if req.method != 'POST':
        return BAD_METHOD
    body = json.loads(req.body.decode("utf-8")) if req.body else {}
    try:
        user = get_user(body, "reporter")
    except User.DoesNotExist:
        return request_success(ErrorCode.USER_DOES_NOT_EXIST)

    reason = require(body, "reason", "string")
    content_type = require(body, "content_type", "string")
    object_id = require(body, "object_id", "int")

    if content_type not in ["Post", "Comment"]:
        return request_success(ErrorCode.INVALID_CONTENT_TYPE)

    content_type_model = CONTENT_TYPE.get(content_type)
    try:
        content_object = content_type_model.objects.get(pk=object_id)
    except content_type_model.DoesNotExist:
        return request_success(ErrorCode.OBJECT_DOES_NOT_EXIST)

    Report.objects.create(reporter=user,
                          reported_user=content_object.author,
                          reported_content=content_object.content,
                          content_object=content_object,
                          reason=reason,
                          created_at=utils_time.get_timestamp())
    return request_success({
        "code": 0,
        "msg": "Report created successfully"
    })
    
def modify_report_solved_state(req: HttpRequest):
    if req.method != 'POST':
        return BAD_METHOD
    body = json.loads(req.body.decode("utf-8")) if req.body else {}

    try:
        user = get_user(body, "username")
    except User.DoesNotExist:
        return request_success(ErrorCode.USER_DOES_NOT_EXIST)

    report_id = require(body, "report_id", "int")
    solved_state = require(body, "solved_state", "bool")
    if not has_permission(user, PERMISSION_FORUM_MANAGE_FORUM):
        return request_success(ErrorCode.NO_PERMISSION)
    try:
        report = Report.objects.get(report_id=report_id)
    except Report.DoesNotExist:
        return request_success(ErrorCode.REPORT_DOES_NOT_EXIST)
    report.solved = solved_state
    report.save()
    return request_success({
        "code": 0,
        "msg": "Report solved state modified successfully"
    })

def get_report_list(req: HttpRequest):
    if req.method != 'GET':
        return BAD_METHOD
    try:
        solved_state = require(req.GET, "solved_state", "bool")
    except KeyError:
        solved_state = None
    page, page_size = get_page_info(req.GET)
    if solved_state is not None:
        reports = Report.objects.filter(solved=solved_state).order_by('-created_at', '-report_id')
    else:
        reports = Report.objects.all().order_by('-created_at', '-report_id')
    paginator = Paginator(reports, page_size)
    try:
        page_obj = paginator.page(page)
    except EmptyPage:
        return request_success(ErrorCode.PAGE_OUT_OF_RANGE)
    data = []
    for report in page_obj:
        content_type_model = report.content_type.model_class()
        object_deleted = False
        user_banned = False
        try:
            content_type_model.objects.get(pk=report.object_id)
        except content_type_model.DoesNotExist:
            object_deleted = True
        try: 
            UserPermission.objects.get(user=report.reported_user, permission=PERMISSION_FORUM_POST)
        except UserPermission.DoesNotExist:
            user_banned = True
        data.append({
            "report_id": report.report_id,
            "reporter": report.reporter.username,
            "content_type": report.content_type.model_class().__name__,
            "object_id": report.object_id,
            "reason": report.reason,
            "created_at": report.created_at,
            "solved": report.solved,
            "preview": {
                "author": report.reported_user.username,
                "content": report.reported_content
            },
            "object_deleted": object_deleted,
            "user_banned": user_banned
        })
    return request_success({
        "code": 0,
        "data": {
            "reports": data,
            "total_pages": paginator.num_pages,
            "total_reports": paginator.count
        }
    })

def delete_reported_object(req: HttpRequest):
    if req.method != 'POST':
        return BAD_METHOD
    body = json.loads(req.body.decode("utf-8")) if req.body else {}
    try:
        user = get_user(body, "username")
    except User.DoesNotExist:
        return request_success(ErrorCode.USER_DOES_NOT_EXIST)
    if not has_permission(user, PERMISSION_FORUM_MANAGE_FORUM):
        return request_success(ErrorCode.NO_PERMISSION)
    
    try:
        report = get_report(body, "report_id")
    except Report.DoesNotExist:
        return request_success(ErrorCode.REPORT_DOES_NOT_EXIST)

    content_type_model = report.content_type.model_class()
    try: 
        content_object = content_type_model.objects.get(pk=report.object_id)
    except content_type_model.DoesNotExist:
        return request_success({
            "code": 1032,
            "msg": "Object already deleted"
        })
    content_object.delete()
    return request_success({
        "code": 0,
        "msg": "Reported object deleted successfully"
    })

def ban_reported_user(req: HttpRequest):
    if req.method != 'POST':
        return BAD_METHOD
    body = json.loads(req.body.decode("utf-8")) if req.body else {}

    try:
        user = get_user(body, "username")
        report = get_report(body, "report_id")
    except User.DoesNotExist:
        return request_success(ErrorCode.USER_DOES_NOT_EXIST)
    except Report.DoesNotExist:
        return request_success(ErrorCode.REPORT_DOES_NOT_EXIST)

    result = remove_permission(user, report.reported_user, PERMISSION_FORUM_POST)
    return request_success(result)