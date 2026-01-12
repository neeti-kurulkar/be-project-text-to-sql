from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
from app.utils.jwt_utils import verify_token
from app.services.auth_service import AuthService


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Dependency to get the current authenticated user from JWT token

    Args:
        credentials: HTTP Bearer token from request header

    Returns:
        Dictionary containing user data

    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials

    # Verify and decode token
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user info from token
    user_id = payload.get("sub")
    organization_id = payload.get("organization_id")
    email = payload.get("email")
    role = payload.get("role")

    if not user_id or not organization_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Return user context
    return {
        "user_id": int(user_id),
        "organization_id": organization_id,
        "email": email,
        "role": role
    }


async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Dependency to get current active user (with database verification)

    Args:
        current_user: User context from JWT token

    Returns:
        Dictionary containing full user data from database

    Raises:
        HTTPException: If user is not found or inactive
    """
    user_id = current_user["user_id"]

    # Fetch fresh user data from database
    user = AuthService.get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    if not user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )

    return user


async def require_role(required_role: str):
    """
    Dependency factory to require specific role

    Args:
        required_role: Required role (admin, analyst, viewer)

    Returns:
        Dependency function that checks user role
    """
    async def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        user_role = current_user.get("role")

        # Admin has access to everything
        if user_role == "admin":
            return current_user

        # Check specific role
        if user_role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires '{required_role}' role"
            )

        return current_user

    return role_checker


async def require_admin(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Dependency to require admin role

    Args:
        current_user: User context from JWT token

    Returns:
        User context if user is admin

    Raises:
        HTTPException: If user is not admin
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires admin privileges"
        )

    return current_user


class OrganizationContext:
    """
    Context manager to inject organization_id into request state
    """
    def __init__(self, request: Request, current_user: Dict[str, Any]):
        self.request = request
        self.current_user = current_user

    def __enter__(self):
        # Inject organization_id into request state
        self.request.state.organization_id = self.current_user["organization_id"]
        self.request.state.user_id = self.current_user["user_id"]
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


def get_organization_id(current_user: Dict[str, Any] = Depends(get_current_user)) -> int:
    """
    Dependency to extract organization_id from current user

    Args:
        current_user: User context from JWT token

    Returns:
        Organization ID
    """
    return current_user["organization_id"]
