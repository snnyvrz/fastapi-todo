from fastapi.testclient import TestClient


def get_token(client: TestClient) -> str:
    response = client.post(
        "/auth/signup/",
        data={
            "username": "sinaniya",
            "password": "12345678",
        },
    )

    if response.status_code == 409:
        response = client.post(
            "/auth/signin/",
            data={
                "username": "sinaniya",
                "password": "12345678",
            },
        )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_me(client: TestClient):
    response = client.get("/auth/me/")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_me_authenticated(client: TestClient):
    access_token = get_token(client)
    response = client.get(
        "/auth/me/", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "sinaniya"


def test_signup(client: TestClient):
    response = client.post(
        "/auth/signup/",
        data={
            "username": "sinaniya2",
            "password": "12345678",
            "confirm_password": "12345678",
        },
    )
    assert response.status_code == 200
    assert response.json().get("access_token") is not None


def test_signup_existing_user(client: TestClient):
    response = client.post(
        "/auth/signup/",
        data={
            "username": "sinaniya",
            "password": "12345678",
            "confirm_password": "12345678",
        },
    )
    assert response.status_code == 409
    assert response.json() == {"detail": "Username already exists"}


def test_user_signin(client: TestClient):
    response = client.post(
        "/auth/signin/",
        data={
            "username": "sinaniya",
            "password": "12345678",
        },
    )
    assert response.status_code == 200
    assert response.json().get("access_token") is not None


def test_user_signin_not_found(client: TestClient):
    response = client.post(
        "/auth/signin/",
        data={
            "username": "sina",
            "password": "12345678",
        },
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_user_signin_wrong_password(client: TestClient):
    response = client.post(
        "/auth/signin/",
        data={
            "username": "sinaniya",
            "password": "123456789",
        },
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect password"}
