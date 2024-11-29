import socket
import ssl
import requests
from django.utils import timezone
from datetime import datetime, timedelta
from django.conf import settings
from django.db import models
import logging

logger = logging.getLogger('log')

def cleanup_expired_tokens():
    """
    定期清理过期的token
    """
    from .models import Token
    
    now = timezone.now()
    # 修改清理逻辑，使用新的配置名
    expired_time = now - timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES)  # 使用新的配置名
    session_timeout = now - timedelta(minutes=settings.SESSION_TIMEOUT_MINUTES)
    
    # 使用 Q 对象组合查询条件
    Token.objects.filter(
        models.Q(create_time__lt=expired_time) |  # token 过期
        models.Q(last_activity__lt=session_timeout)  # 会话超时
    ).delete()

class DomainMonitorTask:
    """
    DomainMonitorTask 类处理域名监控的具体逻辑
    """
    @staticmethod
    def normalize_domain(domain):
        """
        规范化域，以确保其格式一致。
        """
        if domain.startswith("http://"):
            domain = domain[len("http://"):]
        elif domain.startswith("https://"):
            domain = domain[len("https://"):]

        return domain.strip()
    
    @staticmethod
    def monitor_domain(domain_id):
        """
        定时任务：监控域名
        :param domain_id: DomainMonitor对象的ID
        """
        from .models import DomainMonitor
        
        domain = DomainMonitor.objects.get(id=domain_id)
        try:
            # 标准化域名
            normalized_domain = DomainMonitorTask.normalize_domain(domain.domain)

            # 优先使用 HTTPS 进行请求
            try:
                response = requests.get(f"https://{normalized_domain}", timeout=10, allow_redirects=True)
            except requests.exceptions.RequestException:
                # 如果 HTTPS 请求失败，则尝试 HTTP
                response = requests.get(f"http://{normalized_domain}", timeout=10, allow_redirects=True)
            
            final_url = response.url  # 最终的URL（可能是重定向后的）
            domain.connectivity = True
            domain.status_code = response.status_code
            domain.redirection = final_url != f"https://{normalized_domain}" and final_url != f"http://{normalized_domain}"
            domain.time_consumption = response.elapsed.total_seconds()

            if domain.redirection:
                logger.info(f"Domain {domain.domain} redirected to {final_url} with status code {response.status_code}")

            # 将HTTP版本号转换并存储
            domain.http_version = str(response.raw.version / 10)  # 格式化HTTP版本

            # 获取TLS版本信息
            context = ssl.create_default_context()
            try:
                with socket.create_connection((normalized_domain, 443), timeout=10) as sock:
                    with context.wrap_socket(sock, server_hostname=normalized_domain) as ssock:
                        domain.tls_version = ssock.version()
                        cert = ssock.getpeercert()
                        domain.certificate_days = (datetime.strptime(cert['notAfter'], "%b %d %H:%M:%S %Y GMT") - timezone.now()).days
                        
                        # 打印证书颁发者信息
                        issuer = dict(x[0] for x in cert['issuer'])
                        print(f"Certificate issued by: {issuer.get('organizationName', 'Unknown')}")
            except Exception as ssl_error:
                logger.error(f"TLS/SSL Error for domain {normalized_domain}: {ssl_error}")
                domain.tls_version = "N/A"
                domain.certificate_days = None

            domain.save()

        except requests.exceptions.RequestException as req_error:
            domain.connectivity = False
            logger.error(f"HTTP request error for domain {normalized_domain}: {str(req_error)}")
            domain.save()
        except socket.gaierror as dns_error:
            domain.connectivity = False
            logger.error(f"DNS resolution error for domain {normalized_domain}: {str(dns_error)}")
            domain.save()
        except Exception as e:
            domain.connectivity = False
            logger.error(f"监控域名 {domain.domain} 时出错: {str(e)}")
            domain.save()
