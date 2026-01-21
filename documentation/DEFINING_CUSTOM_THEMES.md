# Guía Práctica: Definir Custom Themes

Esta guía te ayudará a crear tus propios themes personalizados para Nubisary, incluyendo colormaps personalizados.

## Estructura del JSON

Crea un archivo JSON con esta estructura:

```json
{
  "custom_colormaps": [
    {
      "name": "nombre_del_colormap",
      "colors": ["#FF0000", "#00FF00", "#0000FF"],
      "description": "Descripción opcional"
    }
  ],
  "theme": {
    "name": "nombre-del-theme",
    "background_color": "#1a1a2e",
    "colormap": "nombre_del_colormap",
    "font_color": null,
    "relative_scaling": 0.6,
    "prefer_horizontal": 0.85,
    "description": "Descripción del theme"
  }
}
```

## Paso a Paso

### 1. Elegir Colores para el Colormap

**Gradientes suaves:** Usa colores que se mezclen bien
- Ejemplo: `["#001F3F", "#003D7A", "#0074D9", "#39CCCC"]` (azul oscuro → claro)

**Paletas discretas:** Usa colores con buen contraste
- Ejemplo: `["#FF0000", "#00FF00", "#0000FF", "#FFFF00"]` (RGB + amarillo)

**Recomendaciones:**
- Mínimo 2 colores, recomendado 4-7 para gradientes suaves
- Usa herramientas online para elegir paletas (Coolors.co, Adobe Color, etc.)
- Prueba que los colores contrasten bien con el background

### 2. Definir el Background Color

Elige un color de fondo que:
- **Contraste** con los colores del colormap
- Fondos oscuros → colormaps claros/vibrantes
- Fondos claros → colormaps oscuros o pasteles

**Formatos válidos:**
- Nombres de color: `"white"`, `"black"`, `"blue"`
- Códigos hex: `"#FFFFFF"`, `"#000000"`, `"#1a1a2e"`

### 3. Decidir: Colormap o Font Color

**Usa Colormap si:**
- Quieres múltiples colores (recomendado para mayor impacto visual)
- Quieres que palabras de diferente frecuencia tengan diferentes colores

**Usa Font Color si:**
- Quieres un color único para todas las palabras
- Prefieres simplicidad

**Nota:** Si defines ambos, el colormap tiene prioridad.

### 4. Ajustar Parámetros Visuales (Opcional)

- **`relative_scaling`** (0.0-1.0, default: 0.5):
  - Valores bajos (0.3): Diferencias de tamaño más dramáticas
  - Valores altos (0.8): Diferencias más sutiles
  
- **`prefer_horizontal`** (0.0-1.0, default: 0.9):
  - 1.0: Todas las palabras horizontales
  - 0.5: Balance entre horizontal y vertical
  - 0.0: Mezcla completa de orientaciones

### 5. Crear el Archivo JSON

Ejemplo completo:

```json
{
  "custom_colormaps": [
    {
      "name": "mi_paleta_personalizada",
      "colors": [
        "#2C3E50",
        "#3498DB",
        "#1ABC9C",
        "#F39C12",
        "#E74C3C"
      ],
      "description": "Mi paleta personalizada con azules, verdes, naranjas y rojos"
    }
  ],
  "theme": {
    "name": "mi-theme-personalizado",
    "background_color": "#ECF0F1",
    "colormap": "mi_paleta_personalizada",
    "font_color": null,
    "relative_scaling": 0.55,
    "prefer_horizontal": 0.9,
    "description": "Theme personalizado con fondo claro y paleta vibrante"
  }
}
```

### 6. Probar el Theme

```bash
python nubisary.py generate -i texto.txt -l spanish --custom-theme mi-theme.json -o prueba.png
```

## Ejemplos Prácticos

### Ejemplo 1: Theme Oscuro con Gradiente Personalizado

```json
{
  "custom_colormaps": [
    {
      "name": "gradiente_violeta",
      "colors": ["#667EEA", "#764BA2", "#F093FB", "#F5576C"]
    }
  ],
  "theme": {
    "name": "dark-violet",
    "background_color": "#1A1A2E",
    "colormap": "gradiente_violeta",
    "relative_scaling": 0.6,
    "description": "Fondo oscuro con gradiente violeta-rosa"
  }
}
```

### Ejemplo 2: Theme Claro con Color Único

```json
{
  "theme": {
    "name": "simple-blue",
    "background_color": "#F5F5F5",
    "colormap": null,
    "font_color": "#0066CC",
    "relative_scaling": 0.5,
    "description": "Fondo claro con texto azul simple"
  }
}
```

### Ejemplo 3: Theme con Colormap de Matplotlib

```json
{
  "theme": {
    "name": "mi-plasma-theme",
    "background_color": "#000000",
    "colormap": "plasma",
    "relative_scaling": 0.5,
    "description": "Fondo negro con colormap plasma de matplotlib"
  }
}
```

## Consejos para Elegir Colores

### Herramientas Útiles

1. **Coolors.co**: Generador de paletas de colores
2. **Adobe Color**: Herramienta de Adobe para crear paletas
3. **Paletton**: Herramienta para crear paletas armónicas
4. **ColorHunt**: Colección de paletas populares

### Combinaciones Recomendadas

**Fondos Oscuros:**
- Colormaps brillantes: `["#FF6B6B", "#FFD93D", "#6BCB77", "#4D96FF"]`
- Colormaps vibrantes: `["#667EEA", "#764BA2", "#F093FB"]`

**Fondos Claros:**
- Colormaps oscuros: `["#2C3E50", "#34495E", "#1A1A2E"]`
- Colormaps pasteles: `["#FFB6C1", "#98D8C8", "#F7DC6F"]`

### Validar Contraste

Asegúrate de que los colores del colormap sean visibles sobre el fondo:
- **Fondo oscuro**: Usa colores claros/vibrantes
- **Fondo claro**: Usa colores oscuros o muy saturados

## Errores Comunes y Soluciones

### Error: "Colormap not registered"

**Problema:** El theme referencia un colormap que no existe.

**Solución:**
- Verifica el nombre del colormap (debe coincidir exactamente)
- Si es un colormap custom, asegúrate de que esté en `custom_colormaps`
- Si es un colormap de matplotlib, verifica que el nombre sea correcto

### Error: "Theme name cannot be empty"

**Problema:** El campo `name` está vacío o no existe.

**Solución:**
- Añade el campo `"name"` con un valor no vacío
- Ejemplo: `"name": "mi-theme"`

### Error: "Invalid JSON"

**Problema:** El JSON tiene errores de sintaxis.

**Solución:**
- Valida el JSON con un validador online (jsonlint.com)
- Verifica comas, comillas, corchetes
- Asegúrate de que todos los strings estén entre comillas dobles

### Error: "relative_scaling out of range"

**Problema:** El valor está fuera del rango 0.0-1.0.

**Solución:**
- Usa un valor entre 0.0 y 1.0
- Si no especificas, el default (0.5) se usará automáticamente

## Flujo de Trabajo Recomendado

1. **Elige tu paleta de colores** (usa herramientas online)
2. **Crea un JSON simple** con solo los campos requeridos
3. **Prueba con un texto pequeño** para verificar que funciona
4. **Ajusta los colores** según el resultado
5. **Añade parámetros opcionales** (relative_scaling, prefer_horizontal) si es necesario
6. **Guarda el JSON** para uso futuro

## Ejemplo Completo de Trabajo

### Paso 1: Elegir Colores

Usa Coolors.co para generar: `#2C3E50`, `#3498DB`, `#1ABC9C`, `#F39C12`, `#E74C3C`

### Paso 2: Crear el JSON

```json
{
  "custom_colormaps": [
    {
      "name": "coolors_palette",
      "colors": ["#2C3E50", "#3498DB", "#1ABC9C", "#F39C12", "#E74C3C"]
    }
  ],
  "theme": {
    "name": "my-coolors-theme",
    "background_color": "#ECF0F1",
    "colormap": "coolors_palette",
    "description": "Theme con paleta de Coolors"
  }
}
```

### Paso 3: Probar

```bash
python nubisary.py generate -i test.txt -l english --custom-theme my-coolors-theme.json -o test.png
```

### Paso 4: Ajustar si es Necesario

Si los colores no se ven bien, ajusta el background o los colores del colormap.

## Referencias

- Ver [CUSTOM_THEMES.md](CUSTOM_THEMES.md) para documentación técnica completa
- Ver [samples/example_theme.json](../../samples/example_theme.json) para un ejemplo completo
- Ver [THEMES.md](THEMES.md) para ver themes built-in como referencia

