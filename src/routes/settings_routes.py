from fastapi import APIRouter, Depends, HTTPException
from src.utils.jwt_handler import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/settings", tags=["settings"])

