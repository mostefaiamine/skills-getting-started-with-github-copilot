import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store original activities
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Soccer Team": {
            "description": "Outdoor soccer training and intramural matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 22,
            "participants": ["mason@mergington.edu", "ava@mergington.edu"]
        },
        "Basketball Club": {
            "description": "Skill drills, scrimmages, and local tournaments",
            "schedule": "Wednesdays and Fridays, 4:30 PM - 6:30 PM",
            "max_participants": 15,
            "participants": ["liam@mergington.edu", "isabella@mergington.edu"]
        },
        "Art Club": {
            "description": "Open studio time for drawing, painting and mixed media",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["chloe@mergington.edu", "noah@mergington.edu"]
        },
        "Drama Club": {
            "description": "Theatre production, improvisation and acting workshops",
            "schedule": "Thursdays, 3:30 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu", "mia@mergington.edu"]
        },
        "Debate Team": {
            "description": "Competitive debating, public speaking and research skills",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["oliver@mergington.edu", "sophia@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Hands-on science challenges and regional competitions",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["ethan@mergington.edu", "amelia@mergington.edu"]
        }
    }
    # Reset activities
    activities.clear()
    activities.update(original_activities)
    yield

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    # Check structure
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)

def test_signup_success():
    response = client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "test@mergington.edu" in data["message"]
    assert "Chess Club" in data["message"]
    # Check that participant was added
    response = client.get("/activities")
    data = response.json()
    assert "test@mergington.edu" in data["Chess Club"]["participants"]

def test_signup_activity_not_found():
    response = client.post("/activities/Nonexistent%20Activity/signup?email=test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]

def test_signup_already_signed_up():
    # First signup
    client.post("/activities/Chess%20Club/signup?email=duplicate@mergington.edu")
    # Second signup should fail
    response = client.post("/activities/Chess%20Club/signup?email=duplicate@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]

def test_signup_activity_full():
    # Fill up an activity
    activity = "Art Club"
    max_part = activities[activity]["max_participants"]
    current = len(activities[activity]["participants"])
    for i in range(max_part - current):
        email = f"fill{i}@mergington.edu"
        client.post(f"/activities/{activity.replace(' ', '%20')}/signup?email={email}")
    # Now try to add one more
    response = client.post(f"/activities/{activity.replace(' ', '%20')}/signup?email=overflow@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "full" in data["detail"]

def test_unregister_success():
    # First signup
    client.post("/activities/Programming%20Class/signup?email=unregister@mergington.edu")
    # Then unregister
    response = client.delete("/activities/Programming%20Class/unregister?email=unregister@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "unregister@mergington.edu" in data["message"]
    assert "Programming Class" in data["message"]
    # Check that participant was removed
    response = client.get("/activities")
    data = response.json()
    assert "unregister@mergington.edu" not in data["Programming Class"]["participants"]

def test_unregister_activity_not_found():
    response = client.delete("/activities/Nonexistent%20Activity/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]

def test_unregister_not_signed_up():
    response = client.delete("/activities/Chess%20Club/unregister?email=notsignedup@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "not signed up" in data["detail"]