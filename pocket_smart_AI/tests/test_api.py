def register_user(client):

    return client.post(
        "/api/auth/register",
        data={
            "name": "Test User",
            "email": "test@example.com",
            "password": "password123",
        },
    )


def login_user(client):

    return client.post(
        "/api/auth/login",
        data={
            "email": "test@example.com",
            "password": "password123",
        },
    )


def test_health(client):

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"


def test_register_and_login(client):

    response = register_user(client)

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    response = login_user(client)

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True


def test_home_recommendation(client):

    response = client.post(
        "/api/generate-home",
        json={
            "budget": 100000,
            "rooms": [
                "Living Room",
                "Bedroom",
            ],
            "style": "modern",
            "items": [
                {
                    "category": "Lights",
                    "quantity": 4,
                }
            ],
            "city": "Chennai",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["planner"] == "home"

    assert len(
        data["recommendations"]
    ) > 0


def test_party_recommendation(client):

    response = client.post(
        "/api/generate-party",
        json={
            "budget": 50000,
            "guests": 50,
            "event_type": "birthday",
            "venue_type": "home",
            "city": "Chennai",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["planner"] == "party"

    assert len(
        data["recommendations"]
    ) > 0


def test_jewelry_recommendation(client):

    response = client.post(
        "/api/generate-jewelry",
        data={
            "budget": "15000",
            "occasion": "wedding",
            "style": "elegant",
            "metal": "gold",
            "outfit_description": (
                "Green saree with gold border"
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["planner"] == "jewelry"

    assert len(
        data["recommendations"]
    ) > 0


def test_history(client):

    register_user(client)

    response = client.post(
        "/api/generate-home",
        json={
            "budget": 50000,
            "rooms": [
                "Living Room"
            ],
            "style": "modern",
            "items": [],
            "city": "Chennai",
        },
    )

    assert response.status_code == 200

    response = client.get(
        "/api/history"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert len(
        data["history"]
    ) >= 1