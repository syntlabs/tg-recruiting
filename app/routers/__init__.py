from aiogram import Router

from .client import router as client_router
from .staff import router as staff_router


router = Router(name=__name__)

router.include_routers(staff_router, client_router)
