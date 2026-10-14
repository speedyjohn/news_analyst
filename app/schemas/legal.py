import json

from app.models import LegalRequest
from app.schemas.common import to_local


def legal_request(request: LegalRequest) -> dict:
    payload = json.loads(request.output_text) if request.output_text else None
    return {
        "id": request.id,
        "input_text": request.input_text,
        "verified": request.verified,
        "created_at": to_local(request.created_at),
        "note": payload if request.verified else None,
        "error": (payload or {}).get("error") if not request.verified else None,
        "failed": bool((payload or {}).get("failed")) if not request.verified else False,
    }
