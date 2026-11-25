# Sistema de gestión de solicitudes de servicio (PF-01)

## 1. Información general
- **Proyecto:** gestión de solicitudes de servicio — recepción, evaluación, gestión, seguimiento y finalización.
- **Integrante:** Sara Quimbayo (GitHub: Sarao755) — trabajo individual: análisis, diseño, backend, frontend, pruebas y documentación.
- **Asignatura:** Aplicaciones y Servicios Web — Tecnología en Desarrollo de Software.
- **Fecha:** 25 de noviembre de 2026 · **Repositorio:** https://github.com/Sarao755/proyecto-final-solicitudes

## 2. Descripción del sistema
Una organización recibe solicitudes por canales dispersos y no puede dar trazabilidad. El sistema permite que un **solicitante** presente su solicitud y vea su estado y respuesta, que el **personal de atención** la evalúe, gestione y finalice, y que la **coordinación** consulte un resumen consolidado. Cada acción queda registrada en un historial.
Requisitos completos: [`docs/requisitos.md`](docs/requisitos.md).

## 3. Requisitos y alcance
- **Método:** análisis de la guía PF-01 y supuestos de proceso, pendientes de confirmar con el docente (sección 7 de `docs/requisitos.md`).
- **Requisitos:** RF-01 a RF-07, RNF-01 a RNF-06 y reglas de negocio RN-01 a RN-05, asociados a las condiciones CA-01 a CA-06.
- **Fuera de alcance:** facturación, pagos, WhatsApp, correos reales e integraciones externas.

## 4. Arquitectura, diseño de API y modelo de datos
- Frontend en HTML/JavaScript → API REST con FastAPI → base de datos SQLite (SQLAlchemy).
- Tablas: `usuarios`, `solicitudes`, `acciones` (relaciones 1—N con llaves foráneas).
- Diagramas, estados, decisiones técnicas y especificación de la API: [`docs/diseno.md`](docs/diseno.md).
- Capturas de la interfaz: carpeta [`evidencias/`](evidencias/).

## 5. Configuración del entorno
Requisitos: Python 3.11 o superior y Git.
```bash
git clone https://github.com/Sarao755/proyecto-final-solicitudes.git
cd proyecto-final-solicitudes
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # Windows: copy .env.example .env  (y cambia SECRET_KEY)
python seed.py                     # crea las tablas y carga datos ficticios
uvicorn app.main:app --reload      # servidor en http://localhost:8000
```
- Interfaz: <http://localhost:8000> · Documentación interactiva de la API: <http://localhost:8000/docs>
- La base de datos se crea sola (`app.db`). Para reiniciarla: borrar `app.db` y ejecutar `python seed.py`.

**Usuarios de demostración** (clave `demo123`): `solicitante@demo.com`, `solicitante2@demo.com`, `personal@demo.com`, `personal2@demo.com`, `coordinacion@demo.com`.

## 6. Servicios web implementados
| Método | Ruta | Descripción | Requisito |
|---|---|---|---|
| POST | `/auth/registro` | Registra un solicitante | RF-01 |
| POST | `/auth/login` | Inicia sesión y devuelve el token | RF-01 |
| GET | `/auth/me` | Datos del usuario actual | RF-01 |
| POST | `/solicitudes` | Crea una solicitud (solicitante) | RF-02 |
| GET | `/solicitudes?estado=` | Lista solicitudes (el solicitante solo ve las suyas) | RF-04 |
| GET | `/solicitudes/{id}` | Detalle, estado, responsable y respuesta | RF-04, RF-06 |
| GET | `/solicitudes/{id}/historial` | Acciones de atención | RF-05 |
| POST | `/solicitudes/{id}/acciones` | Gestiona: cambia estado o agrega nota (personal, coordinación) | RF-03, RF-06 |
| GET | `/resumen` | Resumen consolidado (coordinación) | RF-07 |
| GET | `/meta` | Estados, transiciones, categorías y prioridades | — |

**Ejemplo — crear solicitud** (`Authorization: Bearer <token>`)
```json
POST /solicitudes
{ "titulo": "Paz y salvo académico", "descripcion": "Necesito el paz y salvo para mi grado.", "categoria": "Trámite", "prioridad": "alta" }
→ 201 { "id": 4, "estado": "RECIBIDA", "responsable": null, ... }
```
**Errores controlados:** `401` sin sesión, `403` sin permiso, `404` recurso inexistente, `409` transición no permitida o solicitud cerrada, `422` datos inválidos.

## 7. Pruebas de API e integración y evidencias
Las 12 pruebas mínimas de la Actividad 6 están en [`evidencias/resultados_pruebas.md`](evidencias/resultados_pruebas.md) (id, requisito, petición, esperado, obtenido, código HTTP y estado).

**Reproducirlas**
1. Automática (usa una base temporal): `python pruebas/ejecutar_pruebas.py`.
2. Manual con Swagger: abrir `/docs`, usar *Authorize* con el token de `POST /auth/login` y ejecutar los endpoints.
3. Interfaz: ingresar con cada usuario de demostración y repetir el flujo (capturas en `evidencias/ui_*.png`; se regeneran con `python pruebas/capturas_ui.py`).

| Evidencia | Condición |
|---|---|
| `ui_01`, `ui_02` — solicitante registra la solicitud | CA-01 |
| `ui_03`, `ui_04` — personal gestiona y finaliza | CA-02, CA-03, CA-04 |
| `ui_05` — solicitante ve la respuesta | CA-05 |
| `ui_06` — coordinación ve el resumen | CA-06 |

Matriz de trazabilidad: [`docs/trazabilidad.md`](docs/trazabilidad.md).

## 8. Control de versiones
Repositorio: <https://github.com/Sarao755/proyecto-final-solicitudes>. El trabajo se hizo en ramas, con commits descriptivos y un pull request por cada parte, todos fusionados en `main`.

| PR | Rama | Qué aporta | Requisitos |
|---|---|---|---|
| [#1](https://github.com/Sarao755/proyecto-final-solicitudes/pull/1) | `docs/requisitos-diseno` | Requisitos, reglas de negocio y diseño | CA-01 a CA-06 |
| [#2](https://github.com/Sarao755/proyecto-final-solicitudes/pull/2) | `feat/base-datos-modelos` | Configuración, conexión y modelos | CA-04, RNF-01 |
| [#3](https://github.com/Sarao755/proyecto-final-solicitudes/pull/3) | `feat/auth-roles` | Registro, login, JWT y roles | RF-01, RNF-02, RNF-05 |
| [#4](https://github.com/Sarao755/proyecto-final-solicitudes/pull/4) | `feat/api-solicitudes` | Ciclo de vida de la solicitud | CA-01, CA-02, CA-03, CA-05 |
| [#5](https://github.com/Sarao755/proyecto-final-solicitudes/pull/5) | `feat/resumen-coordinacion` | Resumen consolidado y arranque de la app | CA-06, RF-07 |
| [#6](https://github.com/Sarao755/proyecto-final-solicitudes/pull/6) | `feat/interfaz-web` | Interfaz web para los tres roles | CA-01 a CA-06 |
| [#7](https://github.com/Sarao755/proyecto-final-solicitudes/pull/7) | `test/pruebas-funcionales` | 12 pruebas y capturas | CA-01 a CA-06 |
| [#8](https://github.com/Sarao755/proyecto-final-solicitudes/pull/8) | `docs/readme-trazabilidad` | README y matriz de trazabilidad | CA-01 a CA-06 |

Aportes: trabajo individual de Sara Quimbayo; todos los commits y pull requests son suyos y se pueden revisar en la pestaña *Pull requests* y en el historial de commits del repositorio.

## 9. Conclusiones y limitaciones
- **Cumplimiento:** el flujo completo (registro → evaluación → gestión → finalización → consulta de respuesta → resumen) funciona de extremo a extremo y cubre CA-01 a CA-06.
- **Dificultades:** SQLite no aplica llaves foráneas por defecto (se activaron con `PRAGMA foreign_keys=ON`); las reglas de transición se centralizaron para que API e interfaz no se contradigan.
- **Limitaciones:** el personal y la coordinación se crean con `seed.py` (no hay pantalla de administración); no hay reasignación de responsable ni reapertura de solicitudes; los supuestos de `docs/requisitos.md` están pendientes de confirmación con el docente.
