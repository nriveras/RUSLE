# Configuración de Google Earth Engine

Google Earth Engine (GEE) proporciona acceso a imágenes satelitales y conjuntos de datos geoespaciales necesarios para los cálculos RUSLE. Esta guía cubre la autenticación y configuración del proyecto.

## Requisitos Previos

1. Una cuenta de Google
2. Acceso a Google Earth Engine (regístrate en [earthengine.google.com](https://earthengine.google.com/signup/))
3. Un Proyecto de Google Cloud con la API de Earth Engine habilitada

## Crear un Proyecto GEE

### Paso 1: Crear un Proyecto de Google Cloud

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Haz clic en **Crear Proyecto**
3. Ingresa un nombre de proyecto (ej. `rusle-analysis`)
4. Haz clic en **Crear**

### Paso 2: Habilitar la API de Earth Engine

1. En la Cloud Console, ve a **APIs y Servicios** > **Biblioteca**
2. Busca "Earth Engine API"
3. Haz clic en **Habilitar**

### Paso 3: Registrarse en Earth Engine

1. Ve a [earthengine.google.com/signup](https://earthengine.google.com/signup/)
2. Inicia sesión con tu cuenta de Google
3. Completa el formulario de registro
4. Espera la aprobación (normalmente instantánea para uso personal)

## Autenticación

### Desarrollo Local

Para desarrollo local, autentícate usando la línea de comandos:

```bash
# Autenticarse con Earth Engine
earthengine authenticate

# Establecer tu proyecto predeterminado
earthengine set_project tu-id-de-proyecto
```

Esto abre una ventana del navegador para autenticación de Google y almacena las credenciales en `~/.config/earthengine/`.

### Configuración del Entorno

Crea un archivo `.env` en la raíz del proyecto:

```bash
# .env
RUSLE_GEE_PROJECT=tu-id-de-proyecto
RUSLE_DEBUG=true
```

!!! tip "Formato del ID de Proyecto"
    El ID del proyecto generalmente tiene el formato `ee-usuario` o `nombre-de-tu-proyecto`. Puedes encontrarlo en la Google Cloud Console.

### Despliegue con Docker

Cuando se ejecuta en Docker, las credenciales se montan desde tu máquina local:

```yaml
# docker-compose.yml
volumes:
  - ~/.config/earthengine:/home/appuser/.config/earthengine:ro
```

!!! warning "Autenticarse Primero"
    Debes ejecutar `earthengine authenticate` en la máquina host antes de iniciar el contenedor Docker.

## Verificar la Conexión

Prueba tu conexión a GEE:

```python
import ee

# Inicializar con tu proyecto
ee.Authenticate()
ee.Initialize(project='tu-id-de-proyecto')

# Probar la conexión
print(ee.Number(1).getInfo())  # Debe imprimir: 1
```

## Solución de Problemas

### "Project not registered"

Si ves este error:

```
ee.EEException: Project is not registered
```

**Solución**: Registra tu proyecto en [code.earthengine.google.com](https://code.earthengine.google.com/) y acepta los términos de servicio.

### "Invalid credentials"

Si la autenticación falla:

```bash
# Forzar re-autenticación
earthengine authenticate --force
```

### Límites de Velocidad

GEE tiene cuotas de uso. Para análisis grandes:

- Reduce el área de interés
- Aumenta la escala de exportación (menor resolución)
- Usa procesamiento por lotes para múltiples regiones

## Próximos Pasos

- [Guía de Inicio Rápido](quickstart.md) - Ejecutar tu primer análisis
- [Referencia de Configuración](../reference/configuration.md) - Todas las opciones de configuración
