# Instalación

Esta guía cubre cómo instalar y configurar el proyecto RUSLE en tu máquina local.

## Requisitos Previos

Antes de comenzar, asegúrate de tener lo siguiente:

- **Python 3.10+** - El proyecto requiere Python 3.10 o superior
- **[uv](https://docs.astral.sh/uv/)** - Instalador rápido de paquetes Python (recomendado)
- **Cuenta de Google Earth Engine** - Requerida para acceso a datos satelitales

## Instalar uv (Recomendado)

[uv](https://docs.astral.sh/uv/) es un instalador rápido de paquetes Python que recomendamos para este proyecto.

=== "macOS/Linux"

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

=== "Windows"

    ```powershell
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

## Clonar el Repositorio

```bash
git clone https://github.com/nriveras/RUSLE.git
cd RUSLE
```

## Instalar Dependencias

=== "Usando uv (Recomendado)"

    ```bash
    # Instalar todas las dependencias (crea .venv automáticamente)
    uv sync

    # Activar el entorno virtual
    source .venv/bin/activate  # Linux/macOS
    .venv\Scripts\activate     # Windows
    ```

=== "Usando pip"

    ```bash
    # Crear entorno virtual
    python -m venv .venv
    source .venv/bin/activate

    # Instalar dependencias
    pip install -e .
    ```

## Verificar la Instalación

Después de la instalación, verifica que todo funcione:

```bash
# Verificar versión de Python
python --version

# Verificar que Earth Engine está instalado
python -c "import ee; print('Earth Engine instalado correctamente')"

# Iniciar la aplicación
python run.py
```

Deberías ver una salida indicando que el servidor está corriendo en `http://localhost:8000`.

## Próximos Pasos

- [Configurar Google Earth Engine](gee-setup.md) - Configurar autenticación GEE
- [Guía de Inicio Rápido](quickstart.md) - Ejecutar tu primer análisis
