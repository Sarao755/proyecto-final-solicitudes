"""Carga datos ficticios de demostración. Uso: python seed.py"""
from sqlalchemy import select

from app.database import Base, SessionLocal, engine
from app.models import Accion, Solicitud, Usuario
from app.security import hash_password

USUARIOS = [
    ("Laura Gómez", "solicitante@demo.com", "demo123", "solicitante"),
    ("Camilo Rojas", "solicitante2@demo.com", "demo123", "solicitante"),
    ("Andrea Mejía", "personal@demo.com", "demo123", "personal"),
    ("Julián Pérez", "personal2@demo.com", "demo123", "personal"),
    ("Marcela Ruiz", "coordinacion@demo.com", "demo123", "coordinacion"),
]


def cargar():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if db.scalar(select(Usuario).limit(1)):
            print("La base ya tiene datos; no se cargó nada.")
            return
        mapa = {}
        for nombre, email, clave, rol in USUARIOS:
            u = Usuario(nombre=nombre, email=email, password_hash=hash_password(clave), rol=rol)
            db.add(u)
            mapa[email] = u
        db.flush()

        laura, camilo = mapa["solicitante@demo.com"], mapa["solicitante2@demo.com"]
        andrea, julian = mapa["personal@demo.com"], mapa["personal2@demo.com"]

        def nueva(titulo, desc, cat, prio, solicitante):
            s = Solicitud(titulo=titulo, descripcion=desc, categoria=cat, prioridad=prio,
                          solicitante_id=solicitante.id)
            s.acciones.append(Accion(usuario_id=solicitante.id, tipo="REGISTRO",
                                     estado_resultante="RECIBIDA",
                                     comentario="Solicitud registrada por el solicitante"))
            db.add(s)
            return s

        nueva("Certificado de estudios", "Necesito un certificado de estudios para una beca.", "Trámite", "alta", laura)
        s2 = nueva("Orientación sobre homologación", "Quiero saber cómo homologar materias.", "Orientación", "media", camilo)
        s2.estado, s2.responsable_id = "EN_REVISION", andrea.id
        s2.acciones.append(Accion(usuario_id=andrea.id, tipo="CAMBIO_ESTADO", estado_resultante="EN_REVISION",
                                  comentario="Tomo la solicitud para revisarla"))
        s3 = nueva("Cambio de horario", "Solicito cambiar mi horario por cruce de clases.", "Atención administrativa", "media", laura)
        s3.estado, s3.responsable_id, s3.respuesta = "FINALIZADA", julian.id, "Tu horario fue actualizado. Revisa el portal."
        for est, com in (("EN_REVISION", "Reviso el cruce de horarios"), ("EN_GESTION", "Gestiono el cambio con secretaría"),
                         ("FINALIZADA", "Cambio realizado")):
            s3.acciones.append(Accion(usuario_id=julian.id, tipo="CAMBIO_ESTADO", estado_resultante=est, comentario=com))
        db.commit()
        print("Datos de demostración cargados.")


if __name__ == "__main__":
    cargar()
