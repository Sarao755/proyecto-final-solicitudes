"""Pruebas funcionales de la Actividad 6 (12 pruebas mínimas).
Usa una base de datos temporal, no toca app.db.   Uso:  python pruebas/ejecutar_pruebas.py
Genera evidencias/resultados_pruebas.md con el resultado de cada prueba."""
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
BD = RAIZ / "pruebas" / "bd_pruebas.db"
BD.unlink(missing_ok=True)
os.environ["DATABASE_URL"] = f"sqlite:///{BD}"          # antes de importar la app

import warnings
warnings.filterwarnings("ignore")
from fastapi.testclient import TestClient               # noqa: E402
from sqlalchemy import text                              # noqa: E402

import seed                                              # noqa: E402
from app.database import SessionLocal                    # noqa: E402
from app.main import app                                 # noqa: E402

seed.cargar()
c = TestClient(app)
resultados = []


def entrar(email, clave="demo123"):
    r = c.post("/auth/login", json={"email": email, "password": clave})
    return {"Authorization": "Bearer " + r.json()["access_token"]}


def registrar(num, req, nombre, peticion, esperado, obtenido, codigo, ok):
    resultados.append((num, req, nombre, peticion, esperado, obtenido, codigo, "Aprobada" if ok else "FALLIDA"))


SOL = entrar("solicitante@demo.com")
SOL2 = entrar("solicitante2@demo.com")
PER = entrar("personal@demo.com")
PER2 = entrar("personal2@demo.com")
COO = entrar("coordinacion@demo.com")

# 1 ─ registro válido
datos = {"titulo": "Paz y salvo académico", "descripcion": "Necesito el paz y salvo para mi grado.",
         "categoria": "Trámite", "prioridad": "alta"}
r = c.post("/solicitudes", json=datos, headers=SOL)
nueva = r.json()
g = c.get(f"/solicitudes/{nueva.get('id')}", headers=SOL)
registrar(1, "CA-01 / RF-02", "Registro válido de solicitud", "POST /solicitudes",
          "201 y solicitud recuperable con estado RECIBIDA",
          f"id={nueva.get('id')}, estado={nueva.get('estado')}, GET posterior={g.status_code}", r.status_code,
          r.status_code == 201 and g.status_code == 200 and g.json()["estado"] == "RECIBIDA")
ID = nueva["id"]

# 2 ─ datos inválidos
antes = len(c.get("/solicitudes", headers=SOL).json())
r = c.post("/solicitudes", json={"titulo": "ab", "descripcion": "corta", "categoria": "Inventada"}, headers=SOL)
despues = len(c.get("/solicitudes", headers=SOL).json())
registrar(2, "CA-01 / RNF-01", "Registro con datos inválidos", "POST /solicitudes (título corto, categoría falsa)",
          "422 y no se guarda nada", f"cantidad antes={antes}, después={despues}", r.status_code,
          r.status_code == 422 and antes == despues)

# 3 ─ consulta existente
r = c.get(f"/solicitudes/{ID}", headers=SOL)
registrar(3, "CA-03 / RF-04", "Consulta de solicitud existente", f"GET /solicitudes/{ID}",
          "200 con los datos del caso", f"titulo='{r.json().get('titulo')}'", r.status_code,
          r.status_code == 200 and r.json()["titulo"] == datos["titulo"])

# 4 ─ inexistente
r = c.get("/solicitudes/99999", headers=SOL)
registrar(4, "CA-03", "Consulta de solicitud inexistente", "GET /solicitudes/99999",
          "404 con mensaje controlado", f"detail='{r.json().get('detail')}'", r.status_code, r.status_code == 404)

# 5 ─ gestión por personal autorizado
r = c.post(f"/solicitudes/{ID}/acciones", json={"comentario": "Tomo el caso para revisión", "estado_nuevo": "EN_REVISION"}, headers=PER)
registrar(5, "CA-02 / RF-03", "Gestión por actor autorizado", f"POST /solicitudes/{ID}/acciones (EN_REVISION)",
          "201, estado EN_REVISION y responsable asignado",
          f"estado={r.json().get('estado')}, responsable={r.json().get('responsable')}", r.status_code,
          r.status_code == 201 and r.json()["estado"] == "EN_REVISION" and r.json()["responsable"] == "Andrea Mejía")

# 6 ─ gestión no autorizada (solicitante) y regla de transición inválida / otro funcionario
r1 = c.post(f"/solicitudes/{ID}/acciones", json={"comentario": "Intento colarme", "estado_nuevo": "FINALIZADA"}, headers=SOL)
r2 = c.post(f"/solicitudes/{ID}/acciones", json={"comentario": "No es mi caso", "estado_nuevo": "EN_GESTION"}, headers=PER2)
r3 = c.post(f"/solicitudes/{ID}/acciones", json={"comentario": "Salto de estado", "estado_nuevo": "FINALIZADA", "respuesta": "Listo ya"}, headers=PER)
r4 = c.get(f"/solicitudes/{ID}", headers=SOL2)
estado_actual = c.get(f"/solicitudes/{ID}", headers=SOL).json()["estado"]
registrar(6, "CA-02 / RNF-02", "Gestión por actor no autorizado y transición inválida",
          "POST .../acciones como solicitante, como otro funcionario y con salto de estado; GET como otro solicitante",
          "403, 403, 409 y 403; el estado no cambia",
          f"códigos={r1.status_code},{r2.status_code},{r3.status_code},{r4.status_code}; estado sigue {estado_actual}",
          f"{r1.status_code}/{r2.status_code}/{r3.status_code}/{r4.status_code}",
          (r1.status_code, r2.status_code, r3.status_code, r4.status_code) == (403, 403, 409, 403) and estado_actual == "EN_REVISION")

# 7 ─ estado coherente
r = c.post(f"/solicitudes/{ID}/acciones", json={"comentario": "Gestionando con secretaría", "estado_nuevo": "EN_GESTION"}, headers=PER)
g = c.get(f"/solicitudes/{ID}", headers=SOL).json()
registrar(7, "CA-03 / RF-04", "Consulta de estado y responsable", f"POST .../acciones (EN_GESTION) y GET /solicitudes/{ID}",
          "Estado EN_GESTION y responsable Andrea Mejía visibles para el solicitante",
          f"estado={g['estado']}, responsable={g['responsable']}", r.status_code,
          r.status_code == 201 and g["estado"] == "EN_GESTION" and g["responsable"] == "Andrea Mejía")

# 8 ─ historial
h = c.get(f"/solicitudes/{ID}/historial", headers=SOL)
estados = [a["estado_resultante"] for a in h.json()]
registrar(8, "CA-04 / RF-05", "Historial de atención", f"GET /solicitudes/{ID}/historial",
          "3 acciones en orden: RECIBIDA, EN_REVISION, EN_GESTION", f"estados={estados}", h.status_code,
          h.status_code == 200 and estados == ["RECIBIDA", "EN_REVISION", "EN_GESTION"])

# 9 ─ finalización, respuesta obligatoria y consulta del solicitante
sin = c.post(f"/solicitudes/{ID}/acciones", json={"comentario": "Cierro el caso", "estado_nuevo": "FINALIZADA"}, headers=PER)
con = c.post(f"/solicitudes/{ID}/acciones", json={"comentario": "Cierro el caso", "estado_nuevo": "FINALIZADA",
                                                 "respuesta": "Tu paz y salvo fue emitido y enviado a tu correo."}, headers=PER)
g = c.get(f"/solicitudes/{ID}", headers=SOL).json()
reabrir = c.post(f"/solicitudes/{ID}/acciones", json={"comentario": "Reabrir", "estado_nuevo": "EN_GESTION"}, headers=PER)
registrar(9, "CA-05 / RF-06", "Finalización y consulta del resultado", f"POST .../acciones (FINALIZADA) y GET /solicitudes/{ID}",
          "Sin respuesta: 422. Con respuesta: 201 y el solicitante la ve. Cerrada no se reabre: 409",
          f"sin respuesta={sin.status_code}, con respuesta={con.status_code}, respuesta visible='{g['respuesta']}', reabrir={reabrir.status_code}",
          f"{sin.status_code}/{con.status_code}/{reabrir.status_code}",
          sin.status_code == 422 and con.status_code == 201 and g["estado"] == "FINALIZADA" and bool(g["respuesta"]) and reabrir.status_code == 409)

# 10 ─ consolidado
r = c.get("/resumen", headers=COO)
no_coord = c.get("/resumen", headers=PER)
j = r.json()
registrar(10, "CA-06 / RF-07", "Consulta consolidada de coordinación", "GET /resumen (coordinación y personal)",
          "200 con totales por estado y por responsable; personal recibe 403",
          f"total={j.get('total')}, por_estado={j.get('por_estado')}, personal→{no_coord.status_code}", f"{r.status_code}/{no_coord.status_code}",
          r.status_code == 200 and j["total"] == sum(j["por_estado"].values()) and j["total"] >= 4 and no_coord.status_code == 403)

# 11 ─ integridad en la BD
with SessionLocal() as db:
    huerfanas = db.execute(text("SELECT COUNT(*) FROM acciones a LEFT JOIN solicitudes s ON s.id=a.solicitud_id WHERE s.id IS NULL")).scalar()
    sin_usuario = db.execute(text("SELECT COUNT(*) FROM solicitudes s LEFT JOIN usuarios u ON u.id=s.solicitante_id WHERE u.id IS NULL")).scalar()
    total_sol = db.execute(text("SELECT COUNT(*) FROM solicitudes")).scalar()
    try:
        db.execute(text("INSERT INTO acciones(solicitud_id,usuario_id,tipo,estado_resultante,comentario,fecha) VALUES (9999,1,'NOTA','RECIBIDA','x','2026-01-01')"))
        db.commit(); rechazo = False
    except Exception:
        db.rollback(); rechazo = True
registrar(11, "RNF-01 / modelo de datos", "Persistencia e integridad de relaciones", "Consultas SQL sobre la base de datos",
          "0 acciones huérfanas, 0 solicitudes sin solicitante y la BD rechaza una llave foránea inexistente",
          f"huérfanas={huerfanas}, sin solicitante={sin_usuario}, solicitudes guardadas={total_sol}, FK rechazada={rechazo}", "—",
          huerfanas == 0 and sin_usuario == 0 and rechazo)

# 12 ─ integración extremo a extremo (API) + interfaz servida
pagina = c.get("/")
reg = c.post("/auth/registro", json={"nombre": "Prueba Final", "email": "final@demo.com", "password": "clave123"})
tok = c.post("/auth/login", json={"email": "final@demo.com", "password": "clave123"}).json()["access_token"]
H = {"Authorization": "Bearer " + tok}
s = c.post("/solicitudes", json={"titulo": "Flujo completo", "descripcion": "Probando el flujo completo de punta a punta.", "categoria": "Otro"}, headers=H).json()
for est in ("EN_REVISION", "EN_GESTION"):
    c.post(f"/solicitudes/{s['id']}/acciones", json={"comentario": f"Paso a {est}", "estado_nuevo": est}, headers=PER)
c.post(f"/solicitudes/{s['id']}/acciones", json={"comentario": "Cierre", "estado_nuevo": "FINALIZADA", "respuesta": "Atendida correctamente."}, headers=PER)
final = c.get(f"/solicitudes/{s['id']}", headers=H).json()
registrar(12, "CA-01 a CA-06", "Integración interfaz–API–base de datos", "GET / y flujo registro→solicitud→gestión→cierre",
          "La página carga (200) y el flujo completo termina FINALIZADA con respuesta. Capturas de la interfaz en evidencias/",
          f"página={pagina.status_code}, registro={reg.status_code}, estado final={final['estado']}", pagina.status_code,
          pagina.status_code == 200 and reg.status_code == 201 and final["estado"] == "FINALIZADA" and final["respuesta"] is not None)

# ─── salida ───
lineas = ["# Resultados de las pruebas funcionales", "",
          "Generado con `python pruebas/ejecutar_pruebas.py` (base de datos temporal con datos ficticios).", "",
          "| # | Requisito | Prueba | Petición | Resultado esperado | Resultado obtenido | HTTP | Estado |",
          "|---|---|---|---|---|---|---|---|"]
for fila in resultados:
    lineas.append("| " + " | ".join(str(x).replace("|", "/") for x in fila) + " |")
aprob = sum(1 for f in resultados if f[-1] == "Aprobada")
lineas += ["", f"**Resumen: {aprob} de {len(resultados)} pruebas aprobadas.**"]
(RAIZ / "evidencias").mkdir(exist_ok=True)
(RAIZ / "evidencias" / "resultados_pruebas.md").write_text("\n".join(lineas), encoding="utf-8")
for f in resultados:
    print(f"{f[0]:>2}  {f[-1]:<9} {f[2]}")
print(f"\n{aprob}/{len(resultados)} aprobadas")
from app.database import engine
engine.dispose()
BD.unlink(missing_ok=True)
sys.exit(0 if aprob == len(resultados) else 1)
