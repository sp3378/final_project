from builtins import repr
from datetime import datetime, timezone
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user_model import User, UserRole
from sqlalchemy import event

@pytest.mark.asyncio
async def test_user_role(db_session: AsyncSession, user: User, admin_user: User, manager_user: User):
    """
    Tests that the default role is assigned correctly and can be updated.
    """
    assert user.role == UserRole.AUTHENTICATED, "Default role should be USER"
    assert admin_user.role == UserRole.ADMIN, "Admin role should be correctly assigned"
    assert manager_user.role == UserRole.MANAGER, "Pro role should be correctly assigned"

@pytest.mark.asyncio
async def test_has_role(user: User, admin_user: User, manager_user: User):
    """
    Tests the has_role method to ensure it accurately checks the user's role.
    """
    assert user.has_role(UserRole.AUTHENTICATED), "User should have USER role"
    assert not user.has_role(UserRole.ADMIN), "User should not have ADMIN role"
    assert admin_user.has_role(UserRole.ADMIN), "Admin user should have ADMIN role"
    assert manager_user.has_role(UserRole.MANAGER), "Pro user should have PRO role"

@pytest.mark.asyncio
async def test_user_repr(user: User):
    """
    Tests the __repr__ method for accurate representation of the User object.
    """
    assert repr(user) == f"<User {user.nickname}, Role: {user.role.name}>", "__repr__ should include nickname and role"

@pytest.mark.asyncio
async def test_failed_login_attempts_increment(db_session: AsyncSession, user: User):
    """
    Tests that failed login attempts can be incremented and persisted correctly.
    """
    initial_attempts = user.failed_login_attempts
    user.failed_login_attempts += 1
    await db_session.commit()
    await db_session.refresh(user)
    assert user.failed_login_attempts == initial_attempts + 1, "Failed login attempts should increment"

@pytest.mark.asyncio
async def test_last_login_update(db_session: AsyncSession, user: User):
    """
    Tests updating the last login timestamp.
    """
    new_last_login = datetime.now(timezone.utc)
    user.last_login_at = new_last_login
    await db_session.commit()
    await db_session.refresh(user)
    assert user.last_login_at == new_last_login, "Last login timestamp should update correctly"

@pytest.mark.asyncio
async def test_account_lock_and_unlock(db_session: AsyncSession, user: User):
    """
    Tests locking and unlocking the user account.
    """
    # Initially, the account should not be locked.
    assert not user.is_locked, "Account should initially be unlocked"

    # Lock the account and verify.
    user.lock_account()
    await db_session.commit()
    await db_session.refresh(user)
    assert user.is_locked, "Account should be locked after calling lock_account()"

    # Unlock the account and verify.
    user.unlock_account()
    await db_session.commit()
    await db_session.refresh(user)
    assert not user.is_locked, "Account should be unlocked after calling unlock_account()"

@pytest.mark.asyncio
async def test_email_verification(db_session: AsyncSession, user: User):
    """
    Tests the email verification functionality.
    """
    # Initially, the email should not be verified.
    assert not user.email_verified, "Email should initially be unverified"

    # Verify the email and check.
    user.verify_email()
    await db_session.commit()
    await db_session.refresh(user)
    assert user.email_verified, "Email should be verified after calling verify_email()"

@pytest.mark.asyncio
async def test_user_profile_pic_url_update(db_session: AsyncSession, user: User):
    """
    Tests the profile pic update functionality.
    """
    # Initially, the profile pic should be updated.

    # Verify the email and check.
    profile_pic_url = "http://myprofile/picture.png"
    user.profile_picture_url = profile_pic_url
    await db_session.commit()
    await db_session.refresh(user)
    assert user.profile_picture_url == profile_pic_url, "The profile pic did not update"

@pytest.mark.asyncio
async def test_user_linkedin_url_update(db_session: AsyncSession, user: User):
    """
    Tests the profile pic update functionality.
    """
    # Initially, the linkedin should  be updated.

    # Verify the linkedin profile url.
    profile_linkedin_url = "http://www.linkedin.com/profile"
    user.linkedin_profile_url = profile_linkedin_url
    await db_session.commit()
    await db_session.refresh(user)
    assert user.linkedin_profile_url == profile_linkedin_url, "The profile pic did not update"


@pytest.mark.asyncio
async def test_user_github_url_update(db_session: AsyncSession, user: User):
    """
    Tests the profile pic update functionality.
    """
    # Initially, the linkedin should  be updated.

    # Verify the linkedin profile url.
    profile_github_url = "http://www.github.com/profile"
    user.github_profile_url = profile_github_url
    await db_session.commit()
    await db_session.refresh(user)
    assert user.github_profile_url == profile_github_url, "The github did not update"


@pytest.mark.asyncio
async def test_update_user_role(db_session: AsyncSession, user: User):
    """
    Tests updating the user's role and ensuring it persists correctly.
    """
    user.role = UserRole.ADMIN
    await db_session.commit()
    await db_session.refresh(user)
    assert user.role == UserRole.ADMIN, "Role update should persist correctly in the database"

@pytest.mark.asyncio
async def test_user_nickname_uniqueness(db_session):
    """Test that users cannot have duplicate nicknames"""
    nickname = "unique_nickname"
    
    # Create first user
    user1 = User(
        nickname=nickname,
        email="user1@example.com",
        hashed_password="password",
        role=UserRole.AUTHENTICATED
    )
    db_session.add(user1)
    await db_session.commit()
    
    # Try to create second user with same nickname
    user2 = User(
        nickname=nickname,
        email="user2@example.com",
        hashed_password="password",
        role=UserRole.AUTHENTICATED
    )
    db_session.add(user2)
    with pytest.raises(Exception):  # Should raise an integrity error
        await db_session.commit()

@pytest.mark.asyncio
async def test_user_role_transition(db_session, user):
    """Test transitioning user through different roles"""
    # Start as ANONYMOUS
    user.role = UserRole.ANONYMOUS
    await db_session.commit()
    assert user.role == UserRole.ANONYMOUS
    
    # Upgrade to AUTHENTICATED
    user.role = UserRole.AUTHENTICATED
    await db_session.commit()
    assert user.role == UserRole.AUTHENTICATED
    
    # Upgrade to MANAGER
    user.role = UserRole.MANAGER
    await db_session.commit()
    assert user.role == UserRole.MANAGER

@pytest.mark.asyncio
async def test_professional_status_timestamp(db_session, user):
    """Test that professional status updates timestamp"""
    # Update the professional status using the update method
    user.update_professional_status(True)
    await db_session.commit()
    
    # Refresh the user to get the updated timestamp
    await db_session.refresh(user)
    
    # Assert that the timestamp exists and is recent
    assert user.professional_status_updated_at is not None
    assert user.is_professional is True

@pytest.mark.asyncio
async def test_user_model_defaults(db_session):
    """Test default values when creating a new user"""
    user = User(
        nickname="test_defaults",
        email="defaults@example.com",
        hashed_password="password",
        role=UserRole.AUTHENTICATED
    )
    db_session.add(user)
    await db_session.commit()
    
    assert user.failed_login_attempts == 0
    assert user.is_locked is False
    assert user.is_professional is False
    assert user.email_verified is False
    assert user.created_at is not None
    assert user.updated_at is not None
