from aiogram import Router

from .client import router as client_callback_query_router
from .staff import router as staff_callback_query_router


router = Router(name=__name__)

router.include_routers(
    staff_callback_query_router, client_callback_query_router
)
