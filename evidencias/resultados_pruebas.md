# Resultados de las pruebas funcionales

Generado con `python pruebas/ejecutar_pruebas.py` (base de datos temporal con datos ficticios).

| # | Requisito | Prueba | Petición | Resultado esperado | Resultado obtenido | HTTP | Estado |
|---|---|---|---|---|---|---|---|
| 1 | CA-01 / RF-02 | Registro válido de solicitud | POST /solicitudes | 201 y solicitud recuperable con estado RECIBIDA | id=4, estado=RECIBIDA, GET posterior=200 | 201 | Aprobada |
| 2 | CA-01 / RNF-01 | Registro con datos inválidos | POST /solicitudes (título corto, categoría falsa) | 422 y no se guarda nada | cantidad antes=3, después=3 | 422 | Aprobada |
| 3 | CA-03 / RF-04 | Consulta de solicitud existente | GET /solicitudes/4 | 200 con los datos del caso | titulo='Paz y salvo académico' | 200 | Aprobada |
| 4 | CA-03 | Consulta de solicitud inexistente | GET /solicitudes/99999 | 404 con mensaje controlado | detail='La solicitud no existe' | 404 | Aprobada |
| 5 | CA-02 / RF-03 | Gestión por actor autorizado | POST /solicitudes/4/acciones (EN_REVISION) | 201, estado EN_REVISION y responsable asignado | estado=EN_REVISION, responsable=Andrea Mejía | 201 | Aprobada |
| 6 | CA-02 / RNF-02 | Gestión por actor no autorizado y transición inválida | POST .../acciones como solicitante, como otro funcionario y con salto de estado; GET como otro solicitante | 403, 403, 409 y 403; el estado no cambia | códigos=403,403,409,403; estado sigue EN_REVISION | 403/403/409/403 | Aprobada |
| 7 | CA-03 / RF-04 | Consulta de estado y responsable | POST .../acciones (EN_GESTION) y GET /solicitudes/4 | Estado EN_GESTION y responsable Andrea Mejía visibles para el solicitante | estado=EN_GESTION, responsable=Andrea Mejía | 201 | Aprobada |
| 8 | CA-04 / RF-05 | Historial de atención | GET /solicitudes/4/historial | 3 acciones en orden: RECIBIDA, EN_REVISION, EN_GESTION | estados=['RECIBIDA', 'EN_REVISION', 'EN_GESTION'] | 200 | Aprobada |
| 9 | CA-05 / RF-06 | Finalización y consulta del resultado | POST .../acciones (FINALIZADA) y GET /solicitudes/4 | Sin respuesta: 422. Con respuesta: 201 y el solicitante la ve. Cerrada no se reabre: 409 | sin respuesta=422, con respuesta=201, respuesta visible='Tu paz y salvo fue emitido y enviado a tu correo.', reabrir=409 | 422/201/409 | Aprobada |
| 10 | CA-06 / RF-07 | Consulta consolidada de coordinación | GET /resumen (coordinación y personal) | 200 con totales por estado y por responsable; personal recibe 403 | total=4, por_estado={'RECIBIDA': 1, 'EN_REVISION': 1, 'EN_GESTION': 0, 'FINALIZADA': 2, 'RECHAZADA': 0}, personal→403 | 200/403 | Aprobada |
| 11 | RNF-01 / modelo de datos | Persistencia e integridad de relaciones | Consultas SQL sobre la base de datos | 0 acciones huérfanas, 0 solicitudes sin solicitante y la BD rechaza una llave foránea inexistente | huérfanas=0, sin solicitante=0, solicitudes guardadas=4, FK rechazada=True | — | Aprobada |
| 12 | CA-01 a CA-06 | Integración interfaz–API–base de datos | GET / y flujo registro→solicitud→gestión→cierre | La página carga (200) y el flujo completo termina FINALIZADA con respuesta. Capturas de la interfaz en evidencias/ | página=200, registro=201, estado final=FINALIZADA | 200 | Aprobada |

**Resumen: 12 de 12 pruebas aprobadas.**