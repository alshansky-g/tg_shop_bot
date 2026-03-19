from sqlalchemy import DateTime, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from bot.config import config

engine = create_async_engine(url=config.database_url, echo=config.log_level.upper() == 'DEBUG')
session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        fields = ', '.join(
            [
                f'{k}={v}'
                for k, v in self.__dict__.items()
                if not any(k.startswith(prefix) for prefix in ['_', 'cr', 'up'])
            ]
        )
        return f'<{type(self).__name__}: {fields}>'
