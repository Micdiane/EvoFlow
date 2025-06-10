"""
邮件发送Agent
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List
from decimal import Decimal

from .base import BaseAgent, AgentResult, AgentError


class EmailSenderAgent(BaseAgent):
    """邮件发送Agent"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="EmailSenderAgent",
            agent_type="communication",
            capabilities=["email_sending", "notification"],
            config=config
        )
        self.smtp_server = self.config.get("smtp_server", "smtp.gmail.com")
        self.smtp_port = self.config.get("smtp_port", 587)
        self.use_tls = self.config.get("use_tls", True)
    
    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> AgentResult:
        """执行邮件发送"""
        sender_email = input_data.get("sender_email")
        sender_password = input_data.get("sender_password")
        recipients = input_data.get("recipients", [])
        subject = input_data.get("subject", "")
        body = input_data.get("body", "")
        html_body = input_data.get("html_body")
        
        try:
            # 发送邮件
            sent_count = await self._send_email(
                sender_email=sender_email,
                sender_password=sender_password,
                recipients=recipients,
                subject=subject,
                body=body,
                html_body=html_body
            )
            
            return AgentResult(
                success=True,
                data={
                    "sender": sender_email,
                    "recipients": recipients,
                    "subject": subject,
                    "sent_count": sent_count,
                    "message": f"Successfully sent {sent_count} emails"
                },
                metadata={
                    "smtp_server": self.smtp_server,
                    "smtp_port": self.smtp_port,
                    "use_tls": self.use_tls
                }
            )
            
        except Exception as e:
            raise AgentError(f"Email sending failed: {str(e)}")
    
    async def _send_email(
        self,
        sender_email: str,
        sender_password: str,
        recipients: List[str],
        subject: str,
        body: str,
        html_body: str = None
    ) -> int:
        """发送邮件"""
        
        # 创建邮件消息
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = ", ".join(recipients)
        
        # 添加文本内容
        text_part = MIMEText(body, "plain", "utf-8")
        message.attach(text_part)
        
        # 添加HTML内容（如果提供）
        if html_body:
            html_part = MIMEText(html_body, "html", "utf-8")
            message.attach(html_part)
        
        try:
            # 连接SMTP服务器
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            
            if self.use_tls:
                server.starttls()
            
            # 登录
            server.login(sender_email, sender_password)
            
            # 发送邮件
            text = message.as_string()
            server.sendmail(sender_email, recipients, text)
            server.quit()
            
            return len(recipients)
            
        except smtplib.SMTPAuthenticationError:
            raise AgentError("SMTP authentication failed. Check email and password.")
        except smtplib.SMTPRecipientsRefused:
            raise AgentError("All recipients were refused. Check email addresses.")
        except smtplib.SMTPServerDisconnected:
            raise AgentError("SMTP server disconnected unexpectedly.")
        except Exception as e:
            raise AgentError(f"SMTP error: {str(e)}")
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据"""
        if not isinstance(input_data, dict):
            return False
        
        # 验证发送者邮箱
        sender_email = input_data.get("sender_email")
        if not sender_email or not isinstance(sender_email, str) or "@" not in sender_email:
            return False
        
        # 验证发送者密码
        sender_password = input_data.get("sender_password")
        if not sender_password or not isinstance(sender_password, str):
            return False
        
        # 验证收件人列表
        recipients = input_data.get("recipients", [])
        if not isinstance(recipients, list) or len(recipients) == 0:
            return False
        
        for recipient in recipients:
            if not isinstance(recipient, str) or "@" not in recipient:
                return False
        
        # 验证主题
        subject = input_data.get("subject", "")
        if not isinstance(subject, str):
            return False
        
        # 验证邮件内容
        body = input_data.get("body", "")
        if not isinstance(body, str):
            return False
        
        return True
    
    def get_cost_estimate(self, input_data: Dict[str, Any]) -> Decimal:
        """获取成本估算"""
        # 邮件发送成本通常很低，主要是服务器资源成本
        recipients = input_data.get("recipients", [])
        recipient_count = len(recipients)
        
        # 每封邮件成本约0.001美元
        cost_per_email = Decimal("0.001")
        
        return cost_per_email * Decimal(str(recipient_count))
