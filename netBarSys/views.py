from django.shortcuts import render
from django.contrib import messages
from .models import Users,UserInfos
# Create your views here.

def index(request):
    if request.method == 'POST':
        name = request.POST['username']
        password =  request.POST['password']
        usertype=int((request.POST['usertype']))
        # 查询用户是否在数据库中
        print("%s,%s,%d"%(name,password,usertype))
        if Users.objects.filter(name=name).exists():
            user=Users.objects.get(name=name)
            print("%s,%s,%d" % (user.name,user.password,user.usertype))
            print(user.password+",%d" % user.usertype)
            if user.password==password and int(user.usertype)==usertype:
                request.session['is_login'] = 'true'
                request.session['username'] = 'username',
                if user.usertype==1:
                    response=render(request, 'homepage_a.html')#跳到管理员首页界面
                else:
                    response=render(request, 'homepage.html')#跳到顾客首页界面
                #set cookie
                response.set_cookie('username', user.name)
                return response
            else:
                messages.add_message(request,messages.ERROR,'用户密码或身份类型错误')
                return render(request, 'index.html')
        else:
            messages.add_message(request,messages.ERROR,'用户不存在')
            return render(request, 'index.html')
    return render(request, 'index.html')

def home(request):#去首页
    cook = request.COOKIES.get('username')
    if cook == None:
        return  render(request, 'index.html')
    user = Users.objects.get(username = cook)
    if user.usertype == 0:
        userinfo_list = UserInfos.objects.filter().order_by('-publishtime')
        context = {'userinfo_list': userinfo_list}
        return render(request, 'homepage.html',context)
    elif user.usertype == 1:
        userinfo = UserInfos.objects.get(user = user)
        context = {'userinfo': userinfo}
        return render(request, 'homepage_a.html',context)

def searchuser(request):#搜索用户
    cook = request.COOKIES.get('username')
    print('cook:', cook)
    if cook == None:
        return  render(request, 'pages/index.html')
    user = Users.objects.get(username = cook)
    if request.method == 'POST':
        if 'search' in request.POST:#搜索
            searchcontent=request.POST['search_content']
            userinfo_list=UserInfos.objects.filter().order_by('-publishtime') 
            context = {'userinfo_list': userinfo_list}
            messages.add_message(request,messages.INFO,'共'+str(len(userinfo_list_list))+'条结果')
            return  render(request,'pages/homepage_a.html',context )
    return render(request, 'pages/homepage_a.html')
