from fastapi import APIRouter

router = APIRouter()

@router.get("/ready")
def ready():
    return {"ready": True}

@router.get("/live")
def live():
    return {"live": True}
