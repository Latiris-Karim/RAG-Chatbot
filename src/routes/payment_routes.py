from fastapi import APIRouter

router = APIRouter(prefix='/payment', tags=["payment"])

@router.post("/subscribe")
async def subscribe():
    ...

@router.post("/unsubscribe")
async def unsubscribe():
    ...

#maybe refund route if on first 7 days?
@router.post("refund")
async def  refund():
    ...

