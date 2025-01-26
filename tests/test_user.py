from fastapi.testclient import TestClient


def test_root(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "Sina"}


def test_signup(client: TestClient):
    response = client.post(
        "/signup/",
        json={
            "username": "sinaniya",
            "password": "12345678",
            "confirm_password": "12345678",
        },
    )
    assert response.status_code == 200
    assert response.json()["username"] == "sinaniya"


def test_signup_existing_user(client: TestClient):
    response = client.post(
        "/signup/",
        json={
            "username": "sinaniya",
            "password": "12345678",
            "confirm_password": "12345678",
        },
    )
    assert response.status_code == 409
    assert response.json() == {"detail": "Username already exists"}


def test_user_signin(client: TestClient):
    response = client.post(
        "/signin/",
        json={
            "username": "sinaniya",
            "password": "12345678",
        },
    )
    assert response.status_code == 200
    assert response.json()["username"] == "sinaniya"


def test_user_signin_not_found(client: TestClient):
    response = client.post(
        "/signin/",
        json={
            "username": "sina",
            "password": "12345678",
        },
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_user_signin_wrong_password(client: TestClient):
    response = client.post(
        "/signin/",
        json={
            "username": "sinaniya",
            "password": "123456789",
        },
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect password"}
