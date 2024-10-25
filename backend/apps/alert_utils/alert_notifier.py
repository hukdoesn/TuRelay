import requests
import logging
from apps.models import AlertContact, CommandAlert
from asgiref.sync import sync_to_async

logger = logging.getLogger('log')

@sync_to_async
def send_alert_notification(command_alert_id, command, username, hostname):
    try:
        command_alert = CommandAlert.objects.get(id=command_alert_id)
        alert_contact_ids = command_alert.alert_contacts.split(',')
        alert_contacts = AlertContact.objects.filter(id__in=alert_contact_ids)

        for contact in alert_contacts:
            webhook_url = contact.webhook
            notify_type = contact.notify_type

            message = f"告警通知:\n用户 {username} 在主机 {hostname} 上执行了命令: {command}\n这触发了告警规则: {command_alert.name}"

            if notify_type == '钉钉':
                payload = {
                    "msgtype": "text",
                    "text": {"content": message}
                }
            elif notify_type == '企业微信':
                payload = {
                    "msgtype": "text",
                    "text": {"content": message}
                }
            elif notify_type == '飞书':
                payload = {
                    "msg_type": "text",
                    "content": {"text": message}
                }
            else:
                logger.error(f"不支持的通知类型: {notify_type}")
                continue

            response = requests.post(webhook_url, json=payload)
            if response.status_code == 200:
                logger.info(f"成功发送告警通知到 {notify_type}")
            else:
                logger.error(f"发送告警通知到 {notify_type} 失败: {response.text}")

    except CommandAlert.DoesNotExist:
        logger.error(f"未找到ID为 {command_alert_id} 的命令告警规则")
    except Exception as e:
        logger.error(f"发送告警通知时发生错误: {str(e)}")
