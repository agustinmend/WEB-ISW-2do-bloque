# Symposium - Conference Sessions & Registrations Backend

## Instrucciones para ejecutar el proyecto

Clonar el repositorio.

Requisitos previos: Tener instalado Docker y Docker Compose.

Configuración: Crear un archivo `.env` en la raíz basado en el archivo `.env.example`.

Ejecutar el siguiente comando para levantar toda la infraestructura:

### Bash

```bash
docker compose up --build -d
```

(La base de datos, las migraciones, la creación del superusuario y el seeding de los 300 registros, 15 ponentes y 500 usuarios se ejecutarán de forma completamente automática mediante un script en el primer arranque).

---

# Decisiones de Diseño y Trade-offs

## Arquitectura (Separación de Responsabilidades)

El Django Admin (servido vía Gunicorn) gestiona exclusivamente la escritura, relaciones complejas (M2M) y configuración administrativa. FastAPI (servido vía Uvicorn) gestiona el alto volumen de tráfico de lectura pública. Ambos comparten la base de datos PostgreSQL aislando los datos en el esquema `content`, pero operan de forma completamente independiente. En FastAPI se aplicó el principio de Inversión de Dependencias (DIP de SOLID) utilizando Patrones de Repositorio/Servicio y `typing.Protocol`.

## Caché y Degradación Controlada

Se utiliza Redis para cachear respuestas de lista y detalle. Estrategia: Cache-Aside con TTL. Si Redis colapsa o no es alcanzable, la clase `RedisCache` captura silenciosamente la excepción `redis.ConnectionError` y el sistema omite el caché, redirigiendo la consulta directamente a PostgreSQL.

## Lógica de Negocio (Time-Window Filtering)

La rúbrica exigía una ventana de tiempo timezone-aware. La conversión de zonas horarias se delega al motor de base de datos utilizando la instrucción `AT TIME ZONE` de PostgreSQL. Esto permite filtrar fechas exactas (ej. `America/La_Paz`) a nivel de consulta SQL, evitando cargar miles de registros en la memoria de Python para hacer la conversión manualmente.

## Búsqueda Textual

Se implementó un endpoint dedicado `/search/` utilizando el operador nativo `ILIKE` de PostgreSQL para mantener la infraestructura simple y cumplir estrictamente con los requerimientos.

---

# Cómo probar el sistema

Ejecuta la suite de pruebas desde el contenedor de FastAPI para validar la lógica:

### Bash

```bash
docker compose exec fastapi pytest tests/ -v
```

---

# Endpoints Principales

Frontend / Aplicación Web: `http://localhost/`

Panel de Administración (Django): `http://localhost/admin/`

Documentación OpenAPI (Swagger): `http://localhost/api/openapi.json` y `http://localhost/docs`

Healthchecks (Verifican BD y Redis): `http://localhost/api/v1/healthz` y `http://localhost/healthz/` (Retornan 200/503 según estado de las dependencias).

---

## Lógica de Negocio Implementada

**Time-Window Filtering (Filtrado por Zonas Horarias):**
El requerimiento funcional principal abordado fue el filtrado de sesiones por ventana de tiempo considerando zonas horarias dinámicas enviadas por el cliente.

**Solución aplicada:** Para lograrlo se delegó por completo al motor de base de datos en lugar de procesarla en la aplicación. Al recibir un parámetro de zona horaria (ej. `tz=America/La_Paz`), la consulta SQL cruda utiliza la instrucción nativa `AT TIME ZONE` de PostgreSQL. Esto permite comparar y filtrar las fechas exactas directamente a nivel de motor de base de datos, evitando cargar y transformar miles de registros en la memoria de Python.

---

## Submission Reflection

**La decisión por la que me siento más orgullosa:**
La arquitectura de 3 capas implementada en FastAPI utilizando el tipado `Protocol` para definir los contratos. Esta estructura me permitió cumplir con el Principio de Inversión de Dependencias (SOLID), aislando completamente la capa de caché y los repositorios de datos. La implementación de la "Degradación Controlada" de Redis previene que una caída del servidor en memoria destruya la experiencia del usuario, ya que el sistema captura el error de conexión silenciosamente y vuelve a consumir directo de PostgreSQL.

**La decisión que menos me satisface:**
La complejidad y extensión de las sentencias SQL crudas en la capa de repositorios. No me gusta estructurar el JSON directamente en Postgres (usando `json_build_object` y `json_agg`), el resultado es un código SQL embebido muy extenso y difícil de leer a simple vista. Con más tiempo, me gustaría refactorizar esta capa estructurándolas de una forma mucho más legible y mantenible en el código Python.