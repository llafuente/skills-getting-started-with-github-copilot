"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Provide a test client for the FastAPI app"""
    return TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_200(self, client):
        """Test that GET /activities returns 200 OK"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_expected_fields(self, client):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        assert len(activities) > 0, "Should have at least one activity"
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str)
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_has_chess_club(self, client):
        """Test that Chess Club activity exists"""
        response = client.get("/activities")
        activities = response.json()
        assert "Chess Club" in activities


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_returns_200(self, client):
        """Test successful signup returns 200"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@school.edu"
        )
        assert response.status_code == 200

    def test_signup_returns_success_message(self, client):
        """Test signup response contains success message"""
        response = client.post(
            "/activities/Programming%20Class/signup?email=test1@school.edu"
        )
        result = response.json()
        assert "message" in result
        assert "Signed up" in result["message"]

    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test signup for nonexistent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=test@school.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_duplicate_email_returns_400(self, client):
        """Test signing up same email twice returns 400"""
        email = "duplicate.test@school.edu"
        
        # First signup should succeed
        response1 = client.post(
            f"/activities/Art%20Club/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(
            f"/activities/Art%20Club/signup?email={email}"
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"].lower()

    def test_signup_multiple_activities_allowed(self, client):
        """Test that same email can sign up for different activities"""
        email = "multi.activity@school.edu"
        
        response1 = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response1.status_code == 200
        
        response2 = client.post(
            f"/activities/Drama%20Society/signup?email={email}"
        )
        assert response2.status_code == 200


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants endpoint"""

    def test_remove_participant_returns_200(self, client):
        """Test successful participant removal returns 200"""
        email = "remove.test@school.edu"
        
        # First signup
        client.post(f"/activities/Soccer%20Team/signup?email={email}")
        
        # Then remove
        response = client.delete(
            f"/activities/Soccer%20Team/participants?email={email}"
        )
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]

    def test_remove_nonexistent_activity_returns_404(self, client):
        """Test removing from nonexistent activity returns 404"""
        response = client.delete(
            "/activities/Fake%20Activity/participants?email=test@school.edu"
        )
        assert response.status_code == 404

    def test_remove_nonexistent_participant_returns_404(self, client):
        """Test removing non-existent participant returns 404"""
        response = client.delete(
            "/activities/Chess%20Club/participants?email=notareal@email.com"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_remove_participant_actually_removes(self, client):
        """Test that removing a participant actually removes them"""
        email = "verify.remove@school.edu"
        
        # Signup
        client.post(f"/activities/Basketball%20Club/signup?email={email}")
        
        # Verify they're signed up
        response1 = client.get("/activities")
        assert email in response1.json()["Basketball Club"]["participants"]
        
        # Remove
        client.delete(
            f"/activities/Basketball%20Club/participants?email={email}"
        )
        
        # Verify they're removed
        response2 = client.get("/activities")
        assert email not in response2.json()["Basketball Club"]["participants"]


class TestRoot:
    """Tests for GET / endpoint"""

    def test_root_redirects_to_static(self, client):
        """Test that root redirects to static HTML"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
