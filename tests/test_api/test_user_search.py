import pytest
from datetime import datetime, timedelta
from app.models.user_model import UserRole

@pytest.mark.asyncio
async def test_search_users_by_term(async_client, admin_token):
    """Test searching users by search term"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.get(
        "/users/search/?search_term=admin",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) > 0
    assert "admin" in data["items"][0]["email"].lower()

@pytest.mark.asyncio
async def test_search_users_by_role(async_client, admin_token):
    """Test filtering users by role"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.get(
        "/users/search/?role=MANAGER",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    for user in data["items"]:
        assert user["role"] == "MANAGER"

@pytest.mark.asyncio
async def test_search_users_by_status(async_client, admin_token):
    """Test filtering users by account status"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.get(
        "/users/search/?is_locked=true",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    for user in data["items"]:
        assert user["is_locked"] is True

@pytest.mark.asyncio
async def test_search_users_by_date_range(async_client, admin_token):
    """Test filtering users by registration date range"""
    start_date = datetime.utcnow() - timedelta(days=7)
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.get(
        f"/users/search/?registration_start={start_date.isoformat()}",
        headers=headers
    )
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_search_users_combined_filters(async_client, admin_token):
    """Test searching users with multiple filters"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.get(
        "/users/search/?search_term=test&role=AUTHENTICATED&is_verified=true",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    for user in data["items"]:
        assert user["role"] == "AUTHENTICATED"
        assert user["email_verified"] is True 