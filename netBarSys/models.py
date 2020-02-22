from django.db import models

# Create your models here.
class Users(models.Model):
    usertype = models.IntegerField(default=0)#0-顾客，1-管理员
    name = models.CharField(max_length=50)
    password = models.CharField(max_length=50)

class UserInfos(models.Model):
    user= models.OneToOneField(Users, on_delete=models.CASCADE)
    logintime=models.DateTimeField('login in time',default='1920-01-01 00:00:00')#登录时间,初始值赋值一个极早的时间，代表无效值
    lastLogouttime=models.DateTimeField('last login out time',default='1920-01-01 00:00:00')#上次登出时间,初始值赋值一个极早的时间，代表无效值
    onlinetime=models.IntegerField(default=0)#在线时间单位分钟，当该值超过240，强制下线
    state=models.IntegerField(default=0)#顾客状态0-offline normal,1-online normal 2 管理员手动强制下线  3、超时自动强制下线
    fee=models.IntegerField(default=0)#费用