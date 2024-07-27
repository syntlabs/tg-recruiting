from aiogram import Router

from .admin import router as admin_router
from .client import router as client_router
from .staff import router as staff_router


router = Router(name=__name__)

router.include_routers(admin_router, staff_router, client_router)
