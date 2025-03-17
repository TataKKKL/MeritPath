from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt.exceptions import InvalidTokenError
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Supabase JWT secret
JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")
if not JWT_SECRET:
    raise ValueError("Missing SUPABASE_JWT_SECRET environment variable")

# Security scheme for Swagger UI
security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify the JWT token from Supabase
    """
    token = credentials.credentials
    try:
        # Decode and verify the token with options to handle Supabase's JWT format
        payload = jwt.decode(
            token, 
            JWT_SECRET, 
            algorithms=["HS256"],
            options={
                "verify_aud": False,  # Skip audience verification
                "verify_signature": True  # Still verify the signature
            }
        )
        return payload
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid authentication token: {str(e)}"
        )

async def get_current_user(payload=Depends(verify_token)):
    """
    Extract user information from the verified token
    """
    # The 'sub' claim contains the user ID in Supabase tokens
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid user information in token"
        )
    
    return {"id": user_id, "email": payload.get("email")} 