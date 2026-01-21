# Custom Themes Documentation

This document explains how to create and use custom themes for Nubisary, including custom colormaps.

## Overview

Custom themes allow you to:
- Define your own color combinations (background, font colors, or colormaps)
- Create custom colormaps with your own color palettes
- Save and reuse themes for consistent word cloud styling
- Share themes with others via JSON files

## JSON Format

Custom themes are defined in JSON files with the following structure:

```json
{
  "custom_colormaps": [
    {
      "name": "my_custom_colormap",
      "colors": ["#FF0000", "#00FF00", "#0000FF"],
      "description": "Custom three-color palette"
    }
  ],
  "theme": {
    "name": "my-custom-theme",
    "background_color": "#1a1a2e",
    "colormap": "my_custom_colormap",
    "font_color": null,
    "relative_scaling": 0.6,
    "prefer_horizontal": 0.85,
    "description": "My custom theme description"
  }
}
```

### Theme Fields

**Required Fields:**
- `name`: Theme name (string, must be unique)
- `background_color`: Background color (color name like `"white"` or hex code like `"#FF0000"`)

**Optional Fields:**
- `colormap`: Colormap name (string). Can be:
  - Built-in matplotlib colormap: `"viridis"`, `"plasma"`, `"coolwarm"`, etc.
  - Custom colormap defined in `custom_colormaps` section
  - `null` if using `font_color` instead
- `font_color`: Single font color (string or `null`). Ignored if `colormap` is set
- `relative_scaling`: Size difference intensity (0.0-1.0, default: 0.5)
- `prefer_horizontal`: Word orientation preference (0.0-1.0, default: 0.9)
- `description`: Theme description (string, optional)

**Note:** You must specify either `colormap` OR `font_color`, not both (if both are set, `colormap` takes precedence).

### Custom Colormaps Section

The `custom_colormaps` section is optional. Use it to define custom color palettes that can be referenced in the theme.

**Fields:**
- `name`: Colormap name (string, must be unique)
- `colors`: Array of color strings (hex codes or color names)
- `description`: Optional description

**Requirements:**
- Must have at least 2 colors
- Colors are applied in order (first color for low frequency words, last for high frequency)
- Color format: Hex codes (`"#FF0000"`) or color names (`"red"`)

## Examples

### Example 1: Theme with Custom Colormap

```json
{
  "custom_colormaps": [
    {
      "name": "sunset_palette",
      "colors": ["#FF6B6B", "#FF8E53", "#FFA07A", "#FFD700", "#FF6347"],
      "description": "Warm sunset gradient"
    }
  ],
  "theme": {
    "name": "sunset-theme",
    "background_color": "#2D1810",
    "colormap": "sunset_palette",
    "font_color": null,
    "relative_scaling": 0.6,
    "prefer_horizontal": 0.85,
    "description": "Dark warm background with custom sunset gradient"
  }
}
```

**Usage:**
```bash
python nubisary.py generate -i text.txt -l english --custom-theme sunset-theme.json
```

### Example 2: Theme with Single Font Color

```json
{
  "theme": {
    "name": "blue-on-white",
    "background_color": "white",
    "colormap": null,
    "font_color": "#0066CC",
    "relative_scaling": 0.5,
    "prefer_horizontal": 0.9,
    "description": "White background with blue text"
  }
}
```

**Usage:**
```bash
python nubisary.py generate -i text.txt -l english --custom-theme blue-on-white.json
```

### Example 3: Theme with Built-in Matplotlib Colormap

```json
{
  "theme": {
    "name": "my-plasma-theme",
    "background_color": "#000000",
    "colormap": "plasma",
    "font_color": null,
    "relative_scaling": 0.5,
    "prefer_horizontal": 0.9,
    "description": "Black background with plasma colormap"
  }
}
```

**Usage:**
```bash
python nubisary.py generate -i text.txt -l english --custom-theme my-plasma-theme.json
```

### Example 4: Multiple Custom Colormaps

```json
{
  "custom_colormaps": [
    {
      "name": "ocean_gradient",
      "colors": ["#001F3F", "#003D7A", "#0074D9", "#39CCCC", "#7FDBFF"],
      "description": "Ocean depth gradient"
    },
    {
      "name": "forest_gradient",
      "colors": ["#1A4D2E", "#2D5F3F", "#4A7C59", "#7FB069", "#B5E48C"],
      "description": "Forest green gradient"
    }
  ],
  "theme": {
    "name": "ocean-theme",
    "background_color": "#001122",
    "colormap": "ocean_gradient",
    "relative_scaling": 0.55,
    "prefer_horizontal": 0.9,
    "description": "Deep ocean theme with custom gradient"
  }
}
```

## Creating Custom Colormaps

### Color Selection Tips

1. **Gradients**: For smooth gradients, choose colors that blend well together
   - Example: `["#000428", "#004e92", "#009ffd"]` (dark to light blue)

2. **Discrete Palettes**: For distinct colors, choose colors with good contrast
   - Example: `["#FF0000", "#00FF00", "#0000FF", "#FFFF00"]` (RGB + Yellow)

3. **Theme Matching**: Match colormap colors to background color
   - Dark backgrounds: Use bright/vibrant colors
   - Light backgrounds: Use darker or muted colors

### Color Formats

**Hex Codes (Recommended):**
```json
"colors": ["#FF0000", "#00FF00", "#0000FF"]
```

**Color Names:**
```json
"colors": ["red", "green", "blue", "yellow"]
```

**Mixed:**
```json
"colors": ["#FF0000", "green", "#0000FF"]
```

### Testing Custom Colormaps

To test if your custom colormap works:

1. Create a simple test theme JSON
2. Use it with a small text file
3. Check the generated word cloud colors

Example test command:
```bash
python nubisary.py generate -i test.txt -l english --custom-theme test-theme.json -o test_output.png
```

## CLI Usage

### Load Custom Theme

```bash
python nubisary.py generate -i text.txt -l english --custom-theme my_theme.json
```

### Custom Theme vs Built-in Theme

If both `--theme` and `--custom-theme` are specified, the custom theme takes precedence:

```bash
# Custom theme will be used, not 'vibrant'
python nubisary.py generate -i text.txt -l english --theme vibrant --custom-theme my_theme.json
```

### Override Theme Settings

You can override individual theme settings with CLI flags:

```bash
# Use custom theme but override background color
python nubisary.py generate -i text.txt -l english --custom-theme my_theme.json -B "#000000"
```

## Built-in Custom Colormaps

Nubisary includes some custom colormaps (user-defined color palettes) that are registered as built-in:

- `terracotta`: Terracotta color palette with warm earth tones
- `cucu2`: Gray scale gradient from black to light gray

These custom colormaps are used in built-in themes like `sweety`, `cheshire`, `cherry`, and `amanda` (which use `terracotta`).

Note: These are custom color palettes defined in `themes.py`, not matplotlib colormaps. All themes in `themes.py` are built-in themes available via `--theme`.

## Available Built-in Matplotlib Colormaps

You can use any matplotlib colormap in your custom themes. Popular options:

**Sequential (Gradients):**
- `viridis`, `plasma`, `inferno`, `magma`, `cividis`
- `Blues`, `Greens`, `Reds`, `Purples`, `Oranges`

**Diverging:**
- `coolwarm`, `Spectral`, `RdBu`

**Qualitative (Discrete):**
- `Set1`, `Set2`, `Set3`, `Pastel1`, `Pastel2`, `Dark2`
- `tab10`, `tab20`, `Accent`

**Cyclic:**
- `hsv`, `twilight`

See matplotlib documentation for complete list: https://matplotlib.org/stable/tutorials/colors/colormaps.html

## Best Practices

1. **Name Your Themes Uniquely**: Avoid conflicts with built-in themes
2. **Test Your Colormaps**: Ensure colors work well together and are readable
3. **Match Background**: Choose colormap colors that contrast well with background
4. **Document Your Themes**: Add descriptions to help remember theme purposes
5. **Share Your Themes**: JSON format makes it easy to share themes with others

## Troubleshooting

### "Colormap not found" Error

**Problem:** Theme references a colormap that doesn't exist.

**Solution:**
- Check colormap name spelling
- Ensure custom colormap is defined in `custom_colormaps` section
- Use a built-in matplotlib colormap name (see list above)

### "Theme name cannot be empty" Error

**Problem:** Theme name field is missing or empty.

**Solution:**
- Add `"name"` field to theme definition
- Ensure name is not an empty string

### "Invalid relative_scaling" Error

**Problem:** `relative_scaling` value is out of range.

**Solution:**
- Use a value between 0.0 and 1.0
- Default is 0.5 if not specified

### Custom Theme Not Loading

**Problem:** Custom theme file not found or JSON is invalid.

**Solution:**
- Verify file path is correct
- Validate JSON syntax (use a JSON validator)
- Check file permissions
- Ensure all required fields are present

## Advanced: Creating Gradient Colormaps

For smooth gradients, include more colors:

```json
{
  "custom_colormaps": [
    {
      "name": "smooth_gradient",
      "colors": [
        "#000428", "#004e92", "#009ffd", "#2a2a72", 
        "#006994", "#00B4D8", "#90E0EF"
      ],
      "description": "Smooth blue gradient with 7 steps"
    }
  ]
}
```

More colors = smoother gradient transitions.

## Example Files

See `samples/example_theme.json` for a complete example theme file.

