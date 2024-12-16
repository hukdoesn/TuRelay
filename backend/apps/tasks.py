import socket
import ssl
import requests
from django.utils import timezone
from datetime import datetime
from django.conf import settings
import logging
from urllib.parse import urlparse

logger = logging.getLogger('log')

class DomainMonitorTask:
    """
    DomainMonitorTask 类处理域名监控的具体逻辑
    """
    @staticmethod
    def normalize_domain(domain):
        """
        规范化域名，确保使用HTTPS协议
        """
        domain = domain.strip()
        if not domain.startswith('https://'):
            if domain.startswith('http://'):
                domain = 'https://' + domain[7:]
            else:
                domain = 'https://' + domain
        return domain

    @staticmethod
    def check_ssl_certificate(domain):
        """
        检查SSL证书状态
        """
        parsed_url = urlparse(domain)
        hostname = parsed_url.netloc
        context = ssl.create_default_context()
        
        try:
            with socket.create_connection((hostname, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    expiry_date = datetime.strptime(cert['notAfter'], "%b %d %H:%M:%S %Y GMT")
                    days_remaining = (expiry_date - timezone.now()).days
                    
                    cert_info = {
                        'tls_version': ssock.version(),
                        'days_remaining': days_remaining,
                        'issuer': dict(x[0] for x in cert['issuer']),
                        'expiry_date': expiry_date
                    }
                    
                    if days_remaining <= 0:
                        raise ssl.CertificateError(f"证书已过期 {-days_remaining} 天")
                    elif days_remaining <= 30:
                        logger.warning(f"域名 {domain} 的SSL证书即将在 {days_remaining} 天后过期")
                    
                    return cert_info
                    
        except (socket.gaierror, socket.timeout) as e:
            logger.error(f"域名 {domain} 的SSL连接失败: {str(e)}")
            raise ssl.SSLError(f"无法建立SSL连接: {str(e)}")
        except ssl.SSLError as e:
            logger.error(f"域名 {domain} 的SSL验证失败: {str(e)}")
            raise
    
    @staticmethod
    def monitor_domain(domain_id):
        """
        定时任务：监控域名
        :param domain_id: DomainMonitor对象的ID
        """
        from .models import DomainMonitor
        
        domain_obj = DomainMonitor.objects.get(id=domain_id)
        try:
            # 标准化域名（确保使用HTTPS）
            normalized_domain = DomainMonitorTask.normalize_domain(domain_obj.domain)
            domain_obj.domain = normalized_domain  # 更新为标准化的域名
            
            # 首先检查SSL证书
            try:
                cert_info = DomainMonitorTask.check_ssl_certificate(normalized_domain)
                domain_obj.tls_version = cert_info['tls_version']
                domain_obj.certificate_days = cert_info['days_remaining']
                logger.info(f"域名 {normalized_domain} SSL证书检查通过，剩余 {cert_info['days_remaining']} 天")
            except (ssl.SSLError, ssl.CertificateError) as ssl_error:
                domain_obj.connectivity = False
                domain_obj.tls_version = "N/A"
                domain_obj.certificate_days = None
                logger.error(f"域名 {normalized_domain} SSL证书检查失败: {str(ssl_error)}")
                domain_obj.save()
                return
            
            # 尝试HTTPS请求
            try:
                response = requests.get(normalized_domain, timeout=10, verify=True)
                domain_obj.connectivity = True
                domain_obj.status_code = response.status_code
                domain_obj.redirection = response.url != normalized_domain
                domain_obj.time_consumption = response.elapsed.total_seconds()
                domain_obj.http_version = str(response.raw.version / 10)

                if domain_obj.redirection:
                    logger.info(f"域名 {normalized_domain} 重定向到 {response.url}")
                
                domain_obj.save()
                logger.info(f"域名 {normalized_domain} 监控成功，状态码: {response.status_code}")
                
            except requests.exceptions.SSLError as ssl_err:
                domain_obj.connectivity = False
                logger.error(f"域名 {normalized_domain} SSL连接错误: {str(ssl_err)}")
                domain_obj.save()
            except requests.exceptions.RequestException as req_err:
                domain_obj.connectivity = False
                logger.error(f"域名 {normalized_domain} 请求失败: {str(req_err)}")
                domain_obj.save()
                
        except Exception as e:
            domain_obj.connectivity = False
            logger.error(f"监控域名 {domain_obj.domain} 时发生未知错误: {str(e)}")
            domain_obj.save()
