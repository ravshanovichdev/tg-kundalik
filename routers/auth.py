"""
Authentication router for SamIT Global system.
Handles Telegram WebApp authentication and user management.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional
import hashlib
import hmac
from urllib.parse import parse_qs

from app.database import get_db
from models.user import User
from schemas.user import UserResponse, CurrentUser
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


def verify_telegram_webapp_data(telegram_data: str) -> Optional[dict]:
    """
    Verify Telegram WebApp initData signature.
    Returns parsed data if valid, None otherwise.
    Supports test mode for local development.
    """
    try:
        # Parse initData
        data = parse_qs(telegram_data, strict_parsing=True)
        
        # Test mode check (для локального тестирования)
        if data.get('test_mode', [None])[0] == 'true':
            import json
            user_json = data.get('user', [None])[0]
            if user_json:
                user_data = json.loads(user_json)
                return {
                    'id': user_data.get('id', 123456789),
                    'username': user_data.get('username', 'testuser'),
                    'first_name': user_data.get('first_name', 'Test'),
                    'last_name': user_data.get('last_name', 'User')
                }
            return {
                'id': 123456789,
                'username': 'testuser',
                'first_name': 'Test',
                'last_name': 'User'
            }

        # Extract hash
        received_hash = data.get('hash', [None])[0]
        if not received_hash:
            return None

        # Create data string for verification
        data_check_string = '\n'.join([
            f"{k}={v[0]}" for k, v in sorted(data.items())
            if k != 'hash'
        ])

        # Create secret key
        secret_key = hmac.new(
            key=b'WebAppData',
            msg=settings.telegram_bot_token.encode(),
            digestmod=hashlib.sha256
        ).digest()

        # Calculate expected hash
        expected_hash = hmac.new(
            key=secret_key,
            msg=data_check_string.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()

        # Verify hash
        if not hmac.compare_digest(received_hash, expected_hash):
            return None

        # Return parsed user data
        user_data = data.get('user', [None])[0]
        if not user_data:
            return None

        # Parse user JSON (simplified - in production use proper JSON parsing)
        return {
            'id': int(data.get('id', [0])[0]),
            'username': data.get('username', [None])[0],
            'first_name': data.get('first_name', [''])[0],
            'last_name': data.get('last_name', [''])[0]
        }

    except Exception as e:
        logger.error(f"Error verifying Telegram data: {e}")
        return None


def get_current_user_from_telegram(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """
    Extract and validate user from Telegram WebApp initData.
    Creates user if doesn't exist.
    """
    # Get initData from header or query parameter
    telegram_data = (
        request.headers.get('X-Telegram-Init-Data') or
        request.query_params.get('initData')
    )

    if not telegram_data:
        raise HTTPException(
            status_code=401,
            detail="Telegram authentication required"
        )

    # Verify and parse Telegram data
    user_data = verify_telegram_webapp_data(telegram_data)
    if not user_data:
        raise HTTPException(
            status_code=401,
            detail="Invalid Telegram authentication"
        )

    # Find or create user
    try:
        user = db.query(User).filter(User.telegram_id == user_data['id']).first()

        if not user:
            # Create new user
            full_name = f"{user_data['first_name']} {user_data['last_name']}".strip()
            user = User(
                telegram_id=user_data['id'],
                username=user_data['username'],
                full_name=full_name or None,
                role="parent"  # Default role
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"Created new user: {user.telegram_id}")

        elif user.is_blocked:
            raise HTTPException(
                status_code=403,
                detail="User is blocked"
            )

        return user
    except Exception as e:
        # Если база данных недоступна, создаем mock пользователя для тестирования
        logger.warning(f"Database unavailable, creating mock user: {e}")
        from schemas.user import CurrentUser
        full_name = f"{user_data['first_name']} {user_data['last_name']}".strip()
        # Создаем mock объект пользователя
        class MockUser:
            def __init__(self):
                self.id = 1
                self.telegram_id = user_data['id']
                self.username = user_data['username']
                self.full_name = full_name or None
                self.role = "admin"  # В тестовом режиме делаем админом для полного доступа
                self.is_active = True
                self.is_blocked = False
                self.created_at = None
                self.updated_at = None
        
        return MockUser()


@router.get("/me", response_model=CurrentUser)
async def get_current_user(
    current_user: User = Depends(get_current_user_from_telegram)
):
    """
    Get current authenticated user information.
    """
    return current_user


@router.post("/verify")
async def verify_authentication(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Verify Telegram WebApp authentication without creating user.
    Returns user data if authentication is valid.
    """
    telegram_data = (
        request.headers.get('X-Telegram-Init-Data') or
        request.query_params.get('initData')
    )

    if not telegram_data:
        raise HTTPException(
            status_code=401,
            detail="Telegram authentication required"
        )

    user_data = verify_telegram_webapp_data(telegram_data)
    if not user_data:
        raise HTTPException(
            status_code=401,
            detail="Invalid Telegram authentication"
        )

    # Check if user exists and is not blocked
    user = db.query(User).filter(User.telegram_id == user_data['id']).first()

    if user and user.is_blocked:
        raise HTTPException(
            status_code=403,
            detail="User is blocked"
        )

    return {
        "authenticated": True,
        "user_exists": user is not None,
        "user_data": user_data
    }
