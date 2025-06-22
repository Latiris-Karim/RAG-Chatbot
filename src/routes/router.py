from fastapi import APIRouter
from src.routes import chat_routes
from src.routes import user_routes
from src.routes import subscription_routes

router = APIRouter()

router.include_router(chat_routes.router)
router.include_router(user_routes.router)
router.include_router(subscription_routes.router)
router.include_router(subscription_routes.webhook_router)
