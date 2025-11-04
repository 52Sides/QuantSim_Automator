from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, constr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.database import get_db
from db.models.user_model import UserModel
from services.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


# ---------- Schemas ----------

class RegisterSchema(BaseModel):
    email: EmailStr
    password: constr(min_length=6)


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# ---------- Register ----------

@router.post("/register", status_code=201)
async def register_user(data: RegisterSchema, db: AsyncSession = Depends(get_db)):
    """Регистрирует нового пользователя"""
    q = await db.execute(select(UserModel).where(UserModel.email == data.email))
    if q.scalar():
        raise HTTPException(status_code=400, detail="User already exists")

    user = UserModel(email=data.email, hashed_password=hash_password(data.password))
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return {"id": user.id, "email": user.email}


# ---------- Login ----------

@router.post("/login", response_model=TokenResponse)
async def login_user(data: LoginSchema, db: AsyncSession = Depends(get_db)):
    """Аутентификация: возвращает access + refresh токены"""
    q = await db.execute(select(UserModel).where(UserModel.email == data.email))
    user = q.scalar_one_or_none()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # создаём токены
    access_token = create_access_token(str(user.id))
    refresh_token = await create_refresh_token(user.id, db)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
