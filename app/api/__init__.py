import logging

from flask import Flask, jsonify
from flask_cors import CORS

from app.core.config import settings
from app.core.db import session_scope
from app.core.errors import AppError

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
log = logging.getLogger(__name__)


def create_app() -> Flask:
    from app.api import auth, deps, legal, news, questions, sources

    app = Flask(__name__)
    app.config["JSON_AS_ASCII"] = False
    CORS(app, supports_credentials=True, origins=[settings.public_base_url])

    for blueprint in (auth.bp, news.bp, questions.bp, legal.bp, sources.bp):
        app.register_blueprint(blueprint)

    app.teardown_appcontext(deps.close_session)

    @app.errorhandler(AppError)
    def handle_app_error(exc: AppError):
        return jsonify({"error": {"code": exc.code, "message": exc.message}}), exc.status

    @app.errorhandler(404)
    def handle_404(_):
        return jsonify({"error": {"code": "not_found", "message": "Ресурс не найден"}}), 404

    @app.errorhandler(Exception)
    def handle_unexpected(exc: Exception):
        log.exception("Необработанная ошибка")
        return (
            jsonify({"error": {"code": "internal_error", "message": "Внутренняя ошибка сервера"}}),
            500,
        )

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    _sync_sources()
    return app


def _sync_sources() -> None:
    from app.services import sources as sources_service

    try:
        with session_scope() as session:
            sources_service.sync_from_yaml(session)
    except Exception:
        log.exception("Не удалось синхронизировать источники при старте")


app = create_app()
