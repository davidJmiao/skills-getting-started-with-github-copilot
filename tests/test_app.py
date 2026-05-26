import sys
import importlib
from pathlib import Path

from fastapi.testclient import TestClient


def load_app_module():
    """Ensure the src folder is importable, import and reload the app module."""
    src_dir = Path(__file__).parent.parent / "src"
    src_str = str(src_dir)
    if src_str not in sys.path:
        sys.path.insert(0, src_str)

    import app as app_module
    importlib.reload(app_module)
    return app_module


def test_get_activities():
    app_module = load_app_module()
    client = TestClient(app_module.app)

    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    app_module = load_app_module()
    client = TestClient(app_module.app)

    activity = "Chess Club"
    email = "teststudent@example.com"

    # ensure not present initially
    resp = client.get("/activities")
    assert email not in resp.json()[activity]["participants"]

    # sign up
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert resp.json()["message"] == f"Signed up {email} for {activity}"

    # verify added
    resp = client.get("/activities")
    assert email in resp.json()[activity]["participants"]

    # duplicate sign-up should fail
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 400

    # unregister
    resp = client.delete(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert resp.json()["message"] == f"Unregistered {email} from {activity}"

    # verify removed
    resp = client.get("/activities")
    assert email not in resp.json()[activity]["participants"]


def test_signup_nonexistent_activity():
    app_module = load_app_module()
    client = TestClient(app_module.app)

    resp = client.post("/activities/NoSuchActivity/signup", params={"email": "a@b.com"})
    assert resp.status_code == 404


def test_unregister_missing_participant():
    app_module = load_app_module()
    client = TestClient(app_module.app)

    resp = client.delete("/activities/Programming Class/signup", params={"email": "not.registered@example.com"})
    assert resp.status_code == 404
