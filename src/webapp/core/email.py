import smtplib

from email.message import EmailMessage

from webapp.core.config import settings


def send_email(
    recipient: str,
    subject: str,
    body: str
):

    message = EmailMessage()

    message["From"] = settings.MAIL_FROM
    message["To"] = recipient
    message["Subject"] = subject

    message.set_content(body)

    with smtplib.SMTP(
        settings.MAIL_SERVER,
        settings.MAIL_PORT
    ) as server:

        server.starttls()

        server.login(
            settings.MAIL_USERNAME,
            settings.MAIL_PASSWORD
        )

        server.send_message(message)