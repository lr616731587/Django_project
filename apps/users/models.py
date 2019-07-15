from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager as _UserManager
# Create your models here.
# is_staff 用户是否可以登录admin管理界面
# is_active 是否为活跃用户
#


class UserManage(_UserManager):

    def create_superuser(self, username, password, email=None, **extra_fields):
        super().create_superuser(username=username, password=password, email=email, **extra_fields)


class User(AbstractUser):
    """
    add mobile email_active fields to Django users models
    """
    objects = UserManage()
    REQUIRED_FIELDS = ['mobile']  # 指定用什么方式注册账户

    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号',
                              help_text='mobile number', error_messages={'unique': '此手机号已注册'})
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name  # 显示复数名称

    def __str__(self):
        return self.username



