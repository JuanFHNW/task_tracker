"""Tests for AuthService."""

import pytest

from task_tracker_app.services.auth_service import AuthService


def test_register_then_authenticate(database):
    service = AuthService(database)
    service.register("bob", "hunter2")

    user = service.authenticate("bob", "hunter2")
    assert user is not None
    assert user.username == "bob"


def test_authenticate_returns_none_on_wrong_password(database):
    service = AuthService(database)
    service.register("bob", "hunter2")

    assert service.authenticate("bob", "wrong") is None


def test_authenticate_returns_none_for_unknown_user(database):
    service = AuthService(database)
    assert service.authenticate("nobody", "x") is None


def test_register_rejects_duplicate(database):
    service = AuthService(database)
    service.register("bob", "hunter2")
    with pytest.raises(ValueError):
        service.register("bob", "other")
