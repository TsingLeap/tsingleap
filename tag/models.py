from django.db import models

class TagType(models.TextChoices):
    SPORTS = "sports", "运动"
    DEPARTMENT = "department", "院系"
    EVENT = "event", "赛事"
    HIGHLIGHT = "highlight", "精华帖"
    DEFAULT = "default", "默认"
    

class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32)
    tag_type = models.CharField(max_length=32, choices=TagType.choices, default=TagType.DEFAULT)

    is_post_tag = models.BooleanField()
    is_competition_tag = models.BooleanField()

    def __str__(self):
        return f"{self.name} - {self.get_tag_type_display()}"
