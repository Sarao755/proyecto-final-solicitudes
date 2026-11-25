"""Ciclo de vida de una solicitud: registro, consulta, gestión, historial y cierre."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import ESTADOS, ESTADOS_FINALES, TRANSICIONES
from ..database import get_db
from ..models import Accion, Solicitud, Usuario
from ..schemas import AccionIn, SolicitudIn
from ..security import requiere_roles, usuario_actual

router = APIRouter(prefix="/solicitudes", tags=["Solicitudes"])

PERSONAL = ("personal", "coordinacion")


def solicitud_dict(s: Solicitud) -> dict:
    return {
        "id": s.id, "titulo": s.titulo, "descripcion": s.descripcion,
        "categoria": s.categoria, "prioridad": s.prioridad, "estado": s.estado,
        "respuesta": s.respuesta,
        "solicitante": s.solicitante.nombre,
        "responsable": s.responsable.nombre if s.responsable else None,
        "creada": s.creada.isoformat(), "actualizada": s.actualizada.isoformat(),
        "transiciones_posibles": TRANSICIONES[s.estado],
    }


def accion_dict(a: Accion) -> dict:
    return {"id": a.id, "tipo": a.tipo, "estado_resultante": a.estado_resultante,
            "comentario": a.comentario, "usuario": a.usuario.nombre,
            "rol": a.usuario.rol, "fecha": a.fecha.isoformat()}


def obtener_visible(db: Session, solicitud_id: int, usuario: Usuario) -> Solicitud:
    """404 si no existe; 403 si es un solicitante pidiendo la solicitud de otra persona."""
    s = db.get(Solicitud, solicitud_id)
    if s is None:
        raise HTTPException(404, "La solicitud no existe")
    if usuario.rol == "solicitante" and s.solicitante_id != usuario.id:
        raise HTTPException(403, "No puedes ver solicitudes de otras personas")
    return s


# CA-01 ─ presentar una solicitud
@router.post("", status_code=201)
def crear(datos: SolicitudIn, db: Session = Depends(get_db),
          u: Usuario = Depends(requiere_roles("solicitante"))):
    s = Solicitud(titulo=datos.titulo.strip(), descripcion=datos.descripcion.strip(),
                  categoria=datos.categoria, prioridad=datos.prioridad,
                  estado="RECIBIDA", solicitante_id=u.id)
    s.acciones.append(Accion(usuario_id=u.id, tipo="REGISTRO", estado_resultante="RECIBIDA",
                             comentario="Solicitud registrada por el solicitante"))
    db.add(s)
    db.commit()
    return solicitud_dict(s)


# CA-03 ─ consultar estado (solicitante ve las suyas; personal y coordinación ven todas)
@router.get("")
def listar(estado: Optional[str] = None, db: Session = Depends(get_db),
           u: Usuario = Depends(usuario_actual)):
    if estado is not None and estado not in ESTADOS:
        raise HTTPException(422, f"Estado no válido. Opciones: {', '.join(ESTADOS)}")
    consulta = select(Solicitud).order_by(Solicitud.id.desc())
    if u.rol == "solicitante":
        consulta = consulta.where(Solicitud.solicitante_id == u.id)
    if estado:
        consulta = consulta.where(Solicitud.estado == estado)
    return [solicitud_dict(s) for s in db.scalars(consulta)]


@router.get("/{solicitud_id}")
def detalle(solicitud_id: int, db: Session = Depends(get_db), u: Usuario = Depends(usuario_actual)):
    return solicitud_dict(obtener_visible(db, solicitud_id, u))


# CA-04 ─ trazabilidad de las acciones
@router.get("/{solicitud_id}/historial")
def historial(solicitud_id: int, db: Session = Depends(get_db), u: Usuario = Depends(usuario_actual)):
    s = obtener_visible(db, solicitud_id, u)
    return [accion_dict(a) for a in s.acciones]


# CA-02 ─ evaluar y gestionar (solo personal y coordinación)
@router.post("/{solicitud_id}/acciones", status_code=201)
def gestionar(solicitud_id: int, datos: AccionIn, db: Session = Depends(get_db),
              u: Usuario = Depends(requiere_roles(*PERSONAL))):
    s = db.get(Solicitud, solicitud_id)
    if s is None:
        raise HTTPException(404, "La solicitud no existe")

    # RN-05: una solicitud cerrada ya no se modifica
    if s.estado in ESTADOS_FINALES:
        raise HTTPException(409, f"La solicitud ya está {s.estado} y no admite más cambios")

    # RN-04: el personal solo gestiona las que no tienen responsable o son suyas; coordinación, todas
    if u.rol == "personal" and s.responsable_id not in (None, u.id):
        raise HTTPException(403, "Esta solicitud la atiende otra persona")

    if datos.estado_nuevo is None:
        accion = Accion(solicitud_id=s.id, usuario_id=u.id, tipo="NOTA",
                        estado_resultante=s.estado, comentario=datos.comentario.strip())
    else:
        # RN-02: solo transiciones permitidas
        if datos.estado_nuevo not in TRANSICIONES[s.estado]:
            permitidas = ", ".join(TRANSICIONES[s.estado]) or "ninguna"
            raise HTTPException(409, f"No se puede pasar de {s.estado} a {datos.estado_nuevo}. "
                                     f"Permitidas: {permitidas}")
        # RN-03: cerrar exige dejar una respuesta para el solicitante
        if datos.estado_nuevo in ESTADOS_FINALES:
            if not datos.respuesta or len(datos.respuesta.strip()) < 5:
                raise HTTPException(422, "Para finalizar o rechazar debes escribir la respuesta al solicitante")
            s.respuesta = datos.respuesta.strip()
        # RN-01: quien toma la solicitud en revisión queda como responsable
        if datos.estado_nuevo == "EN_REVISION":
            s.responsable_id = u.id
        s.estado = datos.estado_nuevo
        accion = Accion(solicitud_id=s.id, usuario_id=u.id, tipo="CAMBIO_ESTADO",
                        estado_resultante=s.estado, comentario=datos.comentario.strip())

    db.add(accion)
    db.commit()
    db.refresh(s)
    return solicitud_dict(s)
