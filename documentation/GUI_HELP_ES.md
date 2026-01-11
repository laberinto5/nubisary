# Nubisary - Manual de Usuario

## Bienvenido a Nubisary

Nubisary es un generador de nubes de palabras que crea visualizaciones hermosas a partir de tus documentos de texto. Esta guía te ayudará a comenzar.

## Inicio Rápido

1. **Seleccionar Archivo de Entrada**: Haz clic en "Examinar..." para elegir un archivo de texto, PDF, DOCX o JSON
2. **Elegir Idioma**: Selecciona el idioma de tu texto (por defecto: Español)
3. **Seleccionar Tema**: Elige un tema visual para tu nube de palabras
4. **Generar**: Haz clic en "Generar Nube de Palabras" para crear tu visualización
5. **Previsualizar**: Revisa tu nube de palabras en el área de previsualización
6. **Guardar**: Haz clic en "Guardar como..." cuando estés satisfecho con el resultado

## Archivo de Entrada

### Formatos Soportados
- **Archivos de texto** (`.txt`) - Documentos de texto plano
- **Archivos PDF** (`.pdf`) - Convertidos automáticamente a texto
- **Archivos DOCX** (`.docx`) - Documentos de Microsoft Word (convertidos automáticamente)
- **Archivos JSON** (`.json`) - Datos de frecuencia de palabras

### Selección de Idioma

Elige el idioma de tu texto para habilitar el filtrado correcto de palabras vacías. Los idiomas soportados incluyen:

**Idiomas Europeos**: Inglés, Español, Francés, Italiano, Portugués, Alemán, Holandés, Ruso, Griego, Danés, Noruego, Sueco, Finlandés, Turco

**Otros Idiomas**: Árabe, Chino, Hebreo, Indonesio

La configuración de idioma ayuda a eliminar palabras comunes (como "el", "la", "y" en español) para enfocarse en contenido significativo.

## Opciones de Procesamiento de Texto

### Excluir Palabras/Frases

Elimina palabras o frases específicas de tu nube de palabras:

- **Entrada directa**: Ingresa palabras separadas por comas (ej: "Título, Nombre del Autor")
- **Desde archivo**: Haz clic en "Examinar..." para seleccionar un archivo con una palabra/frase por línea

**Ejemplo de contenido del archivo:**
```
Título del Libro
Nombre del Autor
Nombre de la Colección
```

### Reglas Regex (Avanzado)

Para filtrado avanzado de texto, usa expresiones regulares:

- **Regla única**: Ingresa un patrón o `patrón|reemplazo`
- **Desde archivo**: Haz clic en "Examinar..." para seleccionar un archivo con una regla por línea

**Ejemplos:**
- Eliminar encabezados de página: `^Página \d+`
- Reemplazar formato: `Página (\d+)|P.\\1`

### Opciones de Procesamiento

- **Incluir palabras vacías**: Mantener palabras comunes (generalmente desmarcado)
- **Sensible a mayúsculas**: Distinguir entre mayúsculas y minúsculas
- **Colocaciones**: Agrupar pares de palabras comunes
- **Normalizar plurales**: Tratar formas singulares y plurales como la misma palabra
- **Incluir números**: Mantener valores numéricos en la nube de palabras
- **Longitud mínima de palabra**: Mínimo de caracteres por palabra (por defecto: 0)
- **Máximo de palabras**: Número máximo de palabras a mostrar (por defecto: 200)

## Personalización Visual

### Selección de Tema

Elige entre más de 38 temas predefinidos para combinaciones de colores instantáneas:

- **Clásico y Minimalista**: classic, minimal, high-contrast
- **Temas Oscuros**: dark, vibrant, inferno, magma, hot, jet, turbo
- **Estacionales**: spring, summer, autumn, winter
- **Basados en Color**: blues, greens, reds, purples, oranges
- ¡Y muchos más!

### Creador de Temas Personalizados

Crea tu propio tema con colores personalizados:

1. Marca "Crear Tema Personalizado"
2. Selecciona color de fondo
3. Elige 5 colores para el mapa de colores
4. Opcionalmente guarda tu tema como JSON para reutilizar
5. Carga temas guardados previamente con "Cargar Tema desde JSON..."

### Tamaño del Lienzo

Ajusta las dimensiones de tu nube de palabras:
- **Ancho**: Por defecto 800 píxeles
- **Alto**: Por defecto 600 píxeles

### Orientación de Palabras

- **Escalado Relativo**: Controla la intensidad de diferencia de tamaño (0.0-1.0)
  - Valores más bajos = diferencias de tamaño más dramáticas
  - Valores más altos = diferencias más sutiles
- **Preferir Horizontal**: Preferencia de orientación de palabras (0.0-1.0)
  - 1.0 = todas horizontales
  - 0.0 = orientaciones mixtas
  - 0.5 = equilibrado

## Opciones Avanzadas

### Imágenes de Máscara

Usa formas personalizadas para tu nube de palabras:

1. Selecciona una **Máscara predefinida** del menú desplegable (34 formas disponibles)
2. O elige **Personalizada...** para seleccionar tu propio archivo de imagen
3. Áreas oscuras = colocación de palabras
4. Áreas claras/transparentes = sin palabras

**Opciones de Contorno** (al usar una máscara):
- **Ancho de Contorno**: Grosor del borde (0.0 = sin borde)
- **Color de Contorno**: Color del borde (código hexadecimal o nombre de color)

### Selección de Fuente

Elige una fuente para tu nube de palabras:

- **Por defecto**: Usa DroidSansMono (incluida)
- **Fuentes predefinidas**: 20 fuentes hermosas disponibles:
  - Sans Serif: Comfortaa, Inter Tight, Urbanist, Outfit, Maven Pro
  - Serif: Courier Prime, Marcellus, Special Elite
  - Monospace: Kode Mono, Orbitron
  - Manuscritas: Cabin Sketch, Caveat, Pacifico
  - Decorativas: Barrio, Chelsea Market, Caesar Dressing, Pirata One, Ribeye Marrow, Saira Stencil One, Text Me One
- **Personalizada...**: Selecciona un archivo de fuente de tu sistema

### Exportar Estadísticas

Exporta datos de frecuencia de palabras:

- Marca "Exportar estadísticas" para generar archivos JSON y CSV
- Opcionalmente limita a las N palabras principales (ej: top 20)
- Los archivos se guardan junto a tu imagen de nube de palabras

## Consejos y Mejores Prácticas

1. **Comienza Simple**: Empieza con configuraciones por defecto y un tema predefinido
2. **Ajusta Gradualmente**: Haz pequeños cambios y regenera para ver los efectos
3. **Usa Excluir Palabras**: Elimina títulos, nombres de autores y otro texto no deseado
4. **Prueba Diferentes Temas**: Experimenta con varios esquemas de color
5. **Usa Máscaras**: Crea nubes de palabras en formas personalizadas para impacto visual
6. **El Idioma Importa**: Siempre selecciona el idioma correcto para mejor filtrado de palabras vacías

## Solución de Problemas

### La Nube de Palabras No se Genera
- Asegúrate de que el archivo de entrada esté seleccionado y sea válido
- Verifica que el idioma esté configurado correctamente
- Confirma que el formato del archivo sea compatible

### Las Palabras Aparecen como Rectángulos
- Esto generalmente indica un problema de codificación de fuente
- Prueba con una fuente predefinida diferente
- Asegúrate de que las fuentes personalizadas soporten los caracteres de tu idioma

### La Previsualización No se Actualiza
- Haz clic en "Generar Nube de Palabras" nuevamente
- Revisa si hay mensajes de error en el área de estado

### El Archivo No se Guarda
- Asegúrate de haber generado una nube de palabras primero
- Usa el botón "Guardar como..." para elegir la ubicación de guardado
- Verifica los permisos de archivo en el directorio de destino

## Atajos de Teclado

- **F1**: Abrir este manual de ayuda (próximamente)
- **Ctrl+O**: Abrir archivo de entrada (próximamente)
- **Ctrl+S**: Guardar nube de palabras (próximamente)

## Obtener Más Ayuda

Para documentación detallada, visita el repositorio del proyecto o consulta la documentación CLI para funciones avanzadas.

---

**Versión**: 1.0  
**Última Actualización**: Enero 2025

