from django.shortcuts import render
from django.contrib import messages
from .models import Users,UserInfos
# Create your views here.

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
                request.session['is_login'] = 'true'
                request.session['name'] = 'name',
                if user.usertype==1:
                    response=render(request, 'homepage_a.html')#跳到管理员首页界面
                else:
                    response=render(request, 'homepage.html')#跳到顾客首页界面
                #set cookie
                response.set_cookie('name', user.name)
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
    user = Users.objects.get(name = cook)
    if user.usertype == 0:
        userinfo_list = UserInfos.objects.filter().order_by('-publishtime')
        context = {'userinfo_list': userinfo_list}
        return render(request, 'homepage.html',context)
    elif user.usertype == 1:
        userinfo = UserInfos.objects.get(user = user)
        context = {'userinfo': userinfo}
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

def mguser(request):#管理
    cook = request.COOKIES.get('name')
    print('cook:', cook)
    if cook == None:
        return  render(request, 'index.html')
    user = Users.objects.get(name = cook)
    user_list=Users.objects.all() 
    context = {'user_list': user_list}
    return  render(request,'mguser.html',context )

def adduser(request):#
    cook = request.COOKIES.get('name')
    print('cook:', cook)
    if cook == None:
        return  render(request, 'index.html')
    if request.method == 'POST':
        tempname = request.POST['name']
        temppsw = request.POST['password']
        temptype= request.POST['type']

        if Users.objects.filter(name=name).exists():
            messages.add_message(request,messages.ERROR,'该账户已经存在')
            return render(request, 'pages/mguser.html')
        else:
            user=Users(usertype=temptype,name = tempname,password=temppsw)
            user.save()
            return HttpResponseRedirect(reverse('pages:mguser'))
    return render(request, 'pages/mguser.html')

def deluser(request,user_id):
    cook = request.COOKIES.get('name')
    print('cook:', cook)
    if cook == None:
        return  render(request, 'index.html')
    temp_id=user_id
    user = Users.objects.get(id=temp_id)
    UserInfos.objects.filter(user=user).delete()
    Users.objects.filter(id=temp_id).delete()
    return HttpResponseRedirect(reverse('pages:mguser'))

def logout(request):#退出
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
