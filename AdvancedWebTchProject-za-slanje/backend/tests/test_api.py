import os
import sys
from uuid import uuid4
from io import BytesIO

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


@pytest.fixture(scope="session")
def client(tmp_path_factory):
    database = tmp_path_factory.mktemp("database") / "test.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{database}"
    from app import app as application
    application.config.update(TESTING=True)
    with application.test_client() as test_client:
        yield test_client


def register(client, username=None):
    username = username or f"reader_{uuid4().hex[:8]}"
    response = client.post("/api/register", json={
        "firstName": "Test", "lastName": "Reader", "email": f"{username}@test.local",
        "username": username, "password": "Secret123",
    })
    assert response.status_code == 201
    return response.get_json()["user"]


def login(client, username="admin", password="admin123"):
    response = client.post("/api/login", json={"username": username, "password": password})
    assert response.status_code == 200
    return response.get_json()["user"]


def headers(user):
    return {"X-User-Id": str(user["id"])}


def test_health_and_initial_books(client):
    assert client.get("/api/health").status_code == 200
    response = client.get("/api/books")
    assert response.status_code == 200
    assert len(response.get_json()) == 5


def test_register_validation_and_duplicate(client):
    user = register(client, "reader_duplicate")
    missing = client.post("/api/register", json={"username": "missing"})
    duplicate = client.post("/api/register", json={
        "firstName": "Other", "lastName": "Reader", "email": "reader_duplicate@test.local",
        "username": "other", "password": "Secret123",
    })
    assert missing.status_code == 400
    assert duplicate.status_code == 409


def test_login_success_and_failure(client):
    user = register(client)
    assert client.post("/api/login", json={"username": "missing", "password": "Secret123"}).get_json()["message"] == "Username ne postoji."
    assert client.post("/api/login", json={"username": user["username"], "password": "wrong"}).status_code == 401
    assert client.post("/api/login", json={"username": user["username"], "password": "Secret123"}).status_code == 200


def test_password_validation_and_change(client):
    base = {"firstName": "Weak", "lastName": "User", "email": "weak@test.local", "username": "weak_user"}
    exact_minimum = client.post("/api/register", json={**base, "email": "exact@test.local", "username": "exact_minimum", "password": "Abcdef12"})
    assert exact_minimum.status_code == 201
    assert client.post("/api/register", json={**base, "password": "Short1"}).status_code == 400
    assert client.post("/api/register", json={**base, "email": "lower@test.local", "username": "lower_user", "password": "lowercase123"}).status_code == 400
    assert client.post("/api/register", json={**base, "email": "number@test.local", "username": "number_user", "password": "NoNumberHere"}).status_code == 400
    user = register(client, "password_user")
    user_headers = headers(user)
    assert client.put("/api/profile/password", json={"oldPassword": "wrong", "newPassword": "NewSecret123", "confirmPassword": "NewSecret123"}, headers=user_headers).status_code == 400
    assert client.put("/api/profile/password", json={"oldPassword": "Secret123", "newPassword": "NewSecret123", "confirmPassword": "Different123"}, headers=user_headers).status_code == 400
    assert client.put("/api/profile/password", json={"oldPassword": "Secret123", "newPassword": "NewSecret123", "confirmPassword": "NewSecret123"}, headers=user_headers).status_code == 200
    assert client.post("/api/login", json={"username": user["username"], "password": "NewSecret123"}).status_code == 200


def test_book_details_and_missing_book(client):
    user = register(client)
    assert client.get("/api/books/1", headers=headers(user)).get_json()["status"] == "not_read"
    assert client.get("/api/books/999", headers=headers(user)).status_code == 404


def test_status_requires_login_and_valid_book(client):
    assert client.put("/api/books/1/status", json={"status": "read"}).status_code == 401
    user = register(client)
    assert client.put("/api/books/999/status", headers=headers(user), json={"status": "read"}).status_code == 404
    assert client.put("/api/books/1/status", headers=headers(user), json={"status": "unknown"}).status_code == 400
    assert client.put("/api/books/1/status", headers=headers(user), json={"status": "read"}).status_code == 200


def test_profile_and_friend_routes(client):
    reader = register(client, "reader_one")
    friend = register(client, "reader_two")
    assert client.get("/api/profile", headers=headers(reader)).status_code == 200
    assert client.post("/api/friends", headers=headers(reader), json={"username": "missing"}).status_code == 404
    assert client.post("/api/friends", headers=headers(reader), json={"username": friend["username"]}).status_code == 201
    assert client.post("/api/friends", headers=headers(reader), json={"username": friend["username"]}).status_code == 409
    assert client.get("/api/friends", headers=headers(reader)).status_code == 200
    assert client.get("/api/friends/activities", headers=headers(reader)).status_code == 200
    assert client.delete(f"/api/friends/{friend['id']}", headers=headers(reader)).status_code == 200
    assert client.get("/api/friends", headers=headers(reader)).get_json() == []
    assert client.delete(f"/api/friends/{friend['id']}", headers=headers(reader)).status_code == 404
    assert client.get(f"/api/users/{friend['id']}/profile", headers=headers(reader)).status_code == 200
    assert client.get("/api/users/999/profile", headers=headers(reader)).status_code == 404


def test_admin_book_crud_and_permissions(client):
    user = register(client, "regular")
    admin = login(client)
    payload = {"title": "Uploaded", "author": "Author", "description": "Description", "isbn": "123"}
    assert client.post("/api/admin/books", headers=headers(user), data=payload).status_code == 403
    added = client.post("/api/admin/books", headers=headers(admin), data={**payload, "image": (BytesIO(b"image"), "cover.jpg")}, content_type="multipart/form-data")
    assert added.status_code == 201
    book_id = added.get_json()["id"]
    duplicate = client.post("/api/admin/books", headers=headers(admin), data=payload)
    assert duplicate.status_code == 409
    assert client.delete(f"/api/admin/books/{book_id}", headers=headers(admin)).status_code == 200
    assert client.delete("/api/admin/books/999", headers=headers(admin)).status_code == 404


def test_admin_rejects_oversized_image(client):
    admin = login(client)
    payload = {"title": "Oversized image", "author": "Author", "description": "Description", "isbn": "oversized"}
    oversized_image = BytesIO(b"x" * (5 * 1024 * 1024 + 1))
    response = client.post(
        "/api/admin/books",
        headers=headers(admin),
        data={**payload, "image": (oversized_image, "oversized.jpg")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert response.get_json()["message"] == "Slika je prevelika. Maksimalna veličina je 5 MB."


def test_admin_users_list_and_delete(client):
    user = register(client, "deletable_user")
    admin = login(client)
    assert client.get("/api/admin/users", headers=headers(user)).status_code == 403
    assert client.get("/api/admin/users", headers=headers(admin)).status_code == 200
    assert client.delete(f"/api/admin/users/{user['id']}", headers=headers(admin)).status_code == 200
    assert client.delete(f"/api/admin/users/{user['id']}", headers=headers(admin)).status_code == 404
    assert client.delete(f"/api/admin/users/{admin['id']}", headers=headers(admin)).status_code == 400


def test_cover_file_endpoint(client):
    response = client.get("/static/book-covers/placeholder_book_cover.jpeg")
    assert response.status_code == 200