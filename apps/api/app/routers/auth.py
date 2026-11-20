"""Account endpoints: sign-up (sign-in and sessions come in the next step)."""

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import User
from app.schemas import MessageOut, SignUpIn
from app.security import hash_password

router = APIRouter(prefix="/auth", tags=["auth"])

SessionDep = Annotated[Session, Depends(get_session)]

# The same reply whether or not the address was already registered, so that
# nobody can use this form to find out who has an account.
SIGNUP_REPLY = MessageOut(
    message="Your request was received. If this email address can be used, "
    "an account has been created."
)


@router.post("/signup", status_code=202)
def sign_up(data: SignUpIn, session: SessionDep) -> MessageOut:
    """Create an account. The reply never reveals whether the email was taken."""
    # Hash first, always, so the response takes about as long either way.
    password_hash = hash_password(data.password)

    already_exists = session.scalar(
        select(User.id).where(User.email == data.email))
    if already_exists is None:
        user = User(
            email=data.email,
            password_hash=password_hash,
            display_name=data.display_name,
            consent_at=datetime.now(timezone.utc),
        )
        session.add(user)
        try:
            session.commit()
        except IntegrityError:
            # Two sign-ups with the same address at the same moment: the
            # database allowed only one. Treat it like "already exists".
            session.rollback()
        else:
            # Development only: replaced by a real email in step 7D.
            print(
                f"[dev] account {user.id} created; verification email comes in 7D")

    return SIGNUP_REPLY
