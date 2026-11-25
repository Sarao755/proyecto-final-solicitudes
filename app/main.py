"""Punto de entrada: crea la app, las tablas y sirve la interfaz web."""
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import CATEGORIAS, ESTADOS, PRIORIDADES, TRANSICIONES
from .database import Base, engine
from .routers import auth, resumen, solicitudes

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Gestión de solicitudes de servicio",
              description="API REST del Proyecto Final PF-01 (Aplicaciones y Servicios Web)",
              version="1.0.0")

app.include_router(auth.router)
app.include_router(solicitudes.router)
app.include_router(resumen.router)

ESTATICOS = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=ESTATICOS), name="static")


@app.get("/meta", tags=["Sistema"])
def meta():
    """Catálogos que usa la interfaz (estados, transiciones, categorías, prioridades)."""
    return {"estados": ESTADOS, "transiciones": TRANSICIONES,
            "categorias": CATEGORIAS, "prioridades": PRIORIDADES}


@app.get("/", include_in_schema=False)
def inicio():
    return FileResponse(ESTATICOS / "index.html")
