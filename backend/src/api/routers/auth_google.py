from fastapi import APIRouter, Request, Depends, HTTPException
from authlib.integrations.starlette_client import OAuth
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.database import get_db
from db.models.user_model import UserModel
from services.auth import create_access_token, create_refresh_token
from starlette.responses import RedirectResponse
import os

router = APIRouter(prefix="/auth/google", tags=["Auth - Google"])

# --- OAuth Client ---
oauth = OAuth()
oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


@router.get("/login")
async def google_login(request: Request):
    """Отправляет пользователя на Google OAuth2-страницу."""
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/callback")
async def google_callback(request: Request, db: AsyncSession = Depends(get_db)):
    """Получает access_token от Google, создаёт/находит пользователя, редиректит с токенами."""
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")
    if not user_info:
        raise HTTPException(status_code=400, detail="OAuth userinfo missing")

    email = user_info["email"]
    q = await db.execute(select(UserModel).where(UserModel.email == email))
    user = q.scalar_one_or_none()
    if not user:
        user = UserModel(email=email, hashed_password="oauth")
        db.add(user)
        await db.commit()
        await db.refresh(user)

    access_token = create_access_token(str(user.id))
    refresh_token = await create_refresh_token(user.id, db)

    # Редиректим на фронт с токенами в URL
    redirect = f"{FRONTEND_URL}/oauth/callback?access_token={access_token}&refresh_token={refresh_token}"
    return RedirectResponse(url=redirect)
