from django.http import JsonResponse
from django.conf import settings
from django.contrib import auth
from django.db.models import Q
import requests
import json
import datetime
from .models import *
from Agile_BackEnd import settings

# coding:utf-8

# Create your views here.
def get_wechat_secret_key():
    #密码需要保密，因此用文件保存。注意不要上传github
    if not settings.WECHAT_SECRET_KEY:
        #print("no settings key")
        with open('./secretkey.txt', 'r') as f:
            #print("read success")
            settings.WECHAT_SECRET_KEY=f.readline().replace('\r','').replace('\n','')
    return settings.WECHAT_SECRET_KEY

def wechat_login(request, code):
    payload = {'appid': 'wxc80e543e8b92e71f',
               'secret': get_wechat_secret_key(), # 4da***57
               'js_code': code,
               'grant_type': 'authorization_code',
              }
    print("payload success")
    r = requests.get("https://api.weixin.qq.com/sns/jscode2session", params=payload)
    print("session success")
    # r.text={"session_key":"xWm0r4af3WN79vz00d0Ipg==","openid":"oxGBW4-Q6UXupqZJbL8HTbgPEYmY"}
    res = json.loads(r.text)
    print(res)
    allres = {
        "status": True,
        "code": 200,
        "reason": '',
        "param": {}
    }
    if "errmsg" not in res:
        print("not err")
        user = User.objects.filter(id=res["openid"])
        print("get user")
        if not user.exists():
            print("create user")
            user = User.objects.create_user(username=res["openid"],password=res["openid"],email="{}@wechat.com".format(res["openid"]), id=res["openid"], session_key=res["session_key"])
            user.save()
        # auth只能用用户密码登陆，因此如果既有用户密码又有小程序的话，就需要重新设计密码，
        # 使用普通密码/微信id/oathid获取真实密码，再用auth(用户名，真实密码)登陆
        user = auth.authenticate(username=res["openid"], password=res["openid"])
        if user is not None:
            print("login")
            auth.login(request,user)
            print(user.id)
            allres["param"] = res
            return JsonResponse(dict(allres))
        else:
            allres["status"]=False
            allres["code"]=400
            allres["reason"]="Wrong username or password"
            return JsonResponse(dict(allres))
    else:
        allres["status"] = False
        allres["code"] = 400
        allres["reason"] = res["errmsg"]
        return JsonResponse(dict(allres))

def getActivities(request, pageNo, pageSize):
    activities=Activity.objects.order_by("create_Date")
    param=[]
    count=0
    pn=int(pageNo)
    ps=int(pageSize)
    if pn<=0 or ps<=0:
        return JsonResponse({
            "status": False,
            "code": 400,
            "reason": 'Wrong page number or page size',
            "param": ''
        })
    for a in activities:
        if((pn-1)*ps)<=count<(pn*ps):
            #先看下时间对不对
            now = datetime.datetime.now()
            delta = now.replace(tzinfo=None) - a.end_time.replace(tzinfo=None)
            if delta.total_seconds() > 0 :
                a.status = False
                a.save()
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
    picture=json.loads(request.body)["picture"]
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
    owner=User.objects.get(id=uid)
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
        now = datetime.datetime.now()
        delta = now.replace(tzinfo=None) - a.end_time.replace(tzinfo=None)
        if delta.total_seconds() > 0:
            a.status = False
            a.save()
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
    # TODO bg选取,目前直接返回了一张无关的
    res = {
        "status": True,
        "code": 200,
        "reason": '',
        "param": activity.to_one_dict()
    }
    return JsonResponse(dict(res))

def attendActivity(request, uid, aid):
    res = {
        "status": True,
        "code": 200,
        "reason": '',
        "param": None
    }
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
        res["status"]=False
        res["code"]=400
        res["reason"]="You have attended."
    return JsonResponse(dict(res))

def cancelActivity(request, uid, aid):
    res = {
        "status": True,
        "code": 200,
        "reason": '',
        "param": None
    }
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
        res["status"]=False
        res["code"]=400
        res["reason"]="You have not attended."
    return JsonResponse(dict(res))

def getUserOpenActivities(request, uid):
    param=[]
    user = User.objects.get(id=uid)
    print("Get the user")
    activities = Activity.objects.filter(organizer = user)
    print("Get the activities")
    for a in activities:
        param.append(a.to_dict())
    res = {
        "status": True,
        "code": 200,
        "reason": '',
        "param": param
    }
    return JsonResponse(dict(res))

def getUserAttendActivities(request, uid):
    param = []
    activities = Activity.objects.all()
    print("Get the activities")
    for a in activities:
        print(type(a))
        isAttend = a.members.filter(id = uid)
        if isAttend.exists():
            param.append(a.to_dict())
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
    if not activity.organizer.id == owner.id:
        return JsonResponse(res = {
            "status": False,
            "code": 400,
            "reason": 'Wrong organizer',
            "param": None
        })
    isAttend = activity.signed_members.filter(id=mid)
    print('has Signed')
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
    else :
        res = {
            "status": False,
            "code": 400,
            "reason": 'You have signed',
            "param": activity.sign_dict()
        }
    return JsonResponse(dict(res))