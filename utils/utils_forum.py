from forum.models import Comment
from django.contrib.contenttypes.models import ContentType
from utils.utils_params import get_user, get_post, require
from utils.utils_require import ErrorCode
from utils.utils_request import request_success
from tag.models import Tag
from users.models import User
from forum.models import Post

def get_reply_list_by_dfs(comment: Comment) -> list[Comment]:
    def comment_to_dict(comment: Comment) -> dict:
        return {
            "comment_id": comment.comment_id,
            "content": comment.content,
            "created_at": comment.created_at,
            "author": comment.author.username,
            "father_object_id": comment.object_id
        }
    reply_list = [comment_to_dict(comment)]
    reply_of_comment = Comment.objects.filter(content_type=ContentType.objects.get_for_model(Comment),
                                              object_id=comment.comment_id)
    for r in reply_of_comment:
        reply_list.extend(get_reply_list_by_dfs(r))

    reply_list = sorted(reply_list, key=lambda x: x["created_at"])

    return reply_list

def get_post_info_by_paginator(paginator, page) :
    page_obj = paginator.page(page)
    return {
        "posts": [{
            "post_id": post.post_id,
            "title": post.title,
            "content": post.content,
            "created_at": post.created_at,
            "author": post.author.username,
        } for post in page_obj],
        "total_pages": paginator.num_pages,
        "total_posts": paginator.count
    }

def get_comment_info_by_paginator(paginator, page) :
    page_obj = paginator.page(page)
    return {
        "comments": [{
            "comment_id": comment.comment_id,
            "content": comment.content,
            "created_at": comment.created_at,
            "author": comment.author.username,
        } for comment in page_obj],
        "total_pages": paginator.num_pages,
        "total_comments": paginator.count
    }

def get_user_post_tag_from_body(body) :
    try:
        user = get_user(body, "username")
        post = get_post(body, "post_id")
    except User.DoesNotExist:
        return None, None, None, ErrorCode.USER_DOES_NOT_EXIST
    except Post.DoesNotExist:
        return None, None, None, ErrorCode.POST_DOES_NOT_EXIST

    tag_id = require(body, "tag_id", "int")
    try:
        tag = Tag.objects.get(id=tag_id)
    except Tag.DoesNotExist:
        return None, None, None, {
            "code": 1046,
            "msg": f"Invalid tag id: {tag_id}"
        }
    
    return user, post, tag, None