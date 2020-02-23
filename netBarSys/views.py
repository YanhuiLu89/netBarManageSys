from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Users,UserInfos
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

#************************************************渲染相关函数****************************************
def index(request):
    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
    if request.method == 'POST':
        tempname = request.POST['name']
        password =  request.POST['password']
        usertype=int((request.POST['usertype']))
        # 查询用户是否在数据库中
        print("%s,%s,%d"%(tempname,password,usertype))
        if Users.objects.filter(name=tempname).exists():
            print("BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB")
            user=Users.objects.get(name=tempname)

            if user.password==password and int(user.usertype)==usertype:
                print("CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCc")
                if request.session.get("is_login")=='true' and request.COOKIES.get('name')==tempname:
                    print("DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD")
                    return HttpResponseRedirect(reverse('home'))
                else:
                    print("EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE")
                    request.session['is_login'] = 'true'
                    request.session['name'] = 'name',
                    if user.usertype==1:
                        userinfo_list = UserInfos.objects.filter().order_by('-logintime')
                        context = {'userinfo_list': userinfo_list}
                        response=render(request, 'homepage_a.html',context)#跳到管理员首页界面
                    else:
                        print("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF")
                        userinfo = UserInfos.objects.get(user = user)
                        if userinfo.state==3:
                            print("GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG")
                            messages.add_message(request,messages.ERROR,'距离你上次长时间上网还不到2个小时，请再休息一会')
                            return render(request, 'index.html')
                        else:
                            print("HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH")
                            userinfo.state=1
                            userinfo.logintime=datetime.now()
                            userinfo.save()
                            context = {'userinfo': userinfo}
                            response=render(request, 'homepage.html',context)#跳到顾客首页界面
                #set cookie
                print("JJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJ")
                response.set_cookie('name', user.name)
                return response
            else:
                print("KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK")
                messages.add_message(request,messages.ERROR,'用户密码或身份类型错误')
                return render(request, 'index.html')
        else:
            print("LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL")
            messages.add_message(request,messages.ERROR,'用户不存在')
            return render(request, 'index.html')
    print("MMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")
    return render(request, 'index.html')

def home(request):#去首页
    print("NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN")
    cook = request.COOKIES.get('name')
    if cook == None:
        print("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
        return  render(request, 'index.html')
    user = Users.objects.get(name = cook)
    if user.usertype == 0:
        print("PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP")
        userinfo = UserInfos.objects.get(user = user)
        print("QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ %d" %userinfo.state)
        context = {'userinfo': userinfo}
        return render(request, 'homepage.html',context)
    elif user.usertype == 1:
        print("RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR")
        userinfo_list = UserInfos.objects.filter().order_by('-logintime')
        context = {'userinfo_list': userinfo_list}
        return render(request, 'homepage_a.html',context)

def searchuser(request):#搜索用户
    cook = request.COOKIES.get('name')
    print('cook:', cook)
    if cook == None:
        return  render(request, 'index.html')
    user = Users.objects.get(name = cook)
    if request.method == 'POST':
        if 'search' in request.POST:#搜索
            searchcontent=request.POST['search_content']
            userinfo_list=UserInfos.objects.filter().order_by('-publishtime') 
            context = {'userinfo_list': userinfo_list}
            messages.add_message(request,messages.INFO,'共'+str(len(userinfo_list))+'条结果')
            return  render(request,'homepage_a.html',context )
    return render(request, 'homepage_a.html')

def onlineuser(request):#显示在线用户
    cook = request.COOKIES.get('name')
    print('cook:', cook)
    if cook == None:
        return  render(request, 'index.html')
    user = Users.objects.get(name = cook)
    userinfo_list=UserInfos.objects.filter(state=1).order_by('-publishtime') 
    userinfo_list=UserInfos.objects.filter().order_by(onlinetime) 
    context = {'userinfo_list': userinfo_list}
    return  render(request,'onlineuser.html',context )

def mguser(request):#管理用户
    cook = request.COOKIES.get('name')
    print('cook:', cook)
    if cook == None:
        return  render(request, 'index.html')
    user = Users.objects.get(name = cook)
    user_list=Users.objects.filter(usertype=0).order_by('-id')#只管理非管理员账户
    context = {'user_list': user_list}
    return  render(request,'mguser.html',context )

def adduser(request):#添加用户
    cook = request.COOKIES.get('name')
    print('cook:', cook)
    if cook == None:
        return  render(request, 'index.html')
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
    print('cook:', cook)
    if cook == None:
        return  render(request, 'index.html')
    temp_id=user_id
    user = Users.objects.get(id=temp_id)
    UserInfos.objects.filter(user=user).delete()
    Users.objects.filter(id=temp_id).delete()
    return HttpResponseRedirect(reverse('mguser'))

def logout(request):#退出
    print("logoutlogoutlogoutlogoutlogoutlogoutlogoutlogoutlogoutlogoutlogoutlogoutlogoutlogoutlogoutlogout")
    cook = request.COOKIES.get('name')
    print('cook:', cook)
    if cook == None:
        print("cook == Nonecook == Nonecook == Nonecook == Nonecook == Nonecook == None")
        return  render(request, 'index.html')
    user = Users.objects.get(name = cook)
    if user.usertype==0:
        userinfo = UserInfos.objects.get(user = user)
        if userinfo.state!=3:
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
    print('cook:', cook)
    if cook == None:
        return  render(request, 'index.html')
    user = Users.objects.get(name = cook)
    content={'my':user}
    if user.usertype==0:
        return render(request, 'my.html',content)
    elif user.usertype==1:
        return render(request, 'my_a.html',content)

def forceoffline(request,user_id):#强制下线
    cook = request.COOKIES.get('name')
    print('cook:', cook)
    if cook == None:
        return  render(request, 'index.html')
    user = Users.objects.get(name = cook)
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
    print("Tick! userinfo_list=%s" % userinfo_list.count())
    for userinfo in userinfo_list:
        if userinfo.state==1 and timeValied(userinfo.logintime):
            userinfo.onlinetime=(datetime.now()-userinfo.logintime).total_seconds()/60
            print(userinfo.lastlogouttime)
            print("userinfo.onlinetime=%d" % userinfo.onlinetime)
            if userinfo.onlinetime>1: #如果上网时间大于4小时强制下线
                print("userinfo.onlinetime>1 userinfo.state=3")
                userinfo.state=3
                userinfo.save()
        elif userinfo.state==3 and timeValied(userinfo.lastlogouttime):
            print("111111111111111111111111111111")
            print(userinfo.lastlogouttime)
            offlinetime=(datetime.now()-userinfo.lastlogouttime).total_seconds()/60 #距离上次超时退网的时间差
            if offlinetime>1*2: #2小时后才能登陆
                print("22222222222222222222")
                userinfo.state=0
                userinfo.save()
    
scheduler = BackgroundScheduler()
scheduler.add_job(timfunc, 'interval', seconds=10) #1分钟定时器
scheduler.start()
