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