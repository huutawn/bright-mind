
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# Thay bằng chuỗi kết nối của bạn
DATABASE_URL = settings.DATABASE_URL

# Tạo engine và session maker
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

# Dependency để cung cấp DB Session cho mỗi request
async def get_db() -> AsyncGenerator[async_sessionmaker, None]:
    async with AsyncSessionLocal() as session:
        yield session