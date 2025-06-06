from fastapi import APIRouter
from src.routes import chat_routes
from src.routes import user_routes
from src.routes import payment_routes

router = APIRouter()

router.include_router(chat_routes.router)
router.include_router(user_routes.router)
router.include_router(payment_routes.router)
