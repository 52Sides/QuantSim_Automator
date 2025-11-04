from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from db.database import get_db
from db.models.refresh_token_model import RefreshTokenModel
from services.auth import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/refresh")
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    """Обновить access-токен по refresh-токену."""
    stmt = select(RefreshTokenModel).where(RefreshTokenModel.token == refresh_token)
    res = await db.execute(stmt)
    token_obj = res.scalar_one_or_none()

    if not token_obj or token_obj.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    new_access = create_access_token({"sub": str(token_obj.user_id)})
    return {"access_token": new_access, "token_type": "bearer"}


@router.post("/logout")
async def logout(refresh_token: str, db: AsyncSession = Depends(get_db)):
    """Удаляет refresh-токен (logout)."""
    q = await db.execute(
        RefreshTokenModel.__table__.delete().where(RefreshTokenModel.token == refresh_token)
    )
    await db.commit()
    return {"detail": "Logged out"}
