from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Users,UserInfos
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from django.db.models import Q 
import json 

fee_hafhour=5 #费用5元/半小时

#************************************************渲染相关函数****************************************
def index(request):
    if request.method == 'POST':
        tempname = request.POST['name']
        password =  request.POST['password']
        usertype=int((request.POST['usertype']))
        # 查询用户是否在数据库中
        print("%s,%s,%d"%(tempname,password,usertype))
        if Users.objects.filter(name=tempname).exists():
            user=Users.objects.get(name=tempname)

            if user.password==password and int(user.usertype)==usertype:
                if request.session.get("is_login")=='true' and request.COOKIES.get('name')==tempname:
                    return HttpResponseRedirect(reverse('home'))
                else:
                    request.session['is_login'] = 'true'
                    request.session['name'] = 'name',
                    if user.usertype==1:
                        onlineuserinfo_list = UserInfos.objects.filter(state=1).order_by('-logintime')
                        offlineuserinfo_list = UserInfos.objects.filter(~Q(state=1)).order_by('-lastlogouttime')
                        context = {'onlineuserinfo_list': onlineuserinfo_list,'offlineuserinfo_list': offlineuserinfo_list}
                        response=render(request, 'homepage_a.html',context)#跳到管理员首页界面
                    else:
                        userinfo = UserInfos.objects.get(user = user)
                        if userinfo.state==3:
                            messages.add_message(request,messages.ERROR,'距离你上次长时间上网还不到2个小时，请再休息一会')
                            return render(request, 'index.html')
                        else:
                            userinfo.state=1
                            userinfo.logintime=datetime.now()
                            userinfo.onlinetime=0
                            userinfo.onlinetimestr="不到1分钟"
                            userinfo.fee=fee_hafhour
                            userinfo.save()
                            context = {'userinfo': userinfo}
                            response=render(request, 'homepage.html',context)#跳到顾客首页界面
                #set cookie
                trans_uname = user.name.encode('utf-8').decode('latin-1')#转一下解决cooki不能设置中文的问题
                response.set_cookie('name', trans_uname)
                return response
            else:
                messages.add_message(request,messages.ERROR,'用户密码或身份类型错误')
                return render(request, 'index.html')
        else:
            messages.add_message(request,messages.ERROR,'用户不存在')
            return render(request, 'index.html')
    return render(request, 'index.html')

def home(request):#去首页
    cook = request.COOKIES.get('name')
    if cook == None:
        return  render(request, 'index.html')
    else:
       trans_cook=cook.encode('latin-1').decode('utf-8')
    user = Users.objects.get(name = trans_cook)
    if user.usertype == 0:
        userinfo = UserInfos.objects.get(user = user)
        context = {'userinfo': userinfo}
        return render(request, 'homepage.html',context)
    elif user.usertype == 1:
        onlineuserinfo_list = UserInfos.objects.filter(state=1).order_by('-logintime')
        offlineuserinfo_list = UserInfos.objects.filter(~Q(state=1)).order_by('-lastlogouttime')
        context = {'onlineuserinfo_list': onlineuserinfo_list,'offlineuserinfo_list': offlineuserinfo_list}
        return render(request, 'homepage_a.html',context)


def onlineuser(request):#显示在线用户
    cook = request.COOKIES.get('name')
    if cook == None:
        return  render(request, 'index.html')
    else:
        trans_cook=cook.encode('latin-1').decode('utf-8')
    print('cook:',  trans_cook)
    user = Users.objects.get(name = trans_cook)
    userinfo_list=UserInfos.objects.filter(state=1).order_by('-publishtime') 
    userinfo_list=UserInfos.objects.filter().order_by(onlinetime) 
    context = {'userinfo_list': userinfo_list}
    return  render(request,'onlineuser.html',context )

def mguser(request):#管理用户
    cook = request.COOKIES.get('name')
    print('cook:', cook)
    if cook == None:
        return  render(request, 'index.html')
    else:
        trans_cook=cook.encode('latin-1').decode('utf-8')
    user = Users.objects.get(name = trans_cook)
    user_list=Users.objects.filter(usertype=0).order_by('-id')#只管理非管理员账户
    context = {'user_list': user_list}
    return  render(request,'mguser.html',context )

def adduser(request):#添加用户
    cook = request.COOKIES.get('name')
    if cook == None:
        return  render(request, 'index.html')
    else:
        trans_cook=cook.encode('latin-1').decode('utf-8')
    print('cook:', trans_cook)
    if request.method == 'POST':
        tempname = request.POST['name']
        temppsw = request.POST['password']

        if Users.objects.filter(name=tempname).exists():
            messages.add_message(request,messages.ERROR,'该账户已经存在')
            return HttpResponseRedirect(reverse('mguser'))
        else:
            user=Users(name = tempname,password=temppsw)
            user.save()
            userinfo=UserInfos(user=user)#初始时间赋值
            userinfo.save()
            return HttpResponseRedirect(reverse('mguser'))
    return HttpResponseRedirect(reverse('mguser'))

def deluser(request,user_id):#删除用户
    cook = request.COOKIES.get('name')
    if cook == None:
        return  render(request, 'index.html')
    else:
        trans_cook=cook.encode('latin-1').decode('utf-8')
    print('cook:', trans_cook)
    temp_id=user_id
    user = Users.objects.get(id=temp_id)
    UserInfos.objects.filter(user=user).delete()
    Users.objects.filter(id=temp_id).delete()
    return HttpResponseRedirect(reverse('mguser'))

def logout(request):#退出
    cook = request.COOKIES.get('name')
    if cook == None:
        return  render(request, 'index.html')
    else:
        trans_cook=cook.encode('latin-1').decode('utf-8')
    print('cook:', trans_cook)
    user = Users.objects.get(name = trans_cook)
    if user.usertype==0:
        userinfo = UserInfos.objects.get(user = user)
        if userinfo.state==1:
            userinfo.state=0
        userinfo.lastlogouttime=datetime.now()
        userinfo.save()
    request.session.delete()
    request.session.flush() 
    response=render(request, 'index.html')
    response.delete_cookie('name')
    return response

def myinfo(request):#我的界面
    cook = request.COOKIES.get('name')
    if cook == None:
        return  render(request, 'index.html')
    else:
        trans_cook=cook.encode('latin-1').decode('utf-8')
    print('cook:', trans_cook)
    user = Users.objects.get(name = trans_cook)
    if user.usertype==0:
        userinfo = UserInfos.objects.get(user = user)
        content={'my':user,"userinfo":userinfo}
        return render(request, 'my.html',content)
    else:
        content={'my':user}
        return render(request, 'my_a.html',content)

def modifypsw(request):#修改密码
    cook = request.COOKIES.get('name')
    if cook == None:
        return  render(request, 'index.html')
    else:
        trans_cook=cook.encode('latin-1').decode('utf-8')
    print('cook:', trans_cook)
    user = Users.objects.get(name = trans_cook)
    if request.method == 'POST':
        temp_psw=request.POST.get('password')
        user.password=temp_psw
        user.save()
        return HttpResponseRedirect(reverse('myinfo'))
    if user.usertype==0:
        userinfo = UserInfos.objects.get(user = user)
        content={'my':user,"userinfo":userinfo}
        return  render(request,'modifypsw.html',content)
    else:
        content={'my':user}
        return  render(request,'modifypsw_a.html',content)

def forceoffline(request,user_id):#强制下线
    cook = request.COOKIES.get('name')
    if cook == None:
        return  render(request, 'index.html')
    else:
        trans_cook=cook.encode('latin-1').decode('utf-8')
    print('cook:', trans_cook)
    user = Users.objects.get(name = trans_cook)
    if user.usertype==0:
        return  render(request, 'index.html')
    temp_id=user_id
    forceuser=Users.objects.get(id=temp_id)
    forceoffuser = UserInfos.objects.get(user=forceuser)
    forceoffuser.state=2 #将状态设置为强制下线，定时器中检测到该状态后，会强制顾客退出
    forceoffuser.save()
    return HttpResponseRedirect(reverse('home'))

#************************************************逻辑处理相关函数****************************************
def timeValied(time):
    inittime=datetime(1980,1,2,0,0,0)
    if time<inittime:
        return False
    else:
        return True
        
#定时任务，定时更新onlinetime
def timfunc():
    userinfo_list = UserInfos.objects.all()
    for userinfo in userinfo_list:
        if userinfo.state==1 and timeValied(userinfo.logintime):
            userinfo.onlinetime=int((datetime.now()-userinfo.logintime).total_seconds()/60)
            print("userinfo.onlintime =%d " % userinfo.onlinetime)
            if userinfo.onlinetime>60:
                userinfo.onlinetimestr=""+str(int(userinfo.onlinetime/60))+"小时"+str(int(userinfo.onlinetime%60))+"分钟"
            elif userinfo.onlinetime>1:
                userinfo.onlinetimestr=str(int(userinfo.onlinetime))+"分钟"
            else:
                userinfo.onlnietimestr="不到1分钟"
            if userinfo.onlinetime<30: #不满半小时按半小时算
                 userinfo.fee=fee_hafhour
            else:
                userinfo.fee=int(userinfo.onlinetime/30)*fee_hafhour

            if userinfo.onlinetime>60*4: #如果上网时间大于4小时强制下线
                print("userinfo.onlinetime>4hour set userinfo.state=3")
                userinfo.state=3
        elif userinfo.state==3 and timeValied(userinfo.lastlogouttime):
            print(userinfo.lastlogouttime)
            offlinetime=int((datetime.now()-userinfo.lastlogouttime).total_seconds()/60) #距离上次超时退网的时间差
            if offlinetime>60*2: #2小时后才能登陆
                print("offlinetime>2hour set userinfo.state=0")
                userinfo.state=0
        userinfo.save()
    
scheduler = BackgroundScheduler()
scheduler.add_job(timfunc, 'interval', seconds=60) #1分钟定时器
scheduler.start()
