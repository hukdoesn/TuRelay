from django.db import models

class User(models.Model):
    username = models.CharField(max_length=150, unique=True, verbose_name="用户名")
    name = models.CharField(max_length=150, verbose_name="姓名")
    password = models.CharField(max_length=128, verbose_name="密码")
    email = models.EmailField(unique=True, verbose_name="邮箱")
    mobile = models.CharField(max_length=15, verbose_name="手机号")
    status = models.BooleanField(default=True, verbose_name="状态")
    login_time = models.DateTimeField(null=True, blank=True, verbose_name="最后登录时间")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 't_user'     # 指定数据库表名为 t_user
    def __str__(self):
        return self.username

class UserLock(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="用户")
    login_count = models.IntegerField(default=0, verbose_name="登录尝试次数")
    last_attempt_time = models.DateTimeField(null=True, blank=True, verbose_name="最后尝试时间")

    class Meta:
        db_table = 't_user_lock'

    def __str__(self):
        return f"{self.user.username} - {self.login_count}"

class Role(models.Model):
    role_name = models.CharField(max_length=150, unique=True, verbose_name="角色名")
    description = models.TextField(verbose_name="描述")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 't_role'

    def __str__(self):
        return self.role_name

class Permission(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name="权限名")
    code = models.CharField(max_length=150, unique=True, verbose_name="权限代码")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 't_permission'

    def __str__(self):
        return self.name

class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name="角色")

    class Meta:
        db_table = 't_user_role'
        unique_together = (('user', 'role'),)       # 联合唯一约束

    def __str__(self):
        return f"{self.user.username} - {self.role.role_name}"


class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name="角色")
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, verbose_name="权限")

    class Meta:
        db_table = 't_role_permission'
        unique_together = (('role', 'permission'),)

    def __str__(self):
        return f"{self.role.role_name} - {self.permission.name}"
    
class Token(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="用户")
    token = models.CharField(max_length=255, verbose_name="令牌")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = 't_token'

    def __str__(self):
        return f"{self.user.username} - {self.token}"