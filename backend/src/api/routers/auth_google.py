from fastapi import APIRouter, Depends, Request, HTTPException
from authlib.integrations.starlette_client import OAuth
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.database import get_db
from db.models.user_model import UserModel
from services.auth import create_access_token, create_refresh_token
from core.config import settings

router = APIRouter(prefix="/auth", tags=["OAuth2"])

oauth = OAuth()

# Google
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


@router.get("/google/login")
async def google_login(request: Request):
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(request: Request, db: AsyncSession = Depends(get_db)):
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")
    if not user_info:
        raise HTTPException(status_code=400, detail="Google OAuth failed")

    email = user_info["email"]
    q = await db.execute(select(UserModel).where(UserModel.email == email))
    user = q.scalar_one_or_none()
    if not user:
        user = UserModel(email=email, hashed_password=None)
        db.add(user)
        await db.commit()
        await db.refresh(user)

    access_token = create_access_token(str(user.id))
    refresh_token = await create_refresh_token(user.id, db)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
