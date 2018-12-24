from django.db import models
from django.contrib.auth.models import  AbstractUser,UserManager
# Create your models here.
class User(AbstractUser):
    class Meta:
        app_label = 'get_backend'

    def __str__(self):
        return self.nickname if self.nickname else self.username

    nickname = models.CharField(max_length=64)
    address = models.CharField(max_length=128)
    wechat_session=models.CharField(max_length=32)

class Activity(models.Model):
    class Meta:
        app_label = 'get_backend'

    content = models.CharField(max_length=128)
    address = models.CharField(max_length=128)
    create_time = models.TimeField(auto_now_add=True)
    recent_time = models.TimeField(auto_now=True)
    score = models.FloatField()
    organizer = models.ForeignKey("User", on_delete=models.CASCADE)
    signed_users = models.ManyToManyField("User", related_name="signed_users")


class Review(models.Model):
    class Meta:
        app_label = 'get_backend'

    content = models.CharField(max_length=128)
    reviewer = models.ForeignKey("User", on_delete=models.CASCADE)
    score = models.FloatField()
