from fastapi import APIRouter

router = APIRouter(prefix="/serviceable", tags=["misc"])

# Dummy pincode serviceability
PINCODES = {"560001", "560002", "110001"}

@router.get("/{pincode}")
def check_pincode(pincode: str):
    return {"serviceable": pincode in PINCODES}
