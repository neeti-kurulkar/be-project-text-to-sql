import bcrypt
from typing import Optional, Dict, Any
from datetime import datetime
from app.database import get_db_connection
from app.utils.jwt_utils import create_user_token


class AuthService:

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt

        Args:
            password: Plain text password

        Returns:
            Hashed password string
        """
        # Generate salt and hash password
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash

        Args:
            plain_password: Plain text password to check
            hashed_password: Hashed password to compare against

        Returns:
            True if password matches, False otherwise
        """
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )

    @staticmethod
    def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user with email and password

        Args:
            email: User's email address
            password: User's password

        Returns:
            Dictionary containing user data and token if authenticated, None otherwise
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()

            try:
                # Fetch user with organization info
                cursor.execute("""
                    SELECT
                        u.user_id,
                        u.email,
                        u.password_hash,
                        u.name,
                        u.role,
                        u.is_active,
                        u.email_verified,
                        u.organization_id,
                        o.name as organization_name,
                        o.slug as organization_slug,
                        o.is_active as org_is_active
                    FROM users u
                    JOIN organizations o ON u.organization_id = o.organization_id
                    WHERE u.email = %s
                """, (email,))

                user = cursor.fetchone()

                if not user:
                    # User not found
                    return None

                user_id, email, password_hash, name, role, is_active, email_verified, \
                    organization_id, org_name, org_slug, org_is_active = user

                # Check if user is active
                if not is_active:
                    raise ValueError("User account is deactivated")

                # Check if organization is active
                if not org_is_active:
                    raise ValueError("Organization is deactivated")

                # Verify password
                if not AuthService.verify_password(password, password_hash):
                    return None

                # Update last login
                cursor.execute("""
                    UPDATE users
                    SET last_login = CURRENT_TIMESTAMP
                    WHERE user_id = %s
                """, (user_id,))
                conn.commit()

                # Create JWT token
                token = create_user_token(
                    user_id=user_id,
                    organization_id=organization_id,
                    email=email,
                    role=role
                )

                # Return user data and token
                return {
                    "user": {
                        "id": str(user_id),
                        "email": email,
                        "name": name,
                        "role": role,
                        "company": org_name
                    },
                    "token": token
                }

            except Exception as e:
                cursor.close()
                raise e
            finally:
                cursor.close()

    @staticmethod
    def get_organization_by_email_domain(email: str) -> Optional[Dict[str, Any]]:
        """
        Get organization by extracting domain from email

        Args:
            email: User's email address

        Returns:
            Dictionary with organization info if found, None otherwise
        """
        # Extract domain from email
        domain = email.split('@')[1].lower()

        with get_db_connection() as conn:
            cursor = conn.cursor()

            try:
                cursor.execute("""
                    SELECT
                        o.organization_id,
                        o.name,
                        o.slug,
                        o.is_active
                    FROM organizations o
                    JOIN email_domains ed ON ed.organization_id = o.organization_id
                    WHERE LOWER(ed.domain) = %s
                    AND ed.is_verified = true
                    AND o.is_active = true
                    LIMIT 1
                """, (domain,))

                org = cursor.fetchone()
                cursor.close()

                if not org:
                    return None

                organization_id, name, slug, is_active = org

                return {
                    "organization_id": organization_id,
                    "name": name,
                    "slug": slug,
                    "is_active": is_active
                }

            except Exception as e:
                cursor.close()
                raise e

    @staticmethod
    def register_user(email: str, password: str, name: str, role: str = 'analyst') -> Dict[str, Any]:
        """
        Register a new user

        Args:
            email: User's email address
            password: User's password
            name: User's full name
            role: User's role (default: analyst)

        Returns:
            Dictionary containing user data and token

        Raises:
            ValueError: If email domain is not allowed or user already exists
        """
        # Check if email domain is allowed
        org = AuthService.get_organization_by_email_domain(email)
        if not org:
            raise ValueError("Email domain is not registered. Please contact your administrator.")

        organization_id = org['organization_id']

        with get_db_connection() as conn:
            cursor = conn.cursor()

            try:
                # Check if user already exists
                cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
                if cursor.fetchone():
                    raise ValueError("User with this email already exists")

                # Hash password
                password_hash = AuthService.hash_password(password)

                # Create user
                cursor.execute("""
                    INSERT INTO users (organization_id, email, password_hash, name, role, email_verified)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING user_id
                """, (organization_id, email, password_hash, name, role, False))

                user_id = cursor.fetchone()[0]
                conn.commit()

                # Create JWT token
                token = create_user_token(
                    user_id=user_id,
                    organization_id=organization_id,
                    email=email,
                    role=role
                )

                cursor.close()

                # Return user data and token
                return {
                    "user": {
                        "id": str(user_id),
                        "email": email,
                        "name": name,
                        "role": role,
                        "company": org['name']
                    },
                    "token": token
                }

            except Exception as e:
                conn.rollback()
                cursor.close()
                raise e

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user by ID

        Args:
            user_id: User's database ID

        Returns:
            Dictionary with user data if found, None otherwise
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()

            try:
                cursor.execute("""
                    SELECT
                        u.user_id,
                        u.email,
                        u.name,
                        u.role,
                        u.is_active,
                        u.organization_id,
                        o.name as organization_name
                    FROM users u
                    JOIN organizations o ON u.organization_id = o.organization_id
                    WHERE u.user_id = %s
                """, (user_id,))

                user = cursor.fetchone()
                cursor.close()

                if not user:
                    return None

                user_id, email, name, role, is_active, organization_id, org_name = user

                return {
                    "id": str(user_id),
                    "email": email,
                    "name": name,
                    "role": role,
                    "is_active": is_active,
                    "organization_id": organization_id,
                    "company": org_name
                }

            except Exception as e:
                cursor.close()
                raise e
