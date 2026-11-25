# Requisitos — Sistema de gestión de solicitudes de servicio (PF-01)

## 1. Problema y alcance
Una organización recibe solicitudes por correo, llamadas y WhatsApp. La información está dispersa: el usuario no sabe si su solicitud llegó ni en qué estado está, el personal no identifica los casos pendientes y la coordinación no tiene una visión consolidada.

**Alcance:** recepción, evaluación, gestión, seguimiento y finalización de una solicitud, con trazabilidad de las acciones y respuesta al solicitante.
**Fuera de alcance** (según la guía): facturación, pagos, WhatsApp, envío real de correos, integración con plataformas externas.

## 2. Actores
| Actor | Qué hace en el sistema |
|---|---|
| Solicitante | Se registra, presenta solicitudes, consulta estado, historial y respuesta de **sus** solicitudes. |
| Personal de atención | Ve todas las solicitudes, las evalúa, toma las que no tienen responsable, las gestiona y las cierra. |
| Coordinación | Todo lo del personal sobre cualquier solicitud, y además consulta el resumen consolidado. |

## 3. Requisitos funcionales
| ID | Requisito | Condición |
|---|---|---|
| RF-01 | Registrar usuarios (rol solicitante) e iniciar sesión. | — |
| RF-02 | El solicitante registra una solicitud con título, descripción, categoría y prioridad; queda en estado RECIBIDA. | CA-01 |
| RF-03 | El personal autorizado evalúa y gestiona una solicitud: cambia su estado o agrega notas de seguimiento. | CA-02 |
| RF-04 | Cualquier actor autorizado consulta el estado y el responsable de una solicitud. | CA-03 |
| RF-05 | Cada acción queda registrada (quién, qué, cuándo, estado resultante) y se puede consultar el historial. | CA-04 |
| RF-06 | Al finalizar o rechazar se guarda una respuesta que el solicitante puede consultar. | CA-05 |
| RF-07 | La coordinación consulta un resumen: total, solicitudes por estado, sin responsable y carga por responsable. | CA-06 |

## 4. Requisitos no funcionales
| ID | Requisito |
|---|---|
| RNF-01 | Validación de datos en el servidor aunque la petición no venga de la interfaz. |
| RNF-02 | Permisos por rol: el solicitante solo ve lo suyo; solo personal y coordinación gestionan. |
| RNF-03 | Sin secretos en el repositorio: `.env` fuera de Git y `.env.example` sin claves reales. |
| RNF-04 | Datos de demostración ficticios. |
| RNF-05 | Contraseñas almacenadas con hash (PBKDF2) y sesión con token JWT con vencimiento. |
| RNF-06 | Los errores devuelven mensajes claros sin revelar información interna. |

## 5. Reglas de negocio
| ID | Regla |
|---|---|
| RN-01 | Una solicitud nueva nace en RECIBIDA. Quien la pasa a EN_REVISION queda como responsable. |
| RN-02 | Transiciones permitidas: RECIBIDA→EN_REVISION; EN_REVISION→EN_GESTION o RECHAZADA; EN_GESTION→FINALIZADA. |
| RN-03 | Finalizar o rechazar exige escribir una respuesta para el solicitante. |
| RN-04 | El personal solo gestiona solicitudes sin responsable o asignadas a él; coordinación gestiona cualquiera. |
| RN-05 | Una solicitud FINALIZADA o RECHAZADA no se modifica más. |

## 6. Criterios de aceptación
| Condición | Criterio verificable |
|---|---|
| CA-01 | Tras `POST /solicitudes`, la solicitud se recupera con `GET /solicitudes/{id}` y estado RECIBIDA. |
| CA-02 | Una acción del personal cambia el estado y queda registrada; un solicitante recibe 403. |
| CA-03 | El solicitante ve estado y responsable coherentes con las acciones realizadas. |
| CA-04 | `GET /solicitudes/{id}/historial` devuelve las acciones en orden cronológico. |
| CA-05 | Una solicitud finalizada muestra la respuesta al solicitante. |
| CA-06 | `GET /resumen` integra varias solicitudes por estado y por responsable. |

## 7. Supuestos pendientes de confirmar con el docente
> Completar esta sección con la entrevista real. Lo que sigue son supuestos hechos para poder avanzar.

| # | Supuesto | Pregunta para el docente | Respuesta |
|---|---|---|---|
| S1 | Cualquier persona puede registrarse como solicitante; personal y coordinación los crea el administrador. | ¿Quién crea las cuentas del personal? | _pendiente_ |
| S2 | Los estados son RECIBIDA, EN_REVISION, EN_GESTION, FINALIZADA y RECHAZADA. | ¿Los estados son suficientes? | _pendiente_ |
| S3 | Las categorías son Trámite, Orientación, Atención administrativa y Otro. | ¿Qué tipos de solicitud maneja la organización? | _pendiente_ |
| S4 | El responsable es quien toma la solicitud en revisión. | ¿La coordinación debería poder reasignar? | _pendiente_ |
| S5 | Una solicitud cerrada no se reabre. | ¿Debe existir la opción de reabrir? | _pendiente_ |

## 8. Registro de entrevista
- Fecha: _completar_
- Preguntas y respuestas: _completar con la tabla de supuestos_
- Acuerdos: _completar_
