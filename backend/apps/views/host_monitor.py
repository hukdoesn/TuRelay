import paramiko
import io
from django.conf import settings
import logging
from ..models import Host, Credential

logger = logging.getLogger('log')

class HostMonitorTask:
    """
    主机监控任务类，用于定期检测主机连接状态
    """
    @staticmethod
    def test_ssh_connection(ip, port, username, password):
        """
        测试SSH密码连接
        """
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, port=port, username=username, password=password, timeout=5)
            ssh.close()
            return True
        except Exception as e:
            logger.error(f"SSH connection failed for {ip}:{port}: {str(e)}")
            return False

    @staticmethod
    def test_ssh_key_connection(ip, port, username, key, key_password=None):
        """
        测试SSH密钥连接
        """
        try:
            key_file = io.StringIO(key)
            pkey = paramiko.RSAKey.from_private_key(key_file, password=key_password)
            
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, port=port, username=username, pkey=pkey, timeout=5)
            ssh.close()
            return True
        except Exception as e:
            logger.error(f"SSH key connection failed for {ip}:{port}: {str(e)}")
            return False

    @staticmethod
    def monitor_hosts():
        """
        监控所有主机的连接状态
        """
        try:
            # 获取所有启用的主机
            hosts = Host.objects.all()
            
            for host in hosts:
                if not host.account_type:
                    logger.warning(f"Host {host.name} has no credential configured")
                    host.status = False
                    host.save()
                    continue

                credential = host.account_type
                success = False

                if host.protocol == 'SSH':
                    if credential.type == '密码':
                        success = HostMonitorTask.test_ssh_connection(
                            host.network,
                            host.port,
                            credential.account,
                            credential.password
                        )
                    elif credential.type == '密钥':
                        success = HostMonitorTask.test_ssh_key_connection(
                            host.network,
                            host.port,
                            credential.account,
                            credential.key,
                            credential.key_password
                        )
                elif host.protocol == 'RDP':
                    # 这里可以添加RDP连接测试逻辑
                    # 暂时跳过RDP测试
                    continue

                # 更新主机状态
                if host.status != success:
                    host.status = success
                    host.save()
                    logger.info(f"Host {host.name} ({host.network}) status updated to: {'connected' if success else 'disconnected'}")

        except Exception as e:
            logger.error(f"Error in host monitoring task: {str(e)}") 