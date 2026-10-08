from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import models
import schemas
from database import get_db
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "clave_por_defecto_para_desarrollo")

# Configuración del JWT
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # El token dura 24 horas

# Configuración para encriptar contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Define de dónde se obtiene el token (por defecto, del header Authorization)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Busca la cuenta por nombre de usuario
def get_cuenta_by_usuario(db: Session, usuario: str):
    return db.query(models.Cuenta).filter(models.Cuenta.usuario == usuario).first()

def authenticate_user(db: Session, usuario: str, password: str):
    cuenta = get_cuenta_by_usuario(db, usuario)
    if not cuenta or not verify_password(password, cuenta.hashed_password):
        return False
    return cuenta

# Dependencia para obtener el usuario actual desde el token
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        usuario: str = payload.get("sub")
        if usuario is None:
            raise credentials_exception
        token_data = schemas.TokenData(usuario=usuario)
    except JWTError:
        raise credentials_exception
    
    cuenta = get_cuenta_by_usuario(db, usuario=token_data.usuario)
    if cuenta is None:
        raise credentials_exception
    return cuenta

    # ==========================================
# DEPENDENCIA PARA VERIFICAR ROL ADMIN
# ==========================================
def require_admin(current_user: models.Cuenta = Depends(get_current_user)):
    """
    Dependencia que verifica que el usuario actual tenga rol 'admin'.
    Si no es admin, retorna error 403 Forbidden.
    """
    if current_user.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos de administrador para realizar esta acción"
        )
    return current_user