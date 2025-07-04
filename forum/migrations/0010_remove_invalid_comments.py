# Generated by Django 5.1.7 on 2025-04-26 14:58

from django.db import migrations

def delete_orphan_comments(apps, schema_editor):
    Comment = apps.get_model('forum', 'Comment')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    to_delete_ids = set()

    def collect_comment_and_children(comment):
        """递归收集子评论"""
        comment_content_type = ContentType.objects.get_for_model(Comment)
        children = Comment.objects.filter(content_type=comment_content_type, object_id=comment.comment_id)
        for child in children:
            collect_comment_and_children(child)
        to_delete_ids.add(comment.pk)

    comments = Comment.objects.all()

    for comment in comments:
        content_type_obj = comment.content_type

        # ⚡ 用 apps.get_model 拿到对应的模型
        model_class = apps.get_model(content_type_obj.app_label, content_type_obj.model)

        if not model_class.objects.filter(pk=comment.object_id).exists():
            # 找到孤立评论，收集自己和子评论
            collect_comment_and_children(comment)

    if to_delete_ids:
        Comment.objects.filter(pk__in=to_delete_ids).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0009_remove_comment_post'),
    ]

    operations = [
        migrations.RunPython(delete_orphan_comments),
    ]