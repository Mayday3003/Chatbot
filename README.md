# README — Soporte Tecnológico Asistido por IA (Django + React) — 100% Gratis

Este documento describe de forma completa y libre (sin servicios pagos) la arquitectura, la estructura del proyecto, dependencias, flujos de datos, APIs, consideraciones de seguridad, pruebas y despliegue para construir una solución de soporte técnico con chatbot (PLN) que soporte escalamiento a agentes humanos y aprendizaje continuo.

Contenido
- 1. Resumen de la solución
- 2. Requisitos y librerías gratuitas recomendadas
- 3. Estructura propuesta del proyecto (detallada)
- 4. Modelos conceptuales (esquemas y relaciones)
- 5. Endpoints / APIs (especificación funcional)
- 6. Flujo de interacción (detallado)
- 7. Chatbot: arquitectura técnica y pipeline
- 8. Escalamiento automatizado a agentes humanos (reglas y acciones)
- 9. Sistema de retroalimentación (feedback loop)
- 10. Seguridad y buenas prácticas
- 11. Observabilidad y métricas
- 12. Testing y QA
- 13. Despliegue (opciones gratuitas y docker)
- 14. Plan de trabajo sugerido (fases)
- 15. Checklist final
- 16. Variables de entorno (ejemplos)
- 17. Recursos y enlaces útiles
- 18. Recomendaciones finales

---

## 1. Resumen de la solución (100% gratis)

Arquitectura basada en aplicaciones open-source y autoalojadas:
- Backend: Django + Django REST Framework + Django Channels.
- Frontend: React (Vite o CRA).
- Auth: JWT con djangorestframework-simplejwt.
- Real-time: WebSocket via Django Channels; Redis para canalización en producción.
- Chatbot: recuperación + generación (retrieval+generation) con sentence-transformers, FAISS/Annoy y modelos locales de transformers (ej.: google/flan-t5-small).
- Tareas asíncronas: Celery + Redis.
- Orquestación: Docker Compose (CE). Opcionalmente Kubernetes para entornos más complejos.

Objetivo: atención 24/7 por chatbot con memoria (KB indexada), escalamiento a agentes y pipeline de retroalimentación para mejora continua sin depender de servicios de pago.

---

## 2. Requisitos y librerías gratuitas recomendadas

Backend (Python / Django)
- Python 3.10+
- Django 4.x
- djangorestframework
- djangorestframework-simplejwt
- channels
- channels_redis (si usa Redis)
- psycopg2-binary (Postgres) o sqlite3 para desarrollo
- celery
- redis
- sentence-transformers
- faiss-cpu o annoy
- transformers
- scikit-learn, pandas
- python-dotenv o django-environ
- drf-spectacular o redoc
- pytest, pytest-django

Frontend (React)
- React 18+
- Vite o Create React App
- axios (o fetch)
- Redux Toolkit o React Context
- WebSocket nativo
- Tailwind CSS o Material UI
- formik o react-hook-form
- Jest + React Testing Library

Infra / DevOps
- Docker CE
- docker-compose
- PostgreSQL (OSS) o SQLite (dev)
- Redis
- Nginx
- Certbot (Let's Encrypt)
- Prometheus + Grafana
- Opcional: Sentry autoalojado o alternativas OSS

Notas: todas las listas anteriores son herramientas gratuitas si se autoalojan.

---

## 3. Estructura propuesta del proyecto (detallada)

Raíz del repositorio sugerida:

- README.md (este documento)
- .env.example
- docker-compose.yml
- /backend
  - manage.py
  - requirements.txt
  - /config
    - settings.py
    - asgi.py
    - wsgi.py
  - /apps
    - /users
      - models.py
      - serializers.py
      - views.py
      - urls.py
    - /tickets
      - models.py
      - serializers.py
      - views.py
      - urls.py
    - /chatbot
      - models.py (KnowledgeEntry, Conversation)
      - retriever.py (embeddings + faiss)
      - generator.py (transformers pipeline)
      - tasks.py (celery jobs)
    - /notifications
    - /analytics
  - /celery
  - /migrations
- /frontend
  - package.json
  - /src
    - /components
      - /ChatWidget
      - /AdminPanel
      - /Auth
      - /TicketList
    - /pages
      - /Support
      - /Admin
    - /services
      - api.js
      - websocket.js
    - /store
      - slices
- /infra
  - docker/
  - nginx/
- /docs
  - architecture.md
  - api-spec.yaml
  - operational-runbook.md
- /tests
  - backend/
  - frontend/

Notas de diseño:
- Mantener apps Django pequeñas y con responsabilidades claras.
- Versionar esquema de embeddings (modelo + dimensiones) para compatibilidad.

---

## 4. Modelos conceptuales (sin código)

User
- id (UUID/PK)
- username
- email
- password_hash
- role (user/admin)
- is_active, is_staff
- created_at, updated_at

Ticket
- id
- title
- description
- created_by (FK User)
- assigned_to (FK User, opcional)
- status (open, in_progress, closed)
- priority
- tags
- created_at, updated_at

Message
- id
- ticket (FK)
- sender_type (user/system/admin)
- sender_id (FK nullable)
- text
- is_bot (bool)
- attachments (file refs)
- created_at

KnowledgeEntry (KB)
- id
- title
- problem_description
- solution_text
- tags
- source (manual/auto)
- metadata (version, locale)
- created_at
- embedding_vector (almacenado externamente en FAISS / path)

Conversation
- id
- user (FK o anon_session_id)
- session_id
- messages (relation a Message)
- metadata (device, locale)
- created_at

Feedback
- id
- reference_type (message/conversation)
- reference_id
- rating (positive/negative/scale)
- comment
- created_at

Índices y relaciones
- Indexar KB por tags y por vector (FAISS).
- Registrar relaciones Ticket <-> Conversation si la interacción se escala.

---

## 5. Endpoints / APIs (descripción funcional)

Autenticación
- POST /api/auth/register/ — registrar usuario
- POST /api/auth/login/ — obtener access + refresh JWT
- POST /api/auth/token/refresh/ — refresh
- GET /api/auth/me/ — perfil actual

Tickets
- POST /api/tickets/ — crear ticket
- GET /api/tickets/ — listar (filtrado por rol)
- GET /api/tickets/{id}/ — obtener ticket + mensajes
- PATCH /api/tickets/{id}/ — actualizar (admin o owner)
- POST /api/tickets/{id}/messages/ — añadir mensaje
- POST /api/tickets/{id}/close/ — cerrar ticket

Chat / Conversación
- POST /api/chat/session/ — crear sesión (devuelve session_id)
- POST /api/chat/message/ — enviar mensaje (REST fallback)
- WS /ws/chat/{session_id}/ — canal WebSocket para mensajes en tiempo real
- GET /api/chat/conversations/{session_id}/ — histórico
- POST /api/chat/feedback/ — enviar feedback (message_id, rating, comment)

KB / Admin
- GET /api/kb/ — listar entradas
- POST /api/kb/ — crear entrada (admin)
- GET /api/kb/{id}/ — detalle
- PUT/PATCH /api/kb/{id}/ — actualizar
- DELETE /api/kb/{id}/ — eliminar
- POST /api/kb/reindex/ — endpoint protegido para reindexar embeddings

Operaciones / Admin
- GET /api/admin/users/
- POST /api/admin/escalate/ — forzar escalamiento
- GET /api/admin/metrics/ — métricas básicas

Consideraciones de diseño de APIs
- Usar paginación en listados (DRF paginators).
- Filtrado y búsqueda en tickets y KB (by tags, status, dates).
- Rate limiting si se expone públicamente (middleware/simple quotas).

---

## 6. Flujo de interacción (alto y medio nivel)

1) Inicio
- Usuario inicia sesión o abre widget anónimo.
- Frontend crea session_id vía /api/chat/session/.

2) Interacción chat
- Usuario envía mensaje por WS o REST.
- Backend guarda mensaje provisionalmente y calcula embedding (async o sync según latencia).
- Retriever: consulta FAISS con embedding para obtener top-K documentos.
- Si top match > umbral_confianza:
  - Generador arma respuesta basada en plantilla + snippets de KB y la devuelve.
- Si no hay matches confiables:
  - Generador (modelo local) produce respuesta usando prompt con top-K docs (si existen) o respuesta generada desde cero.

3) Post-procesamiento
- Respuesta enviada al usuario y persistida en BD (Message.is_bot = True).
- Si confidence baja o regla de escalamiento aplica, backend crea un Ticket y notifica admins.
- Frontend ofrece opción de feedback (útil/no útil) y 'hablar con agente'.

4) Feedback y aprendizaje
- Feedback almacenado y agrupado por jobs (Celery) para crear dataset de reentrenamiento o crear nuevas entradas en KB.
- Reindexado de KB y reembedding puede ejecutarse periódicamente o a demanda.

---

## 7. Chatbot: arquitectura técnica (100% libre)

Retriever
- Embeddings: sentence-transformers (modelo configurable, p. ej. paraphrase-MiniLM).
- Indexación: faiss-cpu (para producción local) o annoy como alternativa ligera.
- Búsqueda: similaridad coseno o inner product con normalización; top-K retrieval y thresholding.

Generator
- Modelos: Hugging Face transformers locales (ej.: google/flan-t5-small). Usar pipelines de generación con parámetros límite (max_length, temperature).
- Si hardware limitado: usar templates + relleno con snippets de KB en lugar de generación completa.

Pipeline sugerido (pseudocódigo de alto nivel)
1. embedding = embed(question)
2. docs = faiss.search(embedding, top_k)
3. if docs[0].score > THRESHOLD:
     response = fill_template(docs[0:top_n])
   else:
     prompt = build_prompt(question, docs)
     response = generator.generate(prompt)
4. store response, return to user

Gestión de contexto
- Mantener ventana de contexto por conversación (N últimos mensajes).
- Para prompts, incluir solo los mensajes más relevantes y las top-k docs.

Gestión de KB y versionamiento
- Mantener metadatos de versión de embeddings y modelo.
- Al actualizar modelo de embeddings, reindexar KB y regenerar embeddings.

---

## 8. Escalamiento automatizado a agentes humanos (reglas libres)

Reglas típicas (configurables):
- Confidence < umbral_confianza.
- Contenido con palabras clave: "error crítico", "no funciona", "urgente".
- Usuario solicita "hablar con agente".
- Interacciones > N sin resolución.

Acciones al escalar:
- Crear Ticket con historial (últimos mensajes), etiquetas y prioridad.
- Notificar por email (SMTP local) o webhook a sistema interno.
- Asignar ticket a cola/área según palabras clave o tags.
- Notificar admins en panel y por correo.

---

## 9. Sistema de retroalimentación (feedback loop) — 100% gratis

Componentes:
- UI: botones de útil/no útil, campo de comentario y opción de reportar.
- Almacenamiento: tabla Feedback referenciando mensajes/conv.
- Jobs (Celery): agrupan feedback negativo, generan dataset de ejemplos problemáticos y sugieren entradas para KB.
- Opciones:
  - Reentrenamiento local (fine-tuning) cuando exista volumen de datos.
  - Flujo preferible: creación manual de entradas en KB a partir de feedback validado por admins (menos costoso y más seguro).

Pipeline mínimo viable:
1. Recibir feedback y guardarlo.
2. Job nocturno agrega casos negativos a carpeta /data/feedback/
3. Admin revisa y convierte casos a KnowledgeEntry o etiqueta para reentrenamiento.
4. Reindexar embeddings.

---

## 10. Seguridad y buenas prácticas (sin coste adicional)

Transporte y autenticación
- HTTPS obligatorio con Certbot + Nginx.
- JWT con expiraciones razonables y refresh tokens.
- Protección CSRF para endpoints que lo requieran.

Datos y privacidad
- Encriptar secrets en entorno; no subir .env a repo.
- Hash de contraseñas con algoritmos seguros (Django default, preferir Argon2 si disponible).
- Políticas de retención de conversaciones y anonimización de PII.

Acceso y permisos
- Validar roles y permisos en backend (DRF permissions).
- Escuchar privilegios mínimos: solo admin puede CRUD KB.

Hardening
- Rate limiting y protección contra abusos.
- Escaneo de dependencias (safety, pip-audit).
- Monitorizar logs de acceso anómalos.

---

## 11. Observabilidad y métricas (todas las herramientas listadas tienen opciones gratuitas)

Métricas recomendadas
- Latencia de respuestas (avg/percentiles).
- Tiempo de respuesta del retriever vs generator.
- Volumen de conversaciones por hora/día.
- Tasa de escalamiento y tickets abiertos por día.
- Calidad: % de feedback positivo.

Herramientas
- Prometheus para recolección de métricas.
- Grafana para dashboards.
- Logs: archivos + logrotate o ELK si se requiere.
- APM/errores: Sentry autoalojado o similar.

---

## 12. Testing y QA

Backend
- pytest + pytest-django para unit y integration tests.
- Tests para: autenticación, permisos, endpoints críticos, jobs Celery, retriever (recall@k tests con fixtures).

Frontend
- Jest + React Testing Library para componentes.
- Tests E2E: Playwright o Cypress (escenario de chat, registro, escalamiento).

IA
- Evaluación de retrieval: recall@k, MRR sobre dataset separado.
- Evaluación de generación: revisión humana, pruebas A/B locales, métricas de toxicidad si aplica.

CI
- GitHub Actions (gratuito para repos open-source) para ejecutar tests y linters.

---

## 13. Despliegue (opciones gratuitas)

Local / On-prem
- Docker + docker-compose es la forma recomendada para desplegar en infra propia.
- Configurar nginx como proxy reverso y certbot para TLS.

docker-compose (orientativo)
- Servicios: backend, frontend, db (postgres), redis, celery-worker, celery-beat, nginx
- Volúmenes: persistencia de DB y FAISS index

Comandos básicos
- Development: docker-compose up --build
- Migraciones: docker-compose run backend python manage.py migrate
- Crear superuser: docker-compose run backend python manage.py createsuperuser

Backups
- Exportar dumps de Postgres periódicamente.
- Guardar snapshots de FAISS index y directorio de modelos.

Escalado
- Para alta carga, separar servicios, añadir balanceador, y considerar Kubernetes.

---

## 14. Plan de trabajo sugerido (fases y entregables)

Fase 0 — Preparación
- Repo, CI básico, entorno de Docker.

Fase 1 — MVP
- Auth + roles.
- Tickets CRUD + panel admin básico.
- Chat widget (WebSocket) y persistencia de mensajes.

Fase 2 — IA local
- Embeddings (sentence-transformers) + FAISS.
- Integración con modelo local (transformers) para generación.
- Reglas de escalamiento y feedback.

Fase 3 — Mejora
- Pipeline de reindexado y reentrenamiento local (Celery).
- Dashboard de métricas y alertas.

Entrega por fase: repositorio con tests, docker-compose, documentación y runbook.

---

## 15. Checklist final (libre)

- [ ] Especificación OpenAPI
- [ ] Esquema de BD documentado
- [ ] Auth + roles implementados
- [ ] ChatWidget UI funcional
- [ ] Endpoints tickets y chat implementados
- [ ] Channels (WebSocket) funcionando
- [ ] Retriever (FAISS) + embeddings funcionando
- [ ] Generador local (transformers) o pipeline de plantillas
- [ ] Escalamiento y notificaciones (SMTP)
- [ ] Feedback y pipeline de recolección
- [ ] Jobs asíncronos (Celery + Redis)
- [ ] Documentación y operational runbook

---

## 16. Variables de entorno (ejemplos)

# Django & DB
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://user:pass@postgres:5432/dbname

# Redis & Celery
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/1

# JWT
SIMPLE_JWT_SECRET_KEY=your-jwt-secret
ACCESS_TOKEN_LIFETIME=300
REFRESH_TOKEN_LIFETIME=86400

# Embeddings & FAISS
EMBEDDING_MODEL_NAME=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
FAISS_INDEX_PATH=/data/faiss/index.faiss
EMBEDDING_DIM=384

# Generador
GENERATOR_MODEL_NAME=google/flan-t5-small

# SMTP (dev)
SMTP_HOST=mailhog
SMTP_PORT=1025

# Misc
ALLOWED_HOSTS=localhost,127.0.0.1
DEBUG=False

---

## 17. Recursos y enlaces útiles
- Django: https://www.djangoproject.com/
- Django REST Framework: https://www.django-rest-framework.org/
- Django Channels: https://channels.readthedocs.io/
- Celery: https://docs.celeryq.dev/
- Redis: https://redis.io/
- Sentence-Transformers: https://www.sbert.net/
- FAISS: https://github.com/facebookresearch/faiss
- Transformers (Hugging Face): https://huggingface.co/docs/transformers/index
- Docker: https://www.docker.com/
- Vite: https://vitejs.dev/
- Tailwind CSS: https://tailwindcss.com/
- Prometheus: https://prometheus.io/
- Grafana: https://grafana.com/

---

## 18. Recomendaciones finales (prácticas)

- Comenzar con retrieval + plantillas para una solución útil y de bajo costo computacional.
- Mantener KB curada por administradores para mejorar precisión y reducir necesidad de reentrenamiento.
- Registrar y auditar conversaciones y cambios en KB.
- Definir política de retención y anonimización de PII desde el inicio.
- Automatizar backups del índice FAISS y de la base de datos.
- Medir calidad con métricas simples (recall@k, % feedback positivo) y mejorar iterativamente.

---

## Documentos complementarios sugeridos (crear en /docs)
- architecture.md: diagramas y decisiones arquitectónicas.
- api-spec.yaml: OpenAPI spec para todos los endpoints.
- operational-runbook.md: procedimientos para backups, despliegue, rotación de claves y recuperación ante desastres.
- embedding-versioning.md: formato y proceso para actualizar embeddings y reindexado.


Fin del documento.