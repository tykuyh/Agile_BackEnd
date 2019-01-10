from django.db import models
from django.contrib.auth.models import  AbstractUser,UserManager

# Create your models here.
class User(AbstractUser):
    class Meta:
        app_label = 'get_backend'

    def __str__(self):
        return self.nickname if self.nickname else self.username

    def to_dict(self):
        return dict(
            openid=self.id,
            nickname=self.nickname,
            face=self.face,
        )
    id = models.CharField(max_length=64, primary_key=True)
    session_key = models.CharField(max_length=32)
    nickname = models.CharField(max_length=64)
    face = models.CharField(max_length=128)
    #organized_activities = models.ManyToManyField("Activity", related_name="organized_activities")
    #attend_activities = models.ManyToManyField("Activity", related_name="attend_activities")

class Picture(models.Model):
    class Meta:
        app_label = 'get_backend'
    address = models.CharField(max_length=128)
    activity = models.ForeignKey("Activity", on_delete=models.CASCADE)

class Activity(models.Model):
    class Meta:
        app_label = 'get_backend'

    def to_dict(self):
        members = self.members.count()
        #TODO bg选取
        picture_url = 'https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1546847744370&di=f0d19b4627305300f5a9f14d926f2bbc&imgtype=0&src=http%3A%2F%2F5b0988e595225.cdn.sohucs.com%2Fimages%2F20181118%2Fa15713566c0f43c38abb84f9481f99f0.jpeg'
        return dict(
            id=self.id,
            bg=picture_url,
            status=self.status,
            address=self.address,
            title=self.title,
            detail=self.detail,
            start=self.start_time,
            end=self.end_time,
            createDate=self.create_Date,
            members=members,
            ownerId=self.organizer.id,
        )
    def to_one_dict(self):
        owner = self.organizer.to_dict()
        members = []
        for m in self.members.all():
            members.append(m.to_dict())
        picture_url = ['https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1546847744370&di=f0d19b4627305300f5a9f14d926f2bbc&imgtype=0&src=http%3A%2F%2F5b0988e595225.cdn.sohucs.com%2Fimages%2F20181118%2Fa15713566c0f43c38abb84f9481f99f0.jpeg']
        return dict(
            id=self.id,
            bg=picture_url,
            status=self.status,
            address=self.address,
            title=self.title,
            detail=self.detail,
            start=self.start_time,
            end=self.end_time,
            createDate=self.create_Date,
            owner=owner,
            members=members
        )
    def sign_dict(self):
        members = []
        for m in self.signed_members.all():
            members.append(m.to_dict())
        return dict(
            members = members
        )
    status = models.BooleanField()
    address = models.CharField(max_length=128)
    title = models.CharField(max_length=32)
    detail = models.CharField(max_length=128)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    create_Date = models.DateTimeField(auto_now=True)
    score = models.FloatField(default=5)
    organizer = models.ForeignKey("User", on_delete=models.CASCADE)
    members = models.ManyToManyField("User", related_name="users")
    signed_members = models.ManyToManyField("User", related_name="signed_users")
    maxMemberNum = models.IntegerField(default=30)

class Review(models.Model):
    class Meta:
        app_label = 'get_backend'

    content = models.CharField(max_length=128)
    reviewer = models.ForeignKey("User", on_delete=models.CASCADE)
    score = models.FloatField()
