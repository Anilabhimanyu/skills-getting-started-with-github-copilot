import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_root_redirect():
    """Test that root endpoint redirects to static index.html"""
    # Arrange
    expected_url = "/static/index.html"
    
    # Act
    response = client.get("/", follow_redirects=False)
    
    # Assert
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == expected_url


def test_get_activities():
    """Test retrieving all activities"""
    # Arrange
    # (No specific setup needed as data is predefined)
    
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    # Verify structure of one activity
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_signup_success():
    """Test successful signup for an activity"""
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Signed up {email} for {activity_name}" in data["message"]
    
    # Verify participant was added
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate():
    """Test signup fails when student is already signed up"""
    # Arrange
    activity_name = "Programming Class"
    email = "emma@mergington.edu"  # Already in participants
    
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]


def test_signup_nonexistent_activity():
    """Test signup fails for non-existent activity"""
    # Arrange
    activity_name = "NonExistent Activity"
    email = "student@mergington.edu"
    
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_remove_participant_success():
    """Test successful removal of a participant"""
    # Arrange
    activity_name = "Gym Class"
    email = "john@mergington.edu"  # Already in participants
    
    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Removed {email} from {activity_name}" in data["message"]
    
    # Verify participant was removed
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email not in activities[activity_name]["participants"]


def test_remove_participant_nonexistent_activity():
    """Test removal fails for non-existent activity"""
    # Arrange
    activity_name = "NonExistent Activity"
    email = "student@mergington.edu"
    
    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_remove_participant_nonexistent_participant():
    """Test removal fails when participant is not in activity"""
    # Arrange
    activity_name = "Chess Club"
    email = "nonexistent@mergington.edu"
    
    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Participant not found" in data["detail"]