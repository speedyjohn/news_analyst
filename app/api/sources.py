from flask import Blueprint, jsonify

from app.api.deps import open_session
from app.schemas.sources import source_row
from app.services import sources as sources_service

bp = Blueprint("sources", __name__, url_prefix="/api/sources")


@bp.get("")
def listing():
    session = open_session()
    return jsonify({"items": [source_row(s) for s in sources_service.list_sources(session)]})
