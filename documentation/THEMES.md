# Themes & Custom Themes

This guide covers built-in themes and custom themes (JSON).

## Built-in Themes (Quick Use)

```bash
python nubisary.py generate -i text.txt -l english --theme vibrant
```

Override any theme setting with individual flags:

```bash
python nubisary.py generate -i text.txt -l english --theme vibrant --background "#000000"
```

### List Available Themes

```bash
python nubisary.py list-themes
```

Or in code:

```python
from src.themes import get_theme_names
print(get_theme_names())
```

## Custom Themes (JSON)

Use a JSON file to define a custom theme (and optional custom colormaps).

### JSON Structure

```json
{
  "custom_colormaps": [
    {
      "name": "my_colormap",
      "colors": ["#FF0000", "#00FF00", "#0000FF"],
      "description": "Optional"
    }
  ],
  "theme": {
    "name": "my-theme",
    "background_color": "#1a1a2e",
    "colormap": "my_colormap",
    "font_color": null,
    "relative_scaling": 0.6,
    "prefer_horizontal": 0.85,
    "description": "Optional"
  }
}
```

Notes:
- Use **colormap** for multi-color clouds or **font_color** for a single color (colormap wins if both set).
- Colors accept names (`"white"`) or hex (`"#FFFFFF"`).
- `relative_scaling` and `prefer_horizontal` are optional (0.0–1.0).

### Minimal Example (Single Color)

```json
{
  "theme": {
    "name": "simple-blue",
    "background_color": "#F5F5F5",
    "colormap": null,
    "font_color": "#0066CC"
  }
}
```

### Example (Custom Colormap)

```json
{
  "custom_colormaps": [
    {
      "name": "violet_gradient",
      "colors": ["#667EEA", "#764BA2", "#F093FB", "#F5576C"]
    }
  ],
  "theme": {
    "name": "dark-violet",
    "background_color": "#1A1A2E",
    "colormap": "violet_gradient"
  }
}
```

### Use Custom Theme

```bash
python nubisary.py generate -i text.txt -l english --custom-theme my-theme.json -o output.png
```

## Common Errors

- **"Colormap not registered"**: colormap name does not match.
- **"Theme name cannot be empty"**: missing `theme.name`.
- **"Invalid JSON"**: validate the file with a JSON validator.
- **"relative_scaling out of range"**: must be 0.0–1.0.

