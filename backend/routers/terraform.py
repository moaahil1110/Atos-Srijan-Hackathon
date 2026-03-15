# POST /terraform  (stretch goal)
# Calls: services/terraform_service.py

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("/terraform")
async def terraform_endpoint():
    raise HTTPException(
        status_code=501,
        detail="Terraform export is a stretch goal — not yet implemented",
    )
