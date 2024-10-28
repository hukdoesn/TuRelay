import requests
import logging
from apps.models import AlertContact, CommandAlert, Host
from asgiref.sync import sync_to_async

logger = logging.getLogger('log')

@sync_to_async
def send_alert_notification(command_alert_id, command, username, hostname):
    try:
        command_alert = CommandAlert.objects.get(id=command_alert_id)
        host = Host.objects.get(name=hostname)
        alert_contact_ids = command_alert.alert_contacts.split(',')
        alert_contacts = AlertContact.objects.filter(id__in=alert_contact_ids)

        for contact in alert_contacts:
            webhook_url = contact.webhook
            notify_type = contact.notify_type

            message = f"""## 🚨 命令告警通知
---
> 检测到潜在的敏感操作，请及时关注！

**📌 执行详情：**
- 👤 执行用户：**{username}**
- 🖥️ 执行主机：**{hostname}** (IP: {host.network})
- 🔍 匹配类型：**{'精准匹配' if command_alert.match_type == 'exact' else '模糊匹配'}**
- 🛠️ 执行命令：`{command}`
- 🚫 是否阻止：**{'否' if command_alert.is_active else '否'}**
- ⚠️ 触发规则：**{command_alert.name}**
  - 规则详情：`{command_alert.command_rule}`

请相关同学尽快核实此操作的合法性和必要性。如有异常，请立即采取相应的安全措施。

*此为自动告警，请勿回复。*
"""

            if notify_type == '钉钉':
                payload = {
                    "msgtype": "markdown",
                    "markdown": {
                        "title": "🚨 命令告警通知",
                        "text": message
                    },
                    "at": {
                        "isAtAll": True  # 添加@所有人功能
                    }
                }
            elif notify_type == '企业微信':
                payload = {
                    "msgtype": "markdown",
                    "markdown": {
                        "content": message
                    }
                }
            elif notify_type == '飞书':
                payload = {
                    "msg_type": "interactive",
                    "card": {
                        "elements": [{
                            "tag": "markdown",
                            "content": message
                        }],
                        "header": {
                            "title": {
                                "content": "🚨 命令告警通知",
                                "tag": "plain_text"
                            },
                            "template": "red"
                        }
                    }
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
    except Host.DoesNotExist:
        logger.error(f"未找到主机名为 {hostname} 的主机")
    except Exception as e:
        logger.error(f"发送告警通知时发生错误: {str(e)}")
