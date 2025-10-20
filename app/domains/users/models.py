from sqlalchemy import String, DateTime, ForeignKey, CheckConstraint, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.helpers.bases import BaseWithId
from datetime import datetime
from typing import Optional, List


class User(BaseWithId):
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hash_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)
    role: Mapped[str] = mapped_column(default='user')
    status: Mapped[Optional[str]] = mapped_column(default='active', nullable=True)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    campaign: Mapped[Optional[List['Campaign']]] = relationship(back_populates='creator',cascade='all, delete-orphan',foreign_keys='Campaign.creator_id', lazy='selectin')
    campaign_depended: Mapped[Optional[List['Campaign']]] = relationship(back_populates='user_depend_on', cascade='all',foreign_keys='Campaign.user_depend_id')
    user_profile: Mapped[Optional['UserProfile']] = relationship(back_populates='user', cascade='all, delete-orphan')
    donation: Mapped[Optional[List['Donation']]] = relationship(back_populates='user', cascade='all')

    

class UserProfile(BaseWithId):
    full_name: Mapped[Optional[str]] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(unique=True)
    phone: Mapped[Optional[str]] = mapped_column(String(15), nullable=True)
    logo: Mapped[Optional[str]] = mapped_column(nullable=True)
    user: Mapped['User'] = relationship(back_populates='user_profile')
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))

    





