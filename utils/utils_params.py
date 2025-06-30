from utils.utils_require import require

from users.models import User
from forum.models import Post, Comment, Report
from tag.models import Tag

def get_user(body, key, return_username=False):
    username = require(body, key, "string")
    user = User.objects.get(username=username)
    if return_username:
        return user, username
    else:
        return user

def get_post(body, key, return_post_id=False):
    post_id = require(body, key, "int")
    post = Post.objects.get(pk=post_id)
    if return_post_id:
        return post, post_id
    else:
        return post

def get_comment(body, key, return_comment_id=False):
    comment_id = require(body, key, "int")
    comment = Comment.objects.get(pk=comment_id)
    if return_comment_id:
        return comment, comment_id
    else:
        return comment

def get_report(body, key, return_report_id=False):
    report_id = require(body, key, "int")
    report = Report.objects.get(pk=report_id)
    if return_report_id:
        return report, report_id
    else:
        return report
    
def get_tag(body, key, return_tag_id=False):
    tag_id = require(body, key, "int")
    tag = Tag.objects.get(pk=tag_id)
    if return_tag_id:
        return tag, tag_id
    else:
        return tag
    
def get_page_info(body):
    page = require(body, "page", "int")
    page_size = require(body, "page_size", "int")
    return page, page_size