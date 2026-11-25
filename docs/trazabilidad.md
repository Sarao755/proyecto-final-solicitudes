# Matriz de trazabilidad — PF-01

Relaciona cada condición de aceptación con su requisito, su implementación, el pull request que la integró y las pruebas que la verifican.

| Condición | Requisito aprobado | Implementación (ruta/componente) | Pull request | Prueba |
|---|---|---|---|---|
| CA-01 | RF-02, RNF-01 | `POST /solicitudes` en `routers/solicitudes.py`; formulario "Nueva solicitud" en `static/index.html` | #4 (API), #6 (interfaz) | P1, P2, P12 |
| CA-02 | RF-03, RN-02, RN-04 | `POST /solicitudes/{id}/acciones`; `requiere_roles` en `security.py`; panel "Gestionar" | #3 (roles), #4 (API), #6 (interfaz) | P5, P6, P12 |
| CA-03 | RF-04 | `GET /solicitudes` y `GET /solicitudes/{id}`; lista y detalle con estado y responsable | #4 (API), #6 (interfaz) | P3, P4, P7 |
| CA-04 | RF-05 | Tabla `acciones` (`models.py`); `GET /solicitudes/{id}/historial`; línea de tiempo en la interfaz | #2 (modelos), #4 (API), #6 (interfaz) | P8, P11 |
| CA-05 | RF-06, RN-03, RN-05 | Campo `respuesta`; bloque "Respuesta final" en el detalle | #4 (API), #6 (interfaz) | P9 |
| CA-06 | RF-07 | `GET /resumen` en `routers/resumen.py`; panel "Resumen general" | #5 (API), #6 (interfaz) | P10 |

## Requisitos transversales
| Requisito | Implementación | Pull request |
|---|---|---|
| RF-01 (registro e inicio de sesión) | `routers/auth.py`, `security.py` | #3 |
| RNF-01 (validación en el servidor) | `schemas.py` y reglas en `routers/solicitudes.py` | #3, #4 |
| RNF-02 (permisos por rol) | `requiere_roles` en `security.py` | #3 |
| RNF-03 (sin secretos en el repositorio) | `.gitignore` y `.env.example` | commit inicial en `main` |
| RNF-05 (contraseñas con hash y JWT) | `security.py` | #3 |

## Pruebas
Las pruebas P1 a P12 están en [`evidencias/resultados_pruebas.md`](../evidencias/resultados_pruebas.md) y se ejecutan con `python pruebas/ejecutar_pruebas.py` (PR #7). Las capturas de la interfaz están en `evidencias/ui_*.png`.

## Pull requests
| PR | Rama |
|---|---|
| #1 | `docs/requisitos-diseno` |
| #2 | `feat/base-datos-modelos` |
| #3 | `feat/auth-roles` |
| #4 | `feat/api-solicitudes` |
| #5 | `feat/resumen-coordinacion` |
| #6 | `feat/interfaz-web` |
| #7 | `test/pruebas-funcionales` |
| #8 | `docs/readme-trazabilidad` |
