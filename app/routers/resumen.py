"""CA-06: información consolidada para la coordinación."""
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..config import ESTADOS, ESTADOS_FINALES
from ..database import get_db
from ..models import Solicitud, Usuario
from ..security import requiere_roles

router = APIRouter(prefix="/resumen", tags=["Coordinación"])


@router.get("")
def resumen(db: Session = Depends(get_db), _: Usuario = Depends(requiere_roles("coordinacion"))):
    por_estado = {e: 0 for e in ESTADOS}
    for estado, total in db.execute(select(Solicitud.estado, func.count()).group_by(Solicitud.estado)):
        por_estado[estado] = total

    por_responsable = []
    filas = db.execute(
        select(Usuario.nombre, Solicitud.estado, func.count())
        .join(Solicitud, Solicitud.responsable_id == Usuario.id)
        .group_by(Usuario.nombre, Solicitud.estado)
    )
    acumulado: dict[str, dict] = {}
    for nombre, estado, total in filas:
        r = acumulado.setdefault(nombre, {"responsable": nombre, "total": 0, "abiertas": 0})
        r["total"] += total
        if estado not in ESTADOS_FINALES:
            r["abiertas"] += total
    por_responsable = sorted(acumulado.values(), key=lambda r: -r["total"])

    return {
        "total": sum(por_estado.values()),
        "por_estado": por_estado,
        "sin_responsable": db.scalar(
            select(func.count()).select_from(Solicitud).where(Solicitud.responsable_id.is_(None))
        ),
        "por_responsable": por_responsable,
    }
