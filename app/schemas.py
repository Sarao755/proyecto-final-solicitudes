"""Esquemas de entrada (validación en el servidor con Pydantic)."""
import re
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from .config import CATEGORIAS, ESTADOS, PRIORIDADES

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class RegistroIn(BaseModel):
    nombre: str = Field(min_length=2, max_length=80)
    email: str = Field(max_length=120)
    password: str = Field(min_length=6, max_length=100)

    @field_validator("email")
    @classmethod
    def email_valido(cls, v):
        v = v.strip().lower()
        if not EMAIL_RE.match(v):
            raise ValueError("Correo electrónico no válido")
        return v


class LoginIn(BaseModel):
    email: str
    password: str


class SolicitudIn(BaseModel):
    titulo: str = Field(min_length=5, max_length=120)
    descripcion: str = Field(min_length=10, max_length=2000)
    categoria: str
    prioridad: str = "media"

    @field_validator("categoria")
    @classmethod
    def categoria_valida(cls, v):
        if v not in CATEGORIAS:
            raise ValueError(f"Categoría no válida. Opciones: {', '.join(CATEGORIAS)}")
        return v

    @field_validator("prioridad")
    @classmethod
    def prioridad_valida(cls, v):
        if v not in PRIORIDADES:
            raise ValueError(f"Prioridad no válida. Opciones: {', '.join(PRIORIDADES)}")
        return v


class AccionIn(BaseModel):
    comentario: str = Field(min_length=3, max_length=1000)
    estado_nuevo: Optional[str] = None  # si es None, se registra solo una nota de seguimiento
    respuesta: Optional[str] = Field(default=None, max_length=2000)

    @field_validator("estado_nuevo")
    @classmethod
    def estado_valido(cls, v):
        if v is not None and v not in ESTADOS:
            raise ValueError(f"Estado no válido. Opciones: {', '.join(ESTADOS)}")
        return v
