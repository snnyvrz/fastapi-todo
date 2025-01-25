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
