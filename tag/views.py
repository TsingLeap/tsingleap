import json, jinja2
from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpRequest, HttpResponse

from users.models import User
from tag.models import Tag, TagType
from forum.models import Post, Comment
from competitions.models import Competition
from django.contrib.contenttypes.models import ContentType
from utils.utils_request import BAD_METHOD, request_failed, request_success, return_field
from utils.utils_require import check_require, require
from django.core.paginator import Paginator, EmptyPage
from utils import utils_time
from utils.utils_permission import has_permission, PERMISSION_TAG_MANAGE_TAG

tag_type_map = {
    "sports": TagType.SPORTS,
    "department": TagType.DEPARTMENT,
    "event": TagType.EVENT,
    "highlight": TagType.HIGHLIGHT,
    "default": TagType.DEFAULT,
}

@check_require
def create_tag(req: HttpRequest):
    if req.method != 'POST':
        return BAD_METHOD
    body = json.loads(req.body.decode("utf-8")) if req.body else {}
    username = require(body, "username", "string")
    name = require(body, "name", "string")
    tag_type = require(body, "tag_type", "string")
    is_post_tag = require(body, "is_post_tag", "bool")
    is_competition_tag = require(body, "is_competition_tag", "bool")
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return request_success({
            "code": 1021,
            "msg": "User does not exist"
        })
    try:
        tag_type = tag_type_map[tag_type]
    except KeyError:
        return request_success({
            "code": 1040,
            "msg": "Invalid tag type"
        })
    if not has_permission(user, PERMISSION_TAG_MANAGE_TAG):
        return request_success({
            "code": 1020,
            "msg": "No permission"
        })
    if Tag.objects.filter(name=name, tag_type=tag_type).exists():
        return request_success({
            "code": 1041,
            "msg": "Tag already exists"
        })
    tag = Tag.objects.create(
        name=name,
        tag_type=tag_type,
        is_post_tag=is_post_tag,
        is_competition_tag=is_competition_tag
    )
    return request_success({
        "code": 0,
        "msg": "Tag created successfully",
        "data": {
            "id": tag.id,
            "name": tag.name,
            "tag_type": tag.tag_type,
            "is_post_tag": tag.is_post_tag,
            "is_competition_tag": tag.is_competition_tag
        }
    })
    
@check_require
def delete_tag(req: HttpRequest):
    if req.method != 'POST':
        return BAD_METHOD
    body = json.loads(req.body.decode("utf-8")) if req.body else {}
    username = require(body, "username", "string")
    tag_id = require(body, "tag_id", "int")
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return request_success({
            "code": 1021,
            "msg": "User does not exist"
        })
    try:
        tag = Tag.objects.get(id=tag_id)
    except Tag.DoesNotExist:
        return request_success({
            "code": 1042,
            "msg": "Tag does not exist"
        })
    if not has_permission(user, PERMISSION_TAG_MANAGE_TAG):
        return request_success({
            "code": 1020,
            "msg": "No permission"
        })
    tag.delete()
    return request_success({
        "code": 0,
        "msg": "Tag deleted successfully"
    })

@check_require
def get_tag_list(req: HttpRequest):
    if req.method != 'GET':
        return BAD_METHOD
    tags = Tag.objects.all()
    return request_success({
        "code": 0,
        "msg": "Tag list fetched successfully",
        "data": [
            {
                "id": tag.id,
                "name": tag.name,
                "tag_type": tag.tag_type,
                "is_post_tag": tag.is_post_tag,
                "is_competition_tag": tag.is_competition_tag
            }
            for tag in tags
        ]
    })

@check_require
def search_tag_by_prefix(req: HttpRequest):
    if req.method != 'GET':
        return BAD_METHOD
    prefix = require(req.GET, "prefix", "string")
    tag_type = require(req.GET, "tag_type", "string")
    if tag_type not in tag_type_map.keys():
        tags = Tag.objects.filter(name__startswith=prefix)
    else:
        tags = Tag.objects.filter(name__startswith=prefix, tag_type=tag_type_map[tag_type])
    return request_success({
        "code": 0,
        "msg": "Tag list fetched successfully",
        "data": [
            {
                "id": tag.id,
                "name": tag.name,
                "tag_type": tag.tag_type,
                "is_post_tag": tag.is_post_tag,
                "is_competition_tag": tag.is_competition_tag
            }
            for tag in tags
        ]
    })

@check_require
def get_post_list_by_tag(req: HttpRequest):
    if req.method != 'GET':
        return BAD_METHOD
    tag_id = require(req.GET, "tag_id", "int")
    page = require(req.GET, "page", "int")
    page_size = require(req.GET, "page_size", "int")
    try:
        tag = Tag.objects.get(id=tag_id)
    except Tag.DoesNotExist:
        return request_success({
            "code": 1042,
            "msg": "Tag does not exist"
        })
    posts = Post.objects.filter(tags=tag).order_by('-created_at', '-post_id')
    paginator = Paginator(posts, page_size)
    try:
        page_obj = paginator.page(page)
    except EmptyPage:
        return request_success({
            "code": 1023,
            "msg": "Page out of range"
        })
    return request_success({
        "code": 0,
        "msg": "Post list fetched successfully",
        "data": {
            "posts": [
                {
                    "id": post.post_id,
                    "title": post.title,
                    "content": post.content,
                    "author": post.author.username,
                    "created_at": post.created_at,
                }
                for post in page_obj
            ],
            "total_pages": paginator.num_pages,
            "total_posts": paginator.count
        }
    })