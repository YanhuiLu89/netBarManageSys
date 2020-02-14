from django.db import models

# Create your models here.
class Users(models.Model):
    usertype = models.IntegerField(default=0)#0-顾客，1-管理员
    name = models.CharField(max_length=50)
    password = models.CharField(max_length=50)

class UserInfos(models.Model):
    user= models.OneToOneField(Users, on_delete=models.CASCADE)
    loginintime=models.DateTimeField('login in time')#登录时间
    lastLogouttime=models.DateTimeField('last login out time')#上次登出时间
    onlinetime=models.IntegerField(default=0)#在线时间单位分钟，当该值超过240，强制下线
    state=models.IntegerField(default=0)#顾客状态0-offline normal,1-online normal 2 force off line 
    fee=models.IntegerField(default=0)#费用