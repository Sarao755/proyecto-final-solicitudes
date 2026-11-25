"""Contraseñas con hash PBKDF2, tokens JWT y control de acceso por rol."""
import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .config import SECRET_KEY, TOKEN_HORAS
from .database import get_db
from .models import Usuario

bearer = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    sal = os.urandom(16)
    h = hashlib.pbkdf2_hmac("sha256", password.encode(), sal, 100_000)
    return sal.hex() + "$" + h.hex()


def verificar_password(password: str, guardado: str) -> bool:
    sal_hex, h_hex = guardado.split("$")
    h = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(sal_hex), 100_000)
    return hmac.compare_digest(h.hex(), h_hex)


def crear_token(usuario: Usuario) -> str:
    payload = {
        "sub": str(usuario.id),
        "exp": datetime.now(timezone.utc) + timedelta(hours=TOKEN_HORAS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def usuario_actual(
    cred: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> Usuario:
    if cred is None:
        raise HTTPException(401, "Debes iniciar sesión")
    try:
        datos = jwt.decode(cred.credentials, SECRET_KEY, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(401, "Sesión no válida o vencida")
    usuario = db.get(Usuario, int(datos["sub"]))
    if usuario is None:
        raise HTTPException(401, "Usuario no encontrado")
    return usuario


def requiere_roles(*roles: str):
    """Dependencia: deja pasar solo a los roles indicados (403 en otro caso)."""
    def verificar(usuario: Usuario = Depends(usuario_actual)) -> Usuario:
        if usuario.rol not in roles:
            raise HTTPException(403, "No tienes permiso para esta operación")
        return usuario
    return verificar
