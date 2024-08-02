from django.db import models

class User(models.Model):
    """
    用户模型，存储用户的基本信息
    """
    username = models.CharField(max_length=150, unique=True, verbose_name="用户名")  # 用户名，唯一
    name = models.CharField(max_length=150, verbose_name="姓名")  # 姓名
    password = models.CharField(max_length=128, verbose_name="密码")  # 密码，存储哈希值
    email = models.EmailField(unique=True, verbose_name="邮箱")  # 邮箱，唯一
    mobile = models.CharField(max_length=15, verbose_name="手机号")  # 手机号
    status = models.BooleanField(default=True, verbose_name="状态")  # 用户状态，是否激活
    login_time = models.DateTimeField(null=True, blank=True, verbose_name="最后登录时间")  # 最后登录时间
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")  # 创建时间
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")  # 更新时间

    class Meta:
        db_table = 't_user'  # 指定数据库表名为 t_user

    def __str__(self):
        return self.username

class UserLock(models.Model):
    """
    用户锁定模型，记录用户的登录尝试次数和最后尝试时间
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="用户")  # 关联到 User 模型
    login_count = models.IntegerField(default=0, verbose_name="登录尝试次数")  # 登录尝试次数
    last_attempt_time = models.DateTimeField(null=True, blank=True, verbose_name="最后尝试时间")  # 最后尝试时间

    class Meta:
        db_table = 't_user_lock'  # 指定数据库表名为 t_user_lock

    def __str__(self):
        return f"{self.user.username} - {self.login_count}"

class Role(models.Model):
    """
    角色模型，存储角色的基本信息
    """
    role_name = models.CharField(max_length=150, unique=True, verbose_name="角色名")  # 角色名，唯一
    description = models.TextField(verbose_name="描述")  # 角色描述
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")  # 创建时间
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")  # 更新时间

    class Meta:
        db_table = 't_role'  # 指定数据库表名为 t_role

    def __str__(self):
        return self.role_name

class Permission(models.Model):
    """
    权限模型，存储权限的基本信息
    """
    name = models.CharField(max_length=150, unique=True, verbose_name="权限名")  # 权限名，唯一
    code = models.CharField(max_length=150, unique=True, verbose_name="权限代码")  # 权限代码，唯一
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")  # 创建时间
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")  # 更新时间

    class Meta:
        db_table = 't_permission'  # 指定数据库表名为 t_permission

    def __str__(self):
        return self.name

class RolePermission(models.Model):
    """
    角色权限模型，存储角色和权限的对应关系
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")  # 关联到 User 模型
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name="角色")  # 关联到 Role 模型
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, verbose_name="权限")  # 关联到 Permission 模型

    class Meta:
        db_table = 't_role_permission'  # 指定数据库表名为 t_role_permission
        unique_together = (('user', 'role', 'permission'),)  # 联合唯一约束

    def __str__(self):
        return f"{self.user.username} - {self.role.role_name} - {self.permission.name}"

class Token(models.Model):
    """
    令牌模型，存储用户的认证令牌
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="用户")  # 关联到 User 模型
    token = models.CharField(max_length=500, verbose_name="令牌")  # 令牌字符串
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")  # 创建时间

    class Meta:
        db_table = 't_token'  # 指定数据库表名为 t_token

    def __str__(self):
        return f"{self.user.username} - {self.token}"

class LoginLog(models.Model):
    """
    登录日志模型，记录用户的登录信息
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="用户")  # 关联到 User 模型
    username = models.CharField(max_length=150, verbose_name="用户名")  # 用户名
    client_ip = models.GenericIPAddressField(verbose_name="客户端IP")  # 客户端 IP 地址
    login_status = models.BooleanField(default=False, verbose_name="登录状态")  # 登录状态，成功或失败
    reason = models.CharField(max_length=255, null=True, blank=True, verbose_name="登录失败原因")  # 登录失败原因
    browser_info = models.CharField(max_length=255, verbose_name="浏览器信息")  # 浏览器信息
    # 用户操作系统
    os_info = models.CharField(max_length=255, null=True, blank=True, verbose_name="操作系统信息")
    login_time = models.DateTimeField(auto_now_add=True, verbose_name="登录时间")  # 登录时间

    class Meta:
        db_table = 't_login_log'  # 指定数据库表名为 t_login_log

    def __str__(self):
        return f"{self.username} - {self.client_ip} - {self.login_status}"
