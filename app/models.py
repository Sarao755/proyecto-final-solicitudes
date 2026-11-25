"""Modelo de datos: Usuario 1—N Solicitud 1—N Accion."""
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def ahora():
    return datetime.now(timezone.utc)


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(80))
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    rol: Mapped[str] = mapped_column(String(20))  # solicitante | personal | coordinacion


class Solicitud(Base):
    __tablename__ = "solicitudes"

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(120))
    descripcion: Mapped[str] = mapped_column(Text)
    categoria: Mapped[str] = mapped_column(String(40))
    prioridad: Mapped[str] = mapped_column(String(10), default="media")
    estado: Mapped[str] = mapped_column(String(20), default="RECIBIDA", index=True)
    respuesta: Mapped[str | None] = mapped_column(Text, nullable=True)
    solicitante_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    responsable_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    creada: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=ahora)
    actualizada: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=ahora, onupdate=ahora)

    solicitante: Mapped[Usuario] = relationship(foreign_keys=[solicitante_id])
    responsable: Mapped[Usuario | None] = relationship(foreign_keys=[responsable_id])
    acciones: Mapped[list["Accion"]] = relationship(
        back_populates="solicitud", order_by="Accion.id", cascade="all, delete-orphan"
    )


class Accion(Base):
    """Cada intervención sobre una solicitud: da la trazabilidad (CA-04)."""
    __tablename__ = "acciones"

    id: Mapped[int] = mapped_column(primary_key=True)
    solicitud_id: Mapped[int] = mapped_column(ForeignKey("solicitudes.id"), index=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    tipo: Mapped[str] = mapped_column(String(20))  # REGISTRO | CAMBIO_ESTADO | NOTA
    estado_resultante: Mapped[str] = mapped_column(String(20))
    comentario: Mapped[str] = mapped_column(Text)
    fecha: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=ahora)

    solicitud: Mapped[Solicitud] = relationship(back_populates="acciones")
    usuario: Mapped[Usuario] = relationship()
