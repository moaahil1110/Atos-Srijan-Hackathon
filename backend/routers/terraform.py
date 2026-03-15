# POST /terraform — Export config as Terraform file (stretch goal)
# Calls: services/terraform_service.py

from fastapi import APIRouter, HTTPException, Body
from services.terraform_service import export_terraform

router = APIRouter()


@router.post("/terraform")
async def terraform_endpoint(body: dict = Body(...)):
    """
    Export the generated configuration into Terraform HCL format.
    Requires sessionId in the JSON body.
    """
    try:
        session_id = body["sessionId"]
        result = export_terraform(session_id)
        return result
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing field: {e}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
