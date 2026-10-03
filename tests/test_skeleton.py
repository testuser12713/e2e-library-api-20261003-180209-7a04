import asyncio
import json

import pytest
from fastapi import HTTPException

from app.config import settings
from app.dependencies import require_api_key
from app.errors import error_response


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_error_response_shape():
    response = error_response(422, "validation", "Request validation failed")
    body = json.loads(response.body)
    assert response.status_code == 422
    assert body == {"detail": {"code": "validation", "message": "Request validation failed"}}


def test_require_api_key_rejects_missing():
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(require_api_key(None))
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == {
        "code": "unauthorized",
        "message": "Missing or invalid API key",
    }


def test_require_api_key_rejects_wrong():
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(require_api_key("not-the-key"))
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == {
        "code": "unauthorized",
        "message": "Missing or invalid API key",
    }


def test_require_api_key_accepts_correct():
    asyncio.run(require_api_key(settings.api_key))
