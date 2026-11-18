from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel, EmailStr

from webapp.core.email import send_email
from webapp.core.background import log_event

router = APIRouter(
    prefix="/email",
    tags=["Email"]
)


class EmailRequest(BaseModel):

    recipient: EmailStr
    subject: str
    body: str


@router.post("/send")
async def send_mail(
    data: EmailRequest,
    background_tasks: BackgroundTasks
):

    background_tasks.add_task(
        send_email,
        data.recipient,
        data.subject,
        data.body
    )

    background_tasks.add_task(
        log_event,
        "EMAIL_SCHEDULED",
        data.recipient
    )

    return {
        "message": "Email sending has been scheduled"
    }