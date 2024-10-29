import requests
import logging
import json
from apps.models import AlertContact, CommandAlert, Host
from asgiref.sync import sync_to_async

logger = logging.getLogger('log')

def get_dingtalk_message(username, hostname, host_ip, command, command_alert):
    """钉钉消息模板"""
    return f"""## 🚨 命令告警通知
---
> 检测到潜在的敏感操作，请及时关注！

**📌 执行详情：**
- 👤 执行用户：**{username}**
- 🖥️ 执行主机：**{hostname}** (IP: {host_ip})
- 🔍 匹配类型：**{'精准匹配' if command_alert.match_type == 'exact' else '模糊匹配'}**
- 🛠️ 执行命令：`{command}`
- 🚫 是否阻止：**{'是' if command_alert.is_active else '否'}**
- ⚠️ 触发规则：**{command_alert.name}**
  - 规则详情：`{command_alert.command_rule}`

请相关同学尽快核实此操作的合法性和必要性。如有异常，请立即采取相应的安全措施。

*此为自动告警，请勿回复。*
"""

def get_wecom_message(username, hostname, host_ip, command, command_alert):
    """企业微信消息模板"""
    return f"""## 🚨 命令告警通知
检测到潜在的敏感操作，请及时关注！
📌 执行详情：
> 👤 执行用户：{username}
> 🖥️ 执行主机：<font color="">{hostname}</font> (IP: {host_ip})
> 🔍 匹配类型：<font color="">{'精准匹配' if command_alert.match_type == 'exact' else '模糊匹配'}</font>
> 🛠️ 执行命令：<font color="info">{command}</font>
> 🚫 是否阻止：{'是' if command_alert.is_active else '否'}
> ⚠️ 触发规则：<font color="">{command_alert.name}</font>
    > 规则详情：<font color="">{command_alert.command_rule}</font>

请相关同学尽快核实此操作的合法性和必要性。如有异常，请立即采取相应的安全措施。

*此为自动告警，请勿回复。*
"""

def get_feishu_message(username, hostname, host_ip, command, command_alert):
    """飞书消息模板"""
    return f"""**检测到潜在的敏感操作，请及时关注！**
---
**📌 执行详情**
- 👤 执行用户：<font color=''>{username}</font>
- 🖥️ 执行主机：<font color=''>{hostname}</font> (IP: {host_ip})
- 🔍 匹配类型：<font color=''>{'精准匹配' if command_alert.match_type == 'exact' else '模糊匹配'}</font>
- 🛠️ 执行命令：<font color='red'>{command}</font>
- 🚫 是否阻止：{'是' if command_alert.is_active else '否'}
- ⚠️ 触发规则：<font color=''>{command_alert.name}</font>
    - 规则详情：{command_alert.command_rule}
    
请相关同学尽快核实此操作的合法性和必要性。如有异常，请立即采取相应的安全措施。
*此为自动告警，请勿回复。*
"""

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

            logger.info(f"准备发送告警通知到 {notify_type}")
            logger.debug(f"Webhook URL: {webhook_url}")

            try:
                if notify_type == '钉钉':
                    message = get_dingtalk_message(username, hostname, host.network, command, command_alert)
                    payload = {
                        "msgtype": "markdown",
                        "markdown": {
                            "title": "🚨 命令告警通知",
                            "text": message
                        },
                        "at": {
                            "isAtAll": True
                        }
                    }
                elif notify_type == '企微':
                    message = get_wecom_message(username, hostname, host.network, command, command_alert)
                    payload = {
                        "msgtype": "markdown",
                        "markdown": {
                            "content": message
                        }
                    }
                elif notify_type == '飞书':
                    message = get_feishu_message(username, hostname, host.network, command, command_alert)
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

                logger.debug(f"请求载荷: {json.dumps(payload, ensure_ascii=False, indent=2)}")
                response = requests.post(webhook_url, json=payload, timeout=10)
                logger.debug(f"响应状态码: {response.status_code}")
                logger.debug(f"响应内容: {response.text}")

                if response.status_code == 200:
                    response_json = response.json()
                    logger.info(f"成功发送告警通知到 {notify_type}")
                    logger.debug(f"响应详情: {json.dumps(response_json, ensure_ascii=False, indent=2)}")
                    
                    if notify_type == '企微':
                        if response_json.get('errcode') == 0:
                            logger.info("企业微信通知发送成功")
                        else:
                            logger.error(f"企业微信通知发送失败: {response_json.get('errmsg', '未知错误')}")
                else:
                    logger.error(f"发送告警通知到 {notify_type} 失败: HTTP {response.status_code}")
                    logger.error(f"错误响应: {response.text}")

            except requests.exceptions.Timeout:
                logger.error(f"发送告警通知到 {notify_type} 超时")
            except requests.exceptions.RequestException as e:
                logger.error(f"发送告警通知到 {notify_type} 时发生网络错误: {str(e)}")
            except json.JSONDecodeError:
                logger.error(f"解析 {notify_type} 响应JSON失败: {response.text}")

    except CommandAlert.DoesNotExist:
        logger.error(f"未找到ID为 {command_alert_id} 的命令告警规则")
    except Host.DoesNotExist:
        logger.error(f"未找到主机名为 {hostname} 的主机")
    except Exception as e:
        logger.error(f"发送告警通知时发生错误: {str(e)}")
