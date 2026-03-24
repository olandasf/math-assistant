"""
API Router - Autentifikacija ir admin valdymas.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.admin_user import AdminUser
from utils.auth_deps import create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Slaptažodžio hash'avimas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# === Request/Response Models ===


class LoginRequest(BaseModel):
    """Prisijungimo užklausa."""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Prisijungimo atsakymas."""
    access_token: str
    token_type: str = "bearer"
    username: str


class SetupRequest(BaseModel):
    """Pradinis admin kūrimo užklausa."""
    username: str = "admin"
    password: str


class AuthStatusResponse(BaseModel):
    """Autentifikacijos statuso atsakymas."""
    has_admin: bool
    message: str


class UserResponse(BaseModel):
    """Vartotojo informacija."""
    id: int
    username: str


# === Endpoints ===


@router.get("/status", response_model=AuthStatusResponse)
async def auth_status(db: AsyncSession = Depends(get_db)):
    """
    Tikrina ar sistema turi administratorių.
    Viešas endpoint (be autentifikacijos).
    """
    result = await db.execute(select(func.count(AdminUser.id)))
    count = result.scalar()

    if count and count > 0:
        return AuthStatusResponse(
            has_admin=True,
            message="Sistema paruošta. Prisijunkite.",
        )
    return AuthStatusResponse(
        has_admin=False,
        message="Sukurkite administratoriaus paskyrą.",
    )


@router.post("/setup", response_model=LoginResponse)
async def setup_admin(request: SetupRequest, db: AsyncSession = Depends(get_db)):
    """
    Pradinis admin kūrimas. Veikia TIK jei nėra jokio admin.
    """
    # Tikrinti ar jau yra admin
    result = await db.execute(select(func.count(AdminUser.id)))
    count = result.scalar()

    if count and count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Administratorius jau sukurtas. Naudokite /auth/login.",
        )

    # Validuoti slaptažodį
    if len(request.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slaptažodis turi būti bent 6 simbolių.",
        )

    # Sukurti admin
    hashed = pwd_context.hash(request.password)
    admin = AdminUser(
        username=request.username,
        hashed_password=hashed,
    )
    db.add(admin)
    await db.commit()
    await db.refresh(admin)

    logger.info(f"✅ Administratorius '{request.username}' sukurtas sėkmingai!")

    # Iškart grąžinti tokeną
    token = create_access_token(data={"sub": admin.username})
    return LoginResponse(
        access_token=token,
        username=admin.username,
    )


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Prisijungimas su vartotojo vardu ir slaptažodžiu.
    Grąžina JWT Bearer token.
    """
    # Rasti vartotoją
    result = await db.execute(
        select(AdminUser).where(AdminUser.username == request.username)
    )
    user = result.scalar_one_or_none()

    if not user or not pwd_context.verify(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Neteisingas vartotojo vardas arba slaptažodis",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Sukurti tokeną
    token = create_access_token(data={"sub": user.username})

    logger.info(f"✅ Vartotojas '{user.username}' prisijungė sėkmingai")

    return LoginResponse(
        access_token=token,
        username=user.username,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: AdminUser = Depends(get_current_user)):
    """
    Grąžina dabartinio prisijungusio vartotojo informaciją.
    Apsaugotas endpoint.
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
    )
