from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from forum.models import Comment, Post
from competitions.models import Competition

def delete_related_comments(content_type, object_id):
    """
    递归删除所有指向指定对象的评论
    """
    children = Comment.objects.filter(content_type=content_type, object_id=object_id)
    for child in children:
        # 递归删除 child 的子评论
        delete_related_comments(ContentType.objects.get_for_model(Comment), child.comment_id)
        # 删除 child 自己
        child.delete()

@receiver(post_delete, sender=Comment)
def delete_children_comments(sender, instance, **kwargs):
    """
    每当一个 Comment 被删除时，递归删除它的所有子评论
    """
    content_type = ContentType.objects.get_for_model(Comment)
    delete_related_comments(content_type, instance.comment_id)

@receiver(post_delete, sender=Post)
def delete_comments_for_post(sender, instance, **kwargs):
    """
    当 Post 被删除时，递归删除它所有的评论及子评论。
    """
    content_type = ContentType.objects.get_for_model(Post)
    delete_related_comments(content_type, instance.pk)

@receiver(post_delete, sender=Competition)
def delete_comments_for_competition(sender, instance, **kwargs):
    """
    当 Competition 被删除时，递归删除它所有的评论及子评论。
    """
    content_type = ContentType.objects.get_for_model(Competition)
    delete_related_comments(content_type, instance.pk)

@receiver(post_delete, sender=Comment)
def delete_comments_for_comment(sender, instance, **kwargs):
    """
    当 Comment 被删除时，递归删除它所有的子评论。
    """
    content_type = ContentType.objects.get_for_model(Comment)
    delete_related_comments(content_type, instance.comment_id)