"""Registro, inicio de sesión y datos del usuario actual."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Usuario
from ..schemas import LoginIn, RegistroIn
from ..security import crear_token, hash_password, usuario_actual, verificar_password

router = APIRouter(prefix="/auth", tags=["Autenticación"])


def usuario_dict(u: Usuario) -> dict:
    return {"id": u.id, "nombre": u.nombre, "email": u.email, "rol": u.rol}


@router.post("/registro", status_code=201)
def registro(datos: RegistroIn, db: Session = Depends(get_db)):
    """Cualquier persona se registra como solicitante. Personal y coordinación los crea el administrador."""
    if db.scalar(select(Usuario).where(Usuario.email == datos.email)):
        raise HTTPException(409, "Ya existe un usuario con ese correo")
    u = Usuario(nombre=datos.nombre.strip(), email=datos.email,
                password_hash=hash_password(datos.password), rol="solicitante")
    db.add(u)
    db.commit()
    return usuario_dict(u)


@router.post("/login")
def login(datos: LoginIn, db: Session = Depends(get_db)):
    u = db.scalar(select(Usuario).where(Usuario.email == datos.email.strip().lower()))
    # Mismo mensaje si falla el correo o la clave: no revela qué usuarios existen.
    if u is None or not verificar_password(datos.password, u.password_hash):
        raise HTTPException(401, "Correo o contraseña incorrectos")
    return {"access_token": crear_token(u), "token_type": "bearer", "usuario": usuario_dict(u)}


@router.get("/me")
def me(u: Usuario = Depends(usuario_actual)):
    return usuario_dict(u)
