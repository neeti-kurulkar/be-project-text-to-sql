from fastapi import APIRouter, HTTPException, status, Depends
from app.models.auth_models import LoginRequest, RegisterRequest, AuthResponse, UserResponse
from app.services.auth_service import AuthService
from app.middleware.auth_middleware import get_current_active_user
from typing import Dict, Any


router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=AuthResponse)
async def login(credentials: LoginRequest):
    """
    Authenticate user and return JWT token

    Args:
        credentials: Login credentials (email and password)

    Returns:
        AuthResponse with user data and JWT token

    Raises:
        HTTPException: If credentials are invalid
    """
    try:
        result = AuthService.authenticate_user(
            email=credentials.email,
            password=credentials.password
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )


@router.post("/register", response_model=AuthResponse)
async def register(user_data: RegisterRequest):
    """
    Register a new user

    Args:
        user_data: User registration data

    Returns:
        AuthResponse with user data and JWT token

    Raises:
        HTTPException: If registration fails
    """
    try:
        result = AuthService.register_user(
            email=user_data.email,
            password=user_data.password,
            name=user_data.name,
            role=user_data.role
        )

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """
    Get current authenticated user information

    Args:
        current_user: Current user from JWT token (injected by dependency)

    Returns:
        UserResponse with user data
    """
    return UserResponse(**current_user)


@router.post("/logout")
async def logout(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """
    Logout user (client should discard token)

    Args:
        current_user: Current user from JWT token (injected by dependency)

    Returns:
        Success message
    """
    # In a stateless JWT system, logout is handled on the client side
    # by removing the token. We could add token blacklisting here if needed.

    return {
        "message": "Successfully logged out",
        "user_id": current_user["id"]
    }
