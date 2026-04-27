from __future__ import annotations

import smtplib
from email.message import EmailMessage


class GmailClient:
    def __init__(self, sender_email: str, app_password: str) -> None:
        self.sender_email = sender_email
        self.app_password = app_password

    def enviar_email(self, destinatario: str, assunto: str, corpo: str) -> None:
        mensagem = EmailMessage()
        mensagem["From"] = self.sender_email
        mensagem["To"] = destinatario
        mensagem["Subject"] = assunto
        mensagem.set_content(corpo)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(self.sender_email, self.app_password)
            smtp.send_message(mensagem)
