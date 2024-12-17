from django.db import models
import uuid
from django.utils import timezone

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
    otp_secret_key = models.CharField(max_length=32, null=True, blank=True, verbose_name="OTP密钥")  # 用于存储2FA密钥
    mfa_level = models.IntegerField(default=0, choices=[(0, '关闭'), (1, '开启')], verbose_name="MFA认证等级")  # MFA认证等级

    class Meta:
        db_table = 't_user'  # 指定数库表名为 t_user

    def __str__(self):
        return self.username

class UserLock(models.Model):
    """
    用户锁定模型，记录用户的登录尝试次数和最后尝试时间
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="用户")  # 关联到 User 模型
    login_count = models.IntegerField(default=0, verbose_name="登录尝试次数")  # 登录尝试次数
    lock_count = models.IntegerField(default=0, verbose_name="尝试锁定次数")  # 尝试锁定次数
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
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="用户")
    token = models.CharField(max_length=500, verbose_name="令牌")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    last_activity = models.DateTimeField(auto_now=True, verbose_name="最后活动时间")

    class Meta:
        db_table = 't_token'

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


class OperationLog(models.Model):
    """
    操作日志模型，记录用户的操作信息
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="操作人员")  # 关联到 User 模型
    module = models.CharField(max_length=150, verbose_name="操作模块")  # 操作模块
    request_interface = models.CharField(max_length=255, verbose_name="请求接口")  # 请求接口
    request_method = models.CharField(max_length=10, verbose_name="请求方式")  # 请求方式，如 GET、POST 等
    ip_address = models.GenericIPAddressField(verbose_name="IP地址")  # IP地址
    before_change = models.TextField(null=True, blank=True, verbose_name="变更前")  # 变更前的内容
    after_change = models.TextField(null=True, blank=True, verbose_name="变更后")  # 变更后的内容
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")  # 创建时间

    class Meta:
        db_table = 't_operation_log'  # 指定数据库表名为 t_operation_log

    def __str__(self):
        return f"{self.user.username} - {self.module} - {self.create_time}"

class Credential(models.Model):
    """
    凭据模型，存储不同类型的凭据信息
    """

    id = models.AutoField(primary_key=True)  # 自动生成的 ID
    name = models.CharField(max_length=150, verbose_name="凭据名称")  # 凭据名称
    type = models.CharField(max_length=50, verbose_name="凭据类型")  # 凭据类型
    account = models.CharField(max_length=150, null=True, blank=True, verbose_name="账户")  # 账户名
    password = models.CharField(max_length=128, null=True, blank=True, verbose_name="密码")  # 密码（加密存储）
    key = models.TextField(null=True, blank=True, verbose_name="密钥")  # 密钥
    key_password = models.CharField(max_length=128, null=True, blank=True, verbose_name="密钥密码")  # 密钥密码
    KeyId = models.CharField(max_length=255, null=True, blank=True, verbose_name="API Key")  # API 密钥
    KeySecret = models.CharField(max_length=255, null=True, blank=True, verbose_name="API Secret")  # API 密钥
    notes = models.TextField(null=True, blank=True, verbose_name="备注")  # 备注
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")  # 创建时间

    class Meta:
        db_table = 't_credential'  # 指定数据库表名为 t_credential

    def __str__(self):
        return f"{self.name} - {self.type}"


class DomainMonitor(models.Model):
    """
    域名监控模型，存储域名监控的相关信息
    """
    name = models.CharField(max_length=150, verbose_name="监控名称")  # 监控名称
    domain = models.CharField(max_length=255, verbose_name="域名")  # 域名
    # type = models.CharField(max_length=50, verbose_name="监控类型")  # 监控型
    connectivity = models.BooleanField(default=False, verbose_name="连通性")  # 连通性
    status_code = models.IntegerField(null=True, blank=True, verbose_name="状态码")  # 状态码
    redirection = models.CharField(max_length=255, null=True, blank=True, verbose_name="重定向地址")  # 重定向地址
    time_consumption = models.FloatField(null=True, blank=True, verbose_name="耗时（秒）")  # 耗时（秒
    # dns = models.CharField(max_length=255, null=True, blank=True, verbose_name="DNS 信息")  # DNS 信息
    tls_version = models.CharField(max_length=50, null=True, blank=True, verbose_name="TLS 版本")  # TLS 版本
    http_version = models.CharField(max_length=50, null=True, blank=True, verbose_name="HTTP 版本")  # HTTP 版本
    certificate_days = models.IntegerField(null=True, blank=True, verbose_name="证书剩余天数")  # 证书剩余天数
    enable = models.BooleanField(default=True, verbose_name="启用")  # 是否启用监控
    alert = models.BooleanField(default=False, verbose_name="告警")  # 是否开启告警
    monitor_frequency = models.IntegerField(default=60, verbose_name="监控频率（秒）")  # 监控频率（秒）
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")  # 创建时间

    class Meta:
        db_table = 't_domain_monitor'  # 指定数据库表名为 t_domain_monitor

    def __str__(self):
        return f"{self.name} - {self.domain}"


class Node(models.Model):
    """
    树节点模型，存储节点信息
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # 使用 UUID 作为主键
    name = models.CharField(max_length=150, verbose_name="节点名称")  # 节点名称
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children', verbose_name="父节点")  # 自引用外键，允许为空
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")  # 创建时间

    class Meta:
        db_table = 't_node'  # 指定数据库表名为 t_node

    def __str__(self):
        return self.name

class Host(models.Model):
    """
    主机模型，存储主机信息
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # 使用 UUID 作为主键
    name = models.CharField(max_length=150, verbose_name="主机名称")  # 主机名称
    status = models.BooleanField(default=False, verbose_name="连接状态")  # 是否可连接
    operating_system = models.CharField(max_length=50, verbose_name="操作系统")  # 操作系统
    network = models.GenericIPAddressField(verbose_name="IP地址")  # IP地址
    protocol = models.CharField(max_length=10, verbose_name="协议")  # 协议
    port = models.IntegerField(verbose_name="端口")  # 端口
    account_type = models.ForeignKey(Credential, null=True, blank=True, on_delete=models.CASCADE, verbose_name="关联凭据")  # 关联凭据，允许为空
    remarks = models.TextField(null=True, blank=True, verbose_name="备注")  # 备注
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")  # 创建时间
    node = models.ForeignKey(Node, null=True, blank=True, on_delete=models.CASCADE, related_name='hosts', verbose_name="所属节点")  # 关联节点，允许为空

    class Meta:
        db_table = 't_host'  # 指定数据库表名为 t_host

    def __str__(self):
        return f"{self.name} - {self.operating_system} - {self.network}"

# 添加新的模型
class CommandLog(models.Model):
    """
    命令日志模型，记录用户执行的命令信息
    """
    username = models.CharField(max_length=150, verbose_name="用户名")  # 执行命令的用户名
    command = models.TextField(verbose_name="执行的命令")  # 记录执行过的命令
    hosts = models.CharField(max_length=255, verbose_name="执行主机")  # 记录执行的主机名
    network = models.CharField(null=True, blank=True, max_length=255, verbose_name="执行主机IP")  # 记录执行的主机IP
    credential = models.CharField(max_length=150, verbose_name="使用的凭据")  # 记录执行命令当前使用账号凭据名称
    create_time = models.DateTimeField(default=timezone.now, verbose_name="创建时间")  # 执行时间

    class Meta:
        db_table = 't_command_log'  # 指定数据库表名为 t_command_log

    def __str__(self):
        return f"{self.username} - {self.hosts} - {self.command[:50]}"

# 在文件的适当位置添加以下代码

class AlertContact(models.Model):
    """
    告警联系人模型，存储告警联系人的基本信息
    """
    name = models.CharField(max_length=150, unique=True, verbose_name="告警联系人名称")
    creator = models.CharField(max_length=150, verbose_name="创建人")
    notify_type = models.CharField(max_length=50, verbose_name="通知类型")  # 钉钉、企微、飞书
    webhook = models.URLField(max_length=255, verbose_name="Webhook链接")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = 't_alert_contacts'  # 指定数据库表名为 t_alert_contacts

    def __str__(self):
        return self.name

class CommandAlert(models.Model):
    """
    命令告警模型，用于设置命令告警规则
    """
    name = models.CharField(max_length=150, unique=True, verbose_name="告警名称")
    command_rule = models.TextField(null=True, blank=True,verbose_name="命令规则")
    hosts = models.TextField(null=True, blank=True,verbose_name="关联主机")  # 存储主机名，用逗号分隔
    alert_contacts = models.TextField(null=True, blank=True, verbose_name="告警联系人")  # 存储联系人名称，用逗号分隔
    is_active = models.BooleanField(null=True, blank=True, default=True, verbose_name="是否告警")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    match_type = models.CharField(max_length=20, choices=[('exact', '精匹配'), ('fuzzy', '模糊匹配')], default='exact', verbose_name="匹配类型")

    class Meta:
        db_table = 't_command_alert'

    def __str__(self):
        return self.name

class SystemSettings(models.Model):
    """
    系统设置模型，存储全局配置
    """
    watermark_enabled = models.BooleanField(default=True, verbose_name="水印启用状态")
    ip_whitelist = models.TextField(null=True, blank=True, verbose_name="IP白名单")
    ip_blacklist = models.TextField(null=True, blank=True, verbose_name="IP黑名单")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    multi_login_account = models.CharField(max_length=150, null=True, blank=True, verbose_name="多人登录账号")

    class Meta:
        db_table = 't_system_settings'

class AlertHistoryLog(models.Model):
    """
    告警历史记录模型，记录触发的告警信息
    """
    alert_name = models.CharField(max_length=150, verbose_name="告警名称")
    alert_rule = models.TextField(verbose_name="告警规则")
    alert_contacts = models.TextField(verbose_name="告警联系人")
    alert_time = models.DateTimeField(auto_now_add=True, verbose_name="告警时间")

    class Meta:
        db_table = 't_alert_history_log'  # 指定数据库表名为 t_alert_history_log

    def __str__(self):
        return f"{self.alert_name} - {self.alert_time}"


