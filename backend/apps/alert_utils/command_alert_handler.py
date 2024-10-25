from apps.models import CommandAlert, Host
from asgiref.sync import sync_to_async
from .alert_notifier import send_alert_notification
import re
import logging
import json

# 获取日志记录器实例
logger = logging.getLogger('log')

async def check_command_alert(host_id, command, username):
    try:
        logger.debug(f"开始检查命令告警: 主机ID={host_id}, 命令={command}")
        host = await sync_to_async(Host.objects.get)(id=host_id)
        logger.debug(f"获取到主机: {host.name}")
        
        alerts = await sync_to_async(list)(CommandAlert.objects.filter(hosts__contains=str(host.id), is_active=True))
        logger.debug(f"找到 {len(alerts)} 个相关的告警规则")
        
        for alert in alerts:
            logger.debug(f"检查告警规则: {alert.name}, 匹配类型: {alert.match_type}")
            try:
                command_rules = json.loads(alert.command_rule)
            except json.JSONDecodeError:
                logger.error(f"解析命令规则失败: {alert.command_rule}")
                continue

            if not isinstance(command_rules, list):
                command_rules = [command_rules]

            logger.debug(f"解析后的命令规则: {command_rules}")

            if alert.match_type == 'exact':
                logger.debug(f"精确匹配规则: {command_rules}")
                if command in command_rules:
                    logger.warning(f"命令 '{command}' 触发了精确匹配告警: {alert.name}")
                    await send_alert_notification(alert.id, command, username, host.name)
                    return True
            elif alert.match_type == 'fuzzy':
                logger.debug(f"模糊匹配规则: {command_rules}")
                for pattern in command_rules:
                    if re.search(pattern.strip(), command):
                        logger.warning(f"命令 '{command}' 触发了模糊匹配告警: {alert.name}")
                        await send_alert_notification(alert.id, command, username, host.name)
                        return True
        
        logger.debug(f"命令 '{command}' 未触发任何告警")
        return False
    except Exception as e:
        logger.error(f"检查命令告警时发生错误: {str(e)}")
        return False
