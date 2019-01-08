from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.contrib import auth
from django.db.models import Q
import requests
import json
import datetime,time
from .models import *
# coding:utf-8
from django.http import HttpResponse

# Create your views here.
def get_wechat_secret_key():
    if not settings.WECHAT_SECRET_KEY:
        with open('./secretkey.txt', 'r') as f:
            settings.WECHAT_SECRET_KEY=f.readline().replace('\r','').replace('\n','')
    return settings.WECHAT_SECRET_KEY

def wechat_login(request, body):
    payload = {'appid': 'wx8c53cbd60fbb55bc',
               'secret': get_wechat_secret_key(), # 4da***57
               'js_code': body["code"],
               'grant_type': 'authorization_code',
              }
    r = requests.get("https://api.weixin.qq.com/sns/jscode2session", params=payload)
    # r.text={"session_key":"xWm0r4af3WN79vz00d0Ipg==","openid":"oxGBW4-Q6UXupqZJbL8HTbgPEYmY"}
    res = json.loads(r.text)
    if "errmsg" not in res:
        user = User.objects.filter(openid=res["openid"])

        if not User.objects.filter(openid=res["openid"]).exists():
            #TODO
            user = User.objects.create_user(username=res["openid"],password=res["openid"],email="{}@wechat.com".format(res["openid"]), openid=res["openid"])
            user.save()
        # auth只能用用户密码登陆，因此如果既有用户密码又有小程序的话，就需要重新设计密码，
        # 使用普通密码/微信id/oathid获取真实密码，再用auth(用户名，真实密码)登陆
        user = auth.authenticate(username=res["openid"], password=res["openid"])
        if user is not None:
            auth.login(request,user)
            print(user.id)
            return {"uid": user.id}, 200
        else:
            return "Wrong username or password", 400
    else:
        return res["errmsg"],400

def getActivities(request, pageNo, pageSize):
    activities=Activity.objects.order_by("create_Date")
    param=[]
    count=0
    pn=int(pageNo)
    ps=int(pageSize)
    for a in activities:
        if((pn-1)*ps)<=count<(pn*ps):
            param.append(a.to_dict())
        count+=1
    res = {
        "status": True,
        "code": 200,
        "reason": '',
        "param": param
    }
    return JsonResponse(dict(res))

def addPicture(request, uid):
    #TODO
    picture=json.loads(request.body)["body"]["picture"]
    picture_url='https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1546847744370&di=f0d19b4627305300f5a9f14d926f2bbc&imgtype=0&src=http%3A%2F%2F5b0988e595225.cdn.sohucs.com%2Fimages%2F20181118%2Fa15713566c0f43c38abb84f9481f99f0.jpeg'
    res= {
        "status": True,
        "code": 200,
        "reason": '',
        "param": picture_url
    }
    return JsonResponse(dict(res))

def addActivity(request, uid):
    #Activity处理
    owner=User.objects.get(id=json.loads(request.body)["ownerId"])
    activity=Activity(status=True,
                      address=json.loads(request.body)["address"],
                      title=json.loads(request.body)["title"],
                      detail=json.loads(request.body)["detail"],
                      start_time=datetime.datetime.strptime(json.loads(request.body)["start"],"%Y-%m-%d %H:%M:%S"),
                      end_time=datetime.datetime.strptime(json.loads(request.body)["end"],"%Y-%m-%d %H:%M:%S"),
                      maxMemberNum=json.loads(request.body)["maxMembers"],
                      organizer=owner
    )
    activity.save()
    # Picture处理
    imgs = json.loads(request.body)["imgs"]
    for p in imgs:
        picture=Picture(
                activity=activity,
                address=imgs[p]
        )
        picture.save()
    res={
        "status": True,
        "code": 200,
        "reason": '',
        "param": activity.id
    }
    return JsonResponse(dict(res))

def search(response, keyword):
    activities = Activity.objects.filter(Q(title__contains=keyword)
                                         |Q(address__contains=keyword)
                                         |Q(detail__contains=keyword))
    param = []
    for a in activities:
        param.append(a.to_dict())
    res = {
        "status": True,
        "code": 200,
        "reason": '',
        "param": param
    }
    return JsonResponse(dict(res))

def getOneActivity(request,aid):
    activity=Activity.objects.get(id=aid)
    res = {
        "status": True,
        "code": 200,
        "reason": '',
        "param": activity.to_one_dict()
    }
    return JsonResponse(dict(res))

def attendActivity(request, uid, aid):
    activity = Activity.objects.get(id=aid)
    isAttend = activity.members.filter(id=uid)
    print('getIsAttend')
    attender = User.objects.get(id=uid)
    if not isAttend.exists():
        print('isAttendNotExists')
        activity.members.add(attender)
        print('addSuccess')
    else:
        print('hasAttend')
    res = {
        "status": True,
        "code": 200,
        "reason": '',
        "param": None
    }
    return JsonResponse(dict(res))

def cancelActivity(request, uid, aid):
    activity = Activity.objects.get(id=aid)
    isAttend = activity.members.filter(id=uid)
    print('getIsAttend')
    attender = User.objects.get(id=uid)
    if isAttend.exists():
        print('isAttendNotExists')
        activity.members.remove(attender)
        print('deleteSuccess')
    else:
        print('notAttend')
    res = {
        "status": True,
        "code": 200,
        "reason": '',
        "param": None
    }
    return JsonResponse(dict(res))

def getUserOpenActivities(request, uid):
    param=[]
    user = User.objects.get(id=uid)
    activities = Activity.objects.filter(organizer=user)
    for a in activities:
        param.append(a.to_dict)
    res = {
        "status": True,
        "code": 200,
        "reason": '',
        "param": param
    }
    return JsonResponse(dict(res))

def getUserAttendActivities(request, uid):
    def getUserOpenActivities(request, uid):
        param = []
        activities = Activity.objects.all()
        for a in activities:
            members=a.members
            isAttend=members.filter(id=uid)
            if isAttend.exists():
                param.append(a.to_dict)
        res = {
            "status": True,
            "code": 200,
            "reason": '',
            "param": param
        }
        return JsonResponse(dict(res))

def sign(request, aid, uid, mid):
    activity = Activity.objects.get(id=aid)
    owner = User.objects.get(id=uid)
    member = User.objects.get(id=mid)
    #TODO 判断owner是否正确
    isAttend = activity.signed_members.filter(id=mid)
    print('getIsSigned')
    if not isAttend.exists():
        print('sign')
        activity.signed_members.add(member)
        print('signSuccess')
    res = {
        "status": True,
        "code": 200,
        "reason": '',
        "param": activity.sign_dict()
    }
    return JsonResponse(dict(res))