# GitHub Actions - Guía Rápida

## ¿Qué es GitHub Actions?

GitHub Actions es una herramienta **integrada en GitHub** que te permite automatizar tareas. No necesitas instalar nada adicional - solo pushear archivos de configuración a tu repositorio.

## Cómo Funciona

1. **Workflows**: Son archivos `.yml` en `.github/workflows/`
2. **Automatización**: GitHub ejecuta estos workflows cuando ocurren eventos (push, release, manual, etc.)
3. **Ejecuta en servidores de GitHub**: No usa tu computadora, se ejecuta en la nube

## Tu Proyecto Actual

Ya tienes **2 workflows**:

### 1. Tests (`.github/workflows/tests.yml`)
- Se ejecuta automáticamente en cada push
- Ejecuta los tests del proyecto
- Te dice si hay errores

### 2. Build Windows (`.github/workflows/build-windows.yml`) - NUEVO
- Se ejecuta **manual** (o en releases/tags)
- Construye el ejecutable de Windows
- Genera un archivo descargable

## Cómo Usar el Workflow de Build Windows

### Paso 1: Hacer Push

Asegúrate de que el workflow esté en tu repositorio:

```bash
git add .github/workflows/build-windows.yml
git commit -m "Add Windows build workflow"
git push
```

### Paso 2: Ir a GitHub

1. Abre tu repositorio en GitHub (en el navegador)
2. Haz clic en la pestaña **"Actions"** (arriba, junto a "Code", "Issues", etc.)

### Paso 3: Ejecutar el Workflow

1. En la pestaña Actions, verás una lista de workflows
2. Busca **"Build Windows Executable"** en la lista de la izquierda
3. Haz clic en **"Build Windows Executable"**
4. Verás un botón azul **"Run workflow"** (arriba a la derecha)
5. Haz clic en **"Run workflow"** → Selecciona la rama (normalmente `main` o `master`)
6. Haz clic de nuevo en **"Run workflow"** (botón verde)

### Paso 4: Esperar

- Verás que aparece un nuevo "run" en la lista
- Haz clic en él para ver el progreso
- Tarda aproximadamente 5-10 minutos
- Verás los logs en tiempo real

### Paso 5: Descargar el Ejecutable

Cuando termine (verás una marca verde ✓):

1. Haz scroll hacia abajo en la página del run
2. Verás una sección **"Artifacts"**
3. Haz clic en **"nubisary-windows"** para descargar
4. Descomprime el archivo ZIP
5. Dentro encontrarás `nubisary.exe`

## Visualización del Proceso

```
GitHub Repositorio
    │
    ├── .github/
    │   └── workflows/
    │       ├── tests.yml          (automático en push)
    │       └── build-windows.yml  (manual o en release)
    │
    └── [Tu código]

Cuando ejecutas el workflow:
    │
    ├── GitHub crea un servidor Windows virtual
    ├── Clona tu código
    ├── Instala Python y dependencias
    ├── Ejecuta PyInstaller
    └── Genera nubisary.exe como artifact descargable
```

## Ventajas de GitHub Actions

✅ **No necesitas Windows**: GitHub ejecuta en Windows por ti  
✅ **Reproducible**: Siempre construye de la misma forma  
✅ **Automatizable**: Puedes configurarlo para ejecutarse en releases  
✅ **Gratis**: Para repositorios públicos, es completamente gratis  
✅ **No usa tu computadora**: Se ejecuta en la nube

## Ejecución Automática (Opcional)

El workflow también se ejecuta automáticamente cuando:
- Creas un **release** en GitHub
- Haces push de un **tag** que empieza con `v` (ej: `v1.0.0`)

Para crear un release:
1. Ve a tu repositorio en GitHub
2. Haz clic en **"Releases"** (lado derecho)
3. Haz clic en **"Create a new release"**
4. Crea el tag (ej: `v1.0.0`)
5. El workflow se ejecutará automáticamente

## Resumen

1. **GitHub Actions está integrado** - no necesitas instalar nada
2. **Workflows = archivos .yml** en `.github/workflows/`
3. **Para construir Windows**: Ve a Actions → Build Windows Executable → Run workflow
4. **Descarga el artifact** cuando termine
5. **Listo**: Tienes `nubisary.exe` sin necesidad de Windows

## Ejemplo de Uso Completo

```bash
# 1. Asegúrate de tener el workflow en tu repo
git status  # Verifica que .github/workflows/build-windows.yml existe

# 2. Si no está commiteado, hazlo:
git add .github/workflows/build-windows.yml
git commit -m "Add Windows build workflow"
git push

# 3. Ve a GitHub → Actions → Build Windows Executable → Run workflow

# 4. Espera 5-10 minutos

# 5. Descarga el artifact y prueba nubisary.exe
```

¡Es así de simple! GitHub Actions hace todo el trabajo pesado por ti.

