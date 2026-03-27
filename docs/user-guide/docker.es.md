# Despliegue con Docker

Despliega RUSLE como una aplicación en contenedor usando Docker.

## Requisitos Previos

- [Docker](https://docs.docker.com/get-docker/) instalado
- [Docker Compose](https://docs.docker.com/compose/install/) (normalmente incluido con Docker Desktop)
- Credenciales de Google Earth Engine (autenticadas localmente)

## Inicio Rápido

```bash
# Autenticarse en GEE en la máquina host primero
earthengine authenticate

# Iniciar la aplicación
docker-compose up -d
```

Accede en **[http://localhost:8000/app](http://localhost:8000/app)**

## Configuración

### Variables de Entorno

Crea un archivo `.env` o establece las variables en `docker-compose.yml`:

| Variable | Por Defecto | Descripción |
|----------|-------------|-------------|
| `RUSLE_GEE_PROJECT` | `ee-nriveras` | ID del proyecto Google Earth Engine |
| `RUSLE_DEBUG` | `false` | Habilitar registro de depuración |
| `RUSLE_MAX_UPLOAD_SIZE_MB` | `50` | Tamaño máximo de carga de archivo |
| `RUSLE_MAX_AOI_AREA_KM2` | `50000` | Área máxima de interés |
| `RUSLE_DEFAULT_EXPORT_SCALE` | `90` | Resolución de exportación por defecto (metros) |

### docker-compose.yml

```yaml
services:
  rusle-app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: rusle-web
    ports:
      - "8000:8000"
    environment:
      - RUSLE_GEE_PROJECT=${RUSLE_GEE_PROJECT:-ee-nriveras}
      - RUSLE_DEBUG=${RUSLE_DEBUG:-false}
    volumes:
      # Credenciales GEE (requeridas)
      - ~/.config/earthengine:/home/appuser/.config/earthengine:ro
      # Persistencia de datos
      - ./data/uploads:/app/data/uploads
      - ./data/output:/app/data/output
    restart: unless-stopped
```

## Montajes de Volúmenes

| Montaje | Propósito |
|---------|-----------|
| `~/.config/earthengine` | Credenciales de autenticación GEE (solo lectura) |
| `./data/uploads` | Shapefiles y GeoJSON cargados |
| `./data/output` | Salidas generadas y exportaciones |

!!! warning "Credenciales Requeridas"
    El contenedor requiere credenciales GEE montadas desde el host. Siempre autentícate con `earthengine authenticate` antes de ejecutar.

## Construir la Imagen

### Usando Docker Compose

```bash
# Construir e iniciar
docker-compose up --build

# Solo construir
docker-compose build
```

### Usando Docker Directamente

```bash
# Construir imagen
docker build -t rusle-app .

# Ejecutar contenedor
docker run -d \
  -p 8000:8000 \
  -v ~/.config/earthengine:/home/appuser/.config/earthengine:ro \
  -v $(pwd)/data:/app/data \
  -e RUSLE_GEE_PROJECT=tu-id-de-proyecto \
  --name rusle-web \
  rusle-app
```

## Despliegue en Producción

### Con Proxy Inverso Nginx

```yaml
# docker-compose.prod.yml
services:
  rusle-app:
    build: .
    expose:
      - "8000"
    environment:
      - RUSLE_DEBUG=false

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - rusle-app
```

### Verificaciones de Salud

La aplicación expone un endpoint de salud:

```bash
curl http://localhost:8000/health
```

## Solución de Problemas

### El Contenedor No Inicia

Revisar los registros:

```bash
docker-compose logs -f rusle-app
```

Causas comunes:

- **Credenciales no montadas**: Asegúrate de que `~/.config/earthengine` existe
- **Puerto en uso**: Cambia el mapeo de puertos en `docker-compose.yml`

### Errores de Autenticación GEE

```bash
# Re-autenticarse en el host
earthengine authenticate --force

# Reiniciar el contenedor
docker-compose restart
```

### Errores de Permisos

Si el contenedor no puede escribir en los directorios de datos:

```bash
# Corregir permisos
chmod -R 777 data/
```

## Actualizar

```bash
# Obtener los últimos cambios
git pull

# Reconstruir y reiniciar
docker-compose up --build -d
```
