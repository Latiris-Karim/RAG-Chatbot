from fastapi import FastAPI
import logging
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from src.routes.router import router


load_dotenv()
logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)
limiter = Limiter(key_func=get_remote_address, default_limits=["10/minute"])


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)


#get_secrets()
app.include_router(router)

