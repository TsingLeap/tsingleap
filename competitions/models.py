from django.db import models
from django.utils import timezone
from utils.utils_require import MAX_CHAR_LENGTH
from users.models import User
from tag.models import Tag

# Create your models here.

class Participant(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=MAX_CHAR_LENGTH)
    score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} - {self.score}"
        
class Competition(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length = MAX_CHAR_LENGTH)
    sport = models.CharField(max_length = MAX_CHAR_LENGTH)
    participants = models.ManyToManyField(Participant, related_name="competition", blank=True)
    is_finished = models.BooleanField(default=False)
    time_begin = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag, related_name="competition", blank=True)

    def __str__(self):
        return f"{self.name} - {self.sport} ({self.time_begin})"
    
class Focus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.competition.name}"

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.participant.name}"