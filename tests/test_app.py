def register(client):

    response = client.post(

        "/api/auth/register",

        json={
            "name":
                "Test User",

            "email":
                "test@example.com",

            "password":
                "password123",
        },
    )

    assert response.status_code == 200

    return response


def test_health(client):

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert (
        response.json()["status"]
        == "ok"
    )


def test_register_and_me(client):

    register(client)

    response = client.get(
        "/api/auth/me"
    )

    assert response.status_code == 200

    assert (
        response.json()["email"]
        == "test@example.com"
    )


def test_login_logout(client):

    register(client)

    client.post(
        "/api/auth/logout"
    )

    assert (
        client.get(
            "/api/auth/me"
        ).status_code
        == 401
    )


    response = client.post(

        "/api/auth/login",

        json={
            "email":
                "test@example.com",

            "password":
                "password123",
        },
    )

    assert response.status_code == 200

    assert (
        client.get(
            "/api/auth/me"
        ).status_code
        == 200
    )


def test_home_planner_fallback(
    client
):

    register(client)

    response = client.post(

        "/api/generate-home",

        json={

            "budget":
                50000,

            "room":
                "Living Room",

            "style":
                "Modern",

            "occupants":
                3,

            "items":
                [
                    "sofa",
                    "light"
                ],

            "priorities":
                [
                    "comfort"
                ],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["planner"]
        == "home"
    )

    assert (
        data["source"]
        == "fallback"
    )

    assert (
        data["budget"]
        == 50000
    )


def test_party_planner(client):

    register(client)

    response = client.post(

        "/api/generate-party",

        json={

            "budget":
                30000,

            "guests":
                30,

            "event_type":
                "Birthday",

            "venue":
                "Indoor",

            "food_preference":
                "Mixed",

            "city":
                "Chennai",
        },
    )

    assert response.status_code == 200

    assert (
        response.json()["planner"]
        == "party"
    )


def test_jewelry_planner(
    client
):

    register(client)

    response = client.post(

        "/api/generate-jewelry",

        data={

            "budget":
                "10000",

            "occasion":
                "Wedding",

            "style":
                "Elegant",

            "metal":
                "Any",

            "outfit_notes":
                "Blue outfit",
        },
    )

    assert response.status_code == 200

    assert (
        response.json()["planner"]
        == "jewelry"
    )


def test_history(client):

    register(client)

    client.post(

        "/api/generate-home",

        json={

            "budget":
                10000,

            "room":
                "Bedroom",

            "style":
                "Minimal",

            "occupants":
                2,

            "items":
                [],

            "priorities":
                [],
        },
    )


    response = client.get(
        "/api/history"
    )

    assert response.status_code == 200

    assert len(
        response.json()
    ) == 1


def test_protected_endpoint(
    client
):

    response = client.get(
        "/api/session-info"
    )

    assert response.status_code == 401