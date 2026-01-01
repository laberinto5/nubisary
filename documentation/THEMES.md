# Word Cloud Themes Documentation

This document describes all available themes for the Word Cloud Generator. Themes provide preset color combinations and visual styles that make it easy to create beautiful word clouds without manually configuring colors.

## Using Themes

To use a theme, simply specify it with the `--theme` flag:

```bash
python nubisary.py generate -i text.txt -l english -o output.png --theme vibrant
```

You can also combine themes with individual color settings - individual flags will override theme settings:

```bash
python nubisary.py generate -i text.txt -l english -o output.png --theme vibrant --background "#000000"
```

## Theme Categories

Themes are organized into several categories based on their visual characteristics and use cases.

---

## Classic & Minimal Themes

### `classic`
- **Background**: White
- **Colors**: Black text (single color)
- **Description**: Classic white background with black text. Simple and clean.
- **Best for**: Professional documents, presentations, print materials
- **Example**: `--theme classic`

### `minimal`
- **Background**: White
- **Colors**: Grey text (#666666)
- **Description**: White background with grey text. Clean and professional.
- **Best for**: Subtle, understated designs
- **Example**: `--theme minimal`

### `high-contrast`
- **Background**: White
- **Colors**: Black text
- **Description**: High contrast white/black with dramatic size differences. Accessible and clear.
- **Best for**: Maximum readability, accessibility
- **Example**: `--theme high-contrast`

---

## Dark Themes

### `dark`
- **Background**: Black
- **Colors**: Set3 colormap (bright, distinct colors)
- **Description**: Black background with bright colormap. Modern and eye-catching.
- **Best for**: Modern presentations, dark mode interfaces
- **Example**: `--theme dark`

### `vibrant`
- **Background**: Dark grey (#1a1a1a)
- **Colors**: Viridis colormap
- **Description**: Dark background with vibrant viridis colormap. Modern and colorful.
- **Best for**: Scientific visualizations, modern designs
- **Example**: `--theme vibrant`

### `inferno`
- **Background**: Very dark (#0d0d0d)
- **Colors**: Inferno colormap
- **Description**: Dark background with inferno colormap. Fiery and intense.
- **Best for**: Dramatic, high-impact visualizations
- **Example**: `--theme inferno`

### `magma`
- **Background**: Very dark (#0c0c0c)
- **Colors**: Magma colormap
- **Description**: Very dark background with magma colormap. Volcanic and powerful.
- **Best for**: Bold, striking designs
- **Example**: `--theme magma`

### `hot`
- **Background**: Dark red (#1a0000)
- **Colors**: Hot colormap
- **Description**: Dark red background with hot colormap. Intense and energetic.
- **Best for**: Energetic, passionate content
- **Example**: `--theme hot`

### `jet`
- **Background**: Very dark (#000814)
- **Colors**: Jet colormap
- **Description**: Very dark background with jet colormap. Classic and vibrant.
- **Best for**: Classic scientific style
- **Example**: `--theme jet`

### `turbo`
- **Background**: Dark (#0a0a0a)
- **Colors**: Turbo colormap
- **Description**: Dark background with turbo colormap. Modern and dynamic.
- **Best for**: Modern, dynamic visualizations
- **Example**: `--theme turbo`

### `dark2`
- **Background**: Dark grey (#1a1a1a)
- **Colors**: Dark2 qualitative colormap
- **Description**: Dark background with Dark2 qualitative colormap. Rich and sophisticated.
- **Best for**: Categorical data, sophisticated designs
- **Example**: `--theme dark2`

---

## Seasonal Themes

### `spring`
- **Background**: Light green (#f0f8f0)
- **Colors**: Spring colormap
- **Description**: Light green background with spring colormap. Fresh and vibrant.
- **Best for**: Nature, growth, renewal themes
- **Example**: `--theme spring`

### `summer`
- **Background**: Warm yellow (#fff8e1)
- **Colors**: Summer colormap
- **Description**: Warm yellow background with summer colormap. Bright and cheerful.
- **Best for**: Happy, energetic content
- **Example**: `--theme summer`

### `autumn`
- **Background**: Warm orange (#fff3e0)
- **Colors**: Autumn colormap
- **Description**: Warm orange background with autumn colormap. Cozy and warm.
- **Best for**: Warm, cozy, seasonal content
- **Example**: `--theme autumn`

### `winter`
- **Background**: Cool blue (#e3f2fd)
- **Colors**: Winter colormap
- **Description**: Cool blue background with winter colormap. Calm and serene.
- **Best for**: Calm, peaceful, cool themes
- **Example**: `--theme winter`

---

## Color-Based Sequential Themes

These themes use sequential colormaps that work well for showing magnitude or intensity.

### `blues`
- **Background**: Light blue (#e3f2fd)
- **Colors**: Blues colormap
- **Description**: Light blue background with Blues colormap. Professional and calm.
- **Best for**: Professional, corporate, calm content
- **Example**: `--theme blues`

### `greens`
- **Background**: Light green (#e8f5e9)
- **Colors**: Greens colormap
- **Description**: Light green background with Greens colormap. Natural and fresh.
- **Best for**: Nature, environment, growth themes
- **Example**: `--theme greens`

### `reds`
- **Background**: Light red (#ffebee)
- **Colors**: Reds colormap
- **Description**: Light red background with Reds colormap. Bold and passionate.
- **Best for**: Passionate, urgent, important content
- **Example**: `--theme reds`

### `purples`
- **Background**: Light purple (#f3e5f5)
- **Colors**: Purples colormap
- **Description**: Light purple background with Purples colormap. Elegant and creative.
- **Best for**: Creative, artistic, elegant content
- **Example**: `--theme purples`

### `oranges`
- **Background**: Light orange (#fff3e0)
- **Colors**: Oranges colormap
- **Description**: Light orange background with Oranges colormap. Warm and inviting.
- **Best for**: Warm, friendly, energetic content
- **Example**: `--theme oranges`

---

## Specialized Themes

### `ocean`
- **Background**: Deep blue (#0a1929)
- **Colors**: Coolwarm colormap
- **Description**: Deep blue background with cool colormap. Calm and professional.
- **Best for**: Ocean, water, calm themes
- **Example**: `--theme ocean`

### `sunset`
- **Background**: Warm orange/red (#2d1b0e)
- **Colors**: Plasma colormap
- **Description**: Warm orange/red background with plasma colormap. Warm and energetic.
- **Best for**: Warm, sunset, energetic themes
- **Example**: `--theme sunset`

### `cool`
- **Background**: Light cyan (#e0f2f1)
- **Colors**: Cool colormap
- **Description**: Light cyan background with cool colormap. Refreshing and modern.
- **Best for**: Modern, tech, refreshing themes
- **Example**: `--theme cool`

### `rainbow`
- **Background**: Light grey (#f5f5f5)
- **Colors**: Rainbow colormap
- **Description**: Light background with rainbow colormap. Colorful and playful.
- **Best for**: Playful, colorful, diverse content
- **Example**: `--theme rainbow`

---

## Diverging Themes

These themes use diverging colormaps that work well for showing differences from a center point.

### `spectral`
- **Background**: Light grey (#fafafa)
- **Colors**: Spectral colormap
- **Description**: Light grey background with Spectral colormap. Colorful and balanced.
- **Best for**: Balanced, diverse color representation
- **Example**: `--theme spectral`

### `rdbu`
- **Background**: Light grey (#f5f5f5)
- **Colors**: Red-Blue diverging colormap
- **Description**: Light grey background with Red-Blue diverging colormap. Contrasting and clear.
- **Best for**: Contrasting data, clear distinctions
- **Example**: `--theme rdbu`

---

## Qualitative Themes

These themes use qualitative colormaps that work well for categorical data with distinct categories.

### `set1`
- **Background**: White
- **Colors**: Set1 qualitative colormap
- **Description**: White background with Set1 qualitative colormap. Bold and distinct colors.
- **Best for**: Categorical data, distinct categories
- **Example**: `--theme set1`

### `set2`
- **Background**: Light grey (#fafafa)
- **Colors**: Set2 qualitative colormap
- **Description**: Light grey background with Set2 qualitative colormap. Muted and harmonious.
- **Best for**: Categorical data, harmonious colors
- **Example**: `--theme set2`

### `set3`
- **Note**: Used in `dark` theme
- **Colors**: Set3 qualitative colormap
- **Description**: Bright, distinct colors on dark background
- **Best for**: Categorical data on dark backgrounds

### `pastel`
- **Background**: Light grey (#f5f5f5)
- **Colors**: Pastel1 colormap
- **Description**: Light background with pastel colormap. Soft and gentle.
- **Best for**: Soft, gentle, subtle designs
- **Example**: `--theme pastel`

### `pastel2`
- **Background**: Very light grey (#f9f9f9)
- **Colors**: Pastel2 colormap
- **Description**: Very light background with Pastel2 colormap. Soft and gentle.
- **Best for**: Very soft, subtle designs
- **Example**: `--theme pastel2`

### `tab10`
- **Background**: White
- **Colors**: Tab10 colormap
- **Description**: White background with tab10 colormap. Modern and accessible.
- **Best for**: Modern designs, accessibility
- **Example**: `--theme tab10`

### `tab20`
- **Background**: Light grey (#f5f5f5)
- **Colors**: Tab20 colormap
- **Description**: Light grey background with tab20 colormap. Wide color variety.
- **Best for**: Many categories, wide variety needed
- **Example**: `--theme tab20`

### `accent`
- **Background**: White
- **Colors**: Accent colormap
- **Description**: White background with Accent colormap. Distinctive and vibrant.
- **Best for**: Distinctive, vibrant categorical data
- **Example**: `--theme accent`

---

## Quick Reference

### By Use Case

**Professional/Business:**
- `classic`, `minimal`, `blues`, `ocean`

**Modern/Tech:**
- `vibrant`, `dark`, `turbo`, `cool`, `tab10`

**Creative/Artistic:**
- `purples`, `rainbow`, `spectral`, `accent`

**Nature/Environment:**
- `spring`, `summer`, `greens`, `ocean`

**Warm/Cozy:**
- `autumn`, `sunset`, `oranges`, `hot`

**Cool/Calm:**
- `winter`, `cool`, `blues`, `ocean`

**Bold/Dramatic:**
- `inferno`, `magma`, `hot`, `jet`, `high-contrast`

**Soft/Gentle:**
- `pastel`, `pastel2`, `minimal`, `set2`

**Categorical Data:**
- `set1`, `set2`, `set3`, `tab10`, `tab20`, `accent`, `dark2`

### By Background Color

**White/Light:**
- `classic`, `minimal`, `high-contrast`, `set1`, `tab10`, `accent`, `pastel`, `pastel2`, `blues`, `greens`, `reds`, `purples`, `oranges`, `spectral`, `rdbu`, `rainbow`

**Dark:**
- `dark`, `vibrant`, `inferno`, `magma`, `hot`, `jet`, `turbo`, `dark2`, `ocean`, `sunset`

**Colored:**
- `spring` (green), `summer` (yellow), `autumn` (orange), `winter` (blue), `cool` (cyan)

---

## Technical Details

### Colormap Types

- **Perceptually Uniform**: `viridis`, `plasma`, `inferno`, `magma`, `turbo` - Best for scientific data
- **Sequential**: `Blues`, `Greens`, `Reds`, `Purples`, `Oranges` - Show magnitude/intensity
- **Diverging**: `coolwarm`, `Spectral`, `RdBu` - Show differences from center
- **Qualitative**: `Set1`, `Set2`, `Set3`, `Pastel1`, `Pastel2`, `Dark2`, `tab10`, `tab20`, `Accent` - Distinct categories
- **Special**: `spring`, `summer`, `autumn`, `winter`, `cool`, `hot`, `rainbow`, `jet` - Specialized purposes

### Theme Properties

Each theme includes:
- `background_color`: Background color (hex code or color name)
- `colormap`: Matplotlib colormap name (if using multi-color)
- `font_color`: Single color (if not using colormap)
- `relative_scaling`: Size difference intensity (0.0-1.0)
- `prefer_horizontal`: Orientation preference (0.0-1.0)

### Customization

You can override any theme setting with individual flags:

```bash
# Use vibrant theme but change background
python nubisary.py generate -i text.txt -l english --theme vibrant --background "#000000"

# Use classic theme but add colormap
python nubisary.py generate -i text.txt -l english --theme classic --colormap viridis
```

---

## Examples

```bash
# Professional document
python nubisary.py generate -i report.txt -l english -o report.png --theme classic

# Modern presentation
python nubisary.py generate -i data.txt -l english -o presentation.png --theme vibrant

# Nature-themed content
python nubisary.py generate -i nature.txt -l english -o nature.png --theme greens

# Categorical analysis
python nubisary.py generate -i categories.txt -l english -o categories.png --theme set1

# Warm, cozy content
python nubisary.py generate -i cozy.txt -l english -o cozy.png --theme autumn
```

---

## List All Themes

To see all available themes programmatically:

```python
from src.themes import get_theme_names
themes = get_theme_names()
print(themes)
```

Or check the CLI help:

```bash
python nubisary.py generate --help
```

---

*Last updated: All 34 themes documented*

