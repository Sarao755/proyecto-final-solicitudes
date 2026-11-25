"""Configuración leída de variables de entorno (.env). Nunca se suben secretos al repo."""
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
SECRET_KEY = os.getenv("SECRET_KEY", "clave-solo-para-desarrollo-local-0123456789")
TOKEN_HORAS = 8

ROLES = ("solicitante", "personal", "coordinacion")
CATEGORIAS = ("Trámite", "Orientación", "Atención administrativa", "Otro")
PRIORIDADES = ("baja", "media", "alta")

# Estados del proceso y transiciones permitidas (regla de negocio RN-02)
ESTADOS = ("RECIBIDA", "EN_REVISION", "EN_GESTION", "FINALIZADA", "RECHAZADA")
TRANSICIONES = {
    "RECIBIDA": ["EN_REVISION"],
    "EN_REVISION": ["EN_GESTION", "RECHAZADA"],
    "EN_GESTION": ["FINALIZADA"],
    "FINALIZADA": [],
    "RECHAZADA": [],
}
ESTADOS_FINALES = ("FINALIZADA", "RECHAZADA")
