Setup rápido (desarrollo local)

1. Clonar repo
2. Crear .env a partir de .env.example
3. Backend:
   - Entrar en backend/ y crear virtualenv
   - pip install -r requirements.txt (nota: faiss-cpu, transformers y torch pueden requerir ruedas específicas según SO)
   - python manage.py migrate
   - python manage.py runserver
4. Frontend:
   - Entrar en frontend/, npm install
   - npm run dev

Notas:
- Para un entorno ligero de desarrollo puedes comentar/importar reemplazos de sentence-transformers si no quieres instalar modelos grandes.
- Docker-compose incluido en la raíz es orientativo. Ajusta imágenes si necesitas soporte GPU.
