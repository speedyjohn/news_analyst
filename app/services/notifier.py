import logging
import smtplib
import threading
from email.message import EmailMessage

from app.core.config import settings
from app.models import Question

log = logging.getLogger(__name__)


def _send(to: str, subject: str, body: str) -> None:
    if not settings.smtp_host:
        log.warning("SMTP не настроен, письмо для %s не отправлено", to)
        return
    message = EmailMessage()
    message["From"] = settings.smtp_from
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as smtp:
            if settings.smtp_tls:
                smtp.starttls()
            if settings.smtp_user:
                smtp.login(settings.smtp_user, settings.smtp_password)
            smtp.send_message(message)
        log.info("Письмо отправлено на %s", to)
    except Exception:
        log.exception("SMTP не принял письмо для %s", to)


def send_async(to: str, subject: str, body: str) -> None:
    threading.Thread(target=_send, args=(to, subject, body), daemon=True).start()


def notify_question_closed(question: Question) -> None:
    closing = question.closing_news
    link = f"{settings.public_base_url}/questions/{question.id}"
    body = (
        f"Здравствуйте!\n\n"
        f"Ваш вопрос закрыт официальной публикацией.\n\n"
        f"Вопрос: {question.text}\n\n"
        f"Ответ официального источника:\n{question.official_answer}\n\n"
        f"Публикация: {closing.title if closing else ''}\n"
        f"{closing.url if closing else ''}\n\n"
        f"Страница вопроса: {link}\n"
    )
    send_async(question.user.email, "Ваш вопрос закрыт официальным источником", body)
