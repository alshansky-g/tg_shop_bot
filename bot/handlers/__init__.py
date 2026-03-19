from aiogram import Router

from .admin_private import router as admin_router
from .payments import router as payments_router
from .user_group import router as group_router
from .user_private import router as user_router

router = Router()

router.include_routers(
    admin_router,
    group_router,
    payments_router,
    user_router,
)
