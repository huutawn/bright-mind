from sqlalchemy import String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.helpers.bases import BareBaseModel
from datetime import datetime
from typing import Optional, List


class User(BareBaseModel):
    full_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(unique=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(15), nullable=True)
    hash_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)
    role: Mapped[str] = mapped_column(default='user')
    logo: Mapped[Optional[str]] = mapped_column(nullable=True)
    status: Mapped[Optional[str]] = mapped_column(default='active', nullable=True)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    supporter: Mapped[Optional['Supporter']] = relationship(back_populates='user', cascade='all, delete-orphan')
    campaign: Mapped[List['Campaign']] = relationship(back_populates='creator',cascade='all, delete-orphan')
    campaign_depended: Mapped[List['Campaign']] = relationship(back_populates='user_depend_on', cascade='all')

class AnonymousUser(BareBaseModel):
    full_name: Mapped[str] = mapped_column(String(100),nullable=True)
    email: Mapped[str] = mapped_column(nullable=True)
    phone: Mapped[str] = mapped_column(String(15), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    role: Mapped[str] = mapped_column(default='user')
    supporter: Mapped[Optional['Supporter']] = relationship(back_populates='anonymous',cascade='all, delete-orphan')

class Supporter(BareBaseModel):
    full_name: Mapped[str] = mapped_column(String(100), nullable=True)
    email: Mapped[str] = mapped_column(nullable=True)
    phone: Mapped[str] = mapped_column(String(15), nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    user: Mapped[Optional['User']] = relationship(back_populates='supporter')
    anonymous_id: Mapped[int] = mapped_column(ForeignKey('anonymous_user.id'))
    anonymous: Mapped[Optional['AnonymousUser']] = relationship(back_populates='supporter')

    __table_args__ = (
        CheckConstraint(
            '(user_id IS NOT NULL AND anonymous_id IS NULL) OR '
            '(user_id IS NULL AND anonymous_id IS NOT NULL)',
            name='ck_supporter_type'
        ),
    )



