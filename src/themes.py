"""Theme definitions for WordCloud visual presets.

This module provides preset themes for word cloud generation.
Each theme combines background colors, colormaps, and visual settings
for beautiful, ready-to-use word clouds.

For complete theme documentation, see THEMES.md in the project root.
"""

from dataclasses import dataclass
from typing import Optional, Dict
from src.config import WordCloudConfig

# Import colormap registration for custom color palettes
# Custom colormaps (user-defined color palettes) are registered before themes are defined
# All themes defined in this file are built-in themes available to users
from src.custom_colormaps import register_custom_colormap

# Available themes registry
THEMES: Dict[str, 'Theme'] = {}


@dataclass
class Theme:
    """Theme configuration for WordCloud generation."""
    
    name: str
    background_color: str
    colormap: Optional[str] = None  # None = use font_color
    font_color: Optional[str] = None  # None = use colormap
    relative_scaling: float = 0.5
    prefer_horizontal: float = 0.9
    description: str = ""
    
    def apply_to_config(self, config: WordCloudConfig) -> WordCloudConfig:
        """
        Apply theme settings to a WordCloudConfig.
        
        Only overrides settings that are None/default in the config.
        This allows users to override theme settings with individual flags.
        
        Args:
            config: WordCloudConfig to apply theme to
            
        Returns:
            New WordCloudConfig with theme applied
        """
        # Create a copy of the config
        new_config = WordCloudConfig(
            canvas_width=config.canvas_width,
            canvas_height=config.canvas_height,
            max_words=config.max_words,
            min_word_length=config.min_word_length,
            lemmatize=config.lemmatize,
            include_numbers=config.include_numbers,
            background_color=config.background_color or self.background_color,
            font_color=config.font_color if config.font_color is not None else self.font_color,
            colormap=config.colormap if config.colormap is not None else self.colormap,
            relative_scaling=config.relative_scaling if config.relative_scaling != 0.5 else self.relative_scaling,
            prefer_horizontal=config.prefer_horizontal if config.prefer_horizontal != 0.9 else self.prefer_horizontal,
            mask=config.mask,
            contour_width=config.contour_width,
            contour_color=config.contour_color,
            font_path=config.font_path,
            language=config.language,
            include_stopwords=config.include_stopwords,
            case_sensitive=config.case_sensitive,
            ngram=config.ngram
        )
        return new_config


def register_theme(theme: Theme) -> None:
    """Register a theme in the global themes registry."""
    THEMES[theme.name.lower()] = theme


def get_theme(name: str) -> Optional[Theme]:
    """
    Get a theme by name (case-insensitive).
    
    Args:
        name: Theme name
        
    Returns:
        Theme object or None if not found
    """
    return THEMES.get(name.lower())


def list_themes() -> Dict[str, Theme]:
    """Get all registered themes."""
    return THEMES.copy()


def get_theme_names() -> list:
    """Get list of all registered theme names."""
    return sorted(THEMES.keys())


# Define preset themes
_playroom = Theme(
    name="playroom",
    background_color="#ffffff",
    font_color=None,
    colormap="crayons",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="White background with cheerful colors. Bright and cheerful."
)
register_theme(_playroom)

_jungle = Theme(
    name="jungle",
    background_color="#76E864",
    font_color=None,
    colormap="greens_dark",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Green background with green colors."
)
register_theme(_jungle)

_garden = Theme(
    name="garden",
    background_color="#B8F194",
    font_color=None,
    colormap="garden_with_flowers",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="White background with green colors."
)
register_theme(_garden)

_brazil = Theme(
    name="brazil",
    background_color="#FFE539",
    font_color=None,
    colormap="blue_green_vibrant",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Brazilian colors palette."
)
register_theme(_brazil)

_woods = Theme(
    name="woods",
    background_color="#218D4C",
    font_color=None,
    colormap="greens_light",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Light green on dark green. Mysterious woods."
)
register_theme(_woods)

_fluorescent = Theme(
    name="fluorescent",
    background_color="#2A2A2A",
    font_color=None,
    colormap="greens_light",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Light green shining in the dark."
)
register_theme(_fluorescent)

_mint = Theme(
    name="mint",
    background_color="#5FB89D",
    font_color=None,
    colormap="greens_light",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Fresh and minty theme."
)
register_theme(_mint)

_stars = Theme(
    name="stars",
    background_color="#1F1F40",
    font_color=None,
    colormap="blues_light",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Like stars in the sky on a dark night."
)
register_theme(_stars)

_lake = Theme(
    name="lake",
    background_color="#1B5274",
    font_color=None,
    colormap="blues_bright",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Blue like a dark lake."
)
register_theme(_lake)

_river = Theme(
    name="river",
    background_color="#7299BD",
    font_color=None,
    colormap="blues_light",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Like a shinny river."
)
register_theme(_river)

_solarized = Theme(
    name="solarized",
    background_color="#FFC98B",
    font_color=None,
    colormap="blues_dark",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Blue letters on vibrant ocre background."
)
register_theme(_solarized)


_office = Theme(
    name="office",
    background_color="#FFFFFF",
    font_color=None,
    colormap="grey_blue_dark",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Blue and grey letters on white. Elegant and simple."
)
register_theme(_office)

_pinky = Theme(
    name="pinky",
    background_color="#000000",
    font_color=None,
    colormap="pinkies",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Pink and purple letters on black. Vibrant and fun."
)
register_theme(_pinky)

_neon = Theme(
    name="neon",
    background_color="#000000",
    font_color=None,
    colormap="neon",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Neon colors palette on black. Vibrant and fun."
)
register_theme(_neon)

_markers = Theme(
    name="markers",
    background_color="#1A284E",
    font_color=None,
    colormap="neon",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Neon colors palette on black. Vibrant and fun."
)
register_theme(_markers)

_golden = Theme(
    name="golden",
    background_color="#FDD67B",
    font_color=None,
    colormap="goldens_dark",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Golden colors palette on black. Vibrant and fun."
)
register_theme(_golden)

_pharaon = Theme(
    name="pharaon",
    background_color="#063866",
    font_color=None,
    colormap="goldens_dark",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Golden letters on dark blue."
)
register_theme(_pharaon)

_cadiz = Theme(
    name="cadiz",
    background_color="#0C88C2",
    font_color=None,
    colormap="goldens_light",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Like Cadiz beach, maybe."
)
register_theme(_cadiz)

_clouds = Theme(
    name="clouds",
    background_color="#0C88C2",
    font_color=None,
    colormap="blues_light",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Blue letters on white clouds."
)
register_theme(_clouds)

_strawberry = Theme(
    name="strawberry",
    background_color="#DE7998",
    font_color=None,
    colormap="reds_dark",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Red letters on strawberry background."
)
register_theme(_strawberry)

_piruleta = Theme(
    name="piruleta",
    background_color="#6D0E2A",
    font_color=None,
    colormap="reds_light",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Vibrant red theme, like a piruleta."
)
register_theme(_piruleta)

_blood = Theme(
    name="blood",
    background_color="#1D0109",
    font_color=None,
    colormap="reds_dark",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Dark red letters on dark red background."
)
register_theme(_blood)

_high_contrast = Theme(
    name="high_contrast",
    background_color="#FFFFFF",
    font_color=None,
    colormap="greys_dark",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Dark letters on white background, high contrast."
)
register_theme(_high_contrast)

_soft = Theme(
    name="soft",
    background_color="#FFFFFF",
    font_color=None,
    colormap="greys_light",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Light letters on white background, soft."
)
register_theme(_soft)

_grey = Theme(
    name="grey",
    background_color="#3F3E40",
    font_color=None,
    colormap="greys_light",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Light letters on grey background."
)
register_theme(_grey)

_elegance = Theme(
    name="elegance",
    background_color="#355690",
    font_color=None,
    colormap="greys_light",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Light grey letters on blue. Elegant and quiet."
)
register_theme(_elegance)

_gum = Theme(
    name="gum",
    background_color="#FF86BF",
    font_color=None,
    colormap="pink_dark",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Dark red letters on pink background. Gum theme."
)
register_theme(_gum)

_sakura = Theme(
    name="sakura",
    background_color="#FFE8F3",
    font_color=None,
    colormap="sakura_palette",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Like sakura leaves flying in the wind."
)
register_theme(_sakura)

_gossip = Theme(
    name="gossip",
    background_color="#32272E",
    font_color=None,
    colormap="sakura_palette",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Pink and grey letters on dark grey background."
)
register_theme(_gossip)

_halloween = Theme(
    name="halloween",
    background_color="#000000",
    font_color=None,
    colormap="pumpkins",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Pumpkin-like colors palette, vibrant version."
)
register_theme(_halloween)

_carrots = Theme(
    name="carrots",
    background_color="#E8AF79",
    font_color=None,
    colormap="pumpkins",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Pumpkin-like colors palette, vibrant version."
)
register_theme(_carrots)

_joy = Theme(
    name="joy",
    background_color="#3B536A",
    font_color=None,
    colormap="pastels",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Pastels colors palette on blue background."
)
register_theme(_joy)

_blackboard = Theme(
    name="blackboard",
    background_color="#323232",
    font_color=None,
    colormap="pastels",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Like a colorful blackboard."
)
register_theme(_blackboard)

_sauvage = Theme(
    name="sauvage",
    background_color="#000000",
    font_color=None,
    colormap="rainbow",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Rainbow colors palette on black background."
)
register_theme(_sauvage)

_loretta  = Theme(
    name="loretta",
    background_color="#200D5F",
    font_color=None,
    colormap="rainbow",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Rainbow colors palette on vibrant dark blue background."
)
register_theme(_loretta)

_old = Theme(
    name="old",
    background_color="#585142",
    font_color=None,
    colormap="greys_light",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Like an old document."
)
register_theme(_old)

_sober = Theme(
    name="sober",
    background_color="#E0DCD8",
    font_color=None,
    colormap="sober_colors",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Sober colors palette, warm and elegant."
)
register_theme(_sober)

_homely = Theme(
    name="homely",
    background_color="#E3D1BB",
    font_color=None,
    colormap="sober_colors",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Sober colors palette, warm and elegant."
)
register_theme(_homely)

_spring = Theme(
    name="spring",
    background_color="#1BA891",
    font_color=None,
    colormap="pink_light",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Spring colors palette, bright and cheerful."
)
register_theme(_spring)

_summer = Theme(
    name="summer",
    background_color="#004697",
    font_color=None,
    colormap="colorful_palette",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Summer colors palette, warm and vibrant."
)
register_theme(_summer)

_autumn = Theme(
    name="autumn",
    background_color="#5F2E0F",
    font_color=None,
    colormap="goldens_dark",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Autumn colors palette, cozy and warm."
)
register_theme(_autumn)

_winter = Theme(
    name="winter",
    background_color="#6689AF",
    font_color=None,
    colormap="blues_light",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Winter colors palette, cold and serene."
)
register_theme(_winter)

_night = Theme(
    name="night",
    background_color="#1A0000",
    font_color=None,
    colormap="blue_green_dark",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Night colors palette, dark and mysterious."
)
register_theme(_night)

_day = Theme(
    name="day",
    background_color="#EEE8CB",
    font_color=None,
    colormap="blue_green_dark",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Day colors palette, bright and cheerful."
)
register_theme(_day)

_radical = Theme(
    name="radical",
    background_color="#003DE3",
    font_color=None,
    colormap="neon",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Radical colors palette, intense and energetic."
)
register_theme(_radical)

_bombons = Theme(
    name="bombons",
    background_color="#311405",
    font_color=None,
    colormap="crayons",
    relative_scaling=0.6,
    prefer_horizontal=0.8,
    description="Vibrant colors on chocolate. Like a chocolate box."
)
register_theme(_bombons)

# ============================================================================
# Custom Colormaps for themes
# ============================================================================
# This section defines themes that use custom color palettes (not matplotlib colormaps).
# Custom colormaps must be registered before themes that use them.
# All themes defined in this file are built-in themes available to users via --theme.

register_custom_colormap(
    name="greens_dark",
    colors=["#11843d", "#0b5437", "#10804a", "#268966", "#11664d"],
    description="Green colors palette, dark version"
)

register_custom_colormap(
    name="greens_light",
    colors=["#3dff74", "#2effa4", "#14ffbd", "#6dffb6", "#89fcca"],
    description="Green colors palette, light version"
)

register_custom_colormap(
    name="blues_dark",
    colors=["#004c72", "#085189", "#1c3e78", "#022b4b", "#012f63"],
    description="Blue colors palette, dark version"
)

register_custom_colormap(
    name="blues_bright",
    colors=["#1e99d7", "#62d5f8", "#35ccf1", "#2cbfec", "#2caeff"],
    description="Blue colors palette, bright version"
)

register_custom_colormap(
    name="blues_light",
    colors=["#a2d7f1", "#b3d9f1", "#bcd2f8", "#d8eaf8", "#f3fbff"],
    description="Blue colors palette, light version"
)


register_custom_colormap(
    name="reds_dark",
    colors=["#870505","#710600","#991c1e","#680018","#7a041d"],
    description="Red colors palette, dark version"
)

register_custom_colormap(
    name="reds_light",
    colors=["#ff3737","#ff655d","#ff334b","#ff1745","#f63b3b"],
    description="Red colors palette, light version"
)

register_custom_colormap(
    name="goldens_dark",
    colors=["#bd7800","#FFB300","#DBA800","#C48D00","#D5961F"],
    description="Golden colors palette, dark version"
)

register_custom_colormap(
    name="goldens_light",
    colors=["#ffdf7f","#ffd65d","#ffcd4f","#ffc13b","#ffce65"],
    description="Golden colors palette, light version"
)

register_custom_colormap(
    name="greys_dark",
    colors=["#131313","#212121","#2f2f2f","#393939","#444444"],
    description="Grey colors palette, dark version"
)

register_custom_colormap(
    name="greys_light",
    colors=["#898989","#9a9a9a","#acacac","#bfbfbf","#dcdcdc"],
    description="Grey colors palette, light version"
)

register_custom_colormap(
    name="neon",
    colors=["#ff00e1","#00FF44","#fff700","#00fbff","#b303ff"],
    description="Neon colors palette"
)

register_custom_colormap(
    name="pastels",
    colors=["#f7c7ff", "#c9ffb0", "#fffca4", "#aefeff", "#ffc0d3"],
    description="Pastels colors palette"
)

register_custom_colormap(
    name="grey_blue_dark",
    colors=["#1d4d95","#183872","#314a82","#2f2f2f","#494949"],
    description="Grey and blue colors palette, dark version"
)

register_custom_colormap(
    name="crayons",
    colors=["#941c1c", "#c1751e", "#345aac", "#2eab6f", "#8540af"],
    description="Almost rainbow colors palette, like crayons"
)

register_custom_colormap(
    name="pinkies",
    colors=["#c606d0", "#dd00ff", "#de07c9", "#ff0195", "#ff00bf"],
    description="Pink and purple colors palette, vibrant"
)

register_custom_colormap(
    name="pink_dark",
    colors=["#FC4C89", "#EA3B90", "#E33988", "#EA4FAF", "#FC478F"],
    description="Pink colors palette, dark version"
)

register_custom_colormap(
    name="pink_light",
    colors=["#f6d6f3", "#fccfea", "#d0f2ff", "#f6dfff", "#f2caff"],
    description="Pink colors palette, light version"
)

register_custom_colormap(
    name="sakura_palette",
    colors=["#f55bb2", "#ef4f9d", "#d95995", "#BB9CAF", "#877279"],
    description="Pink colors palette, dark version"
)

register_custom_colormap(
    name="pumpkins",
    colors=["#dc5400", "#e07109", "#c14d00", "#e0650e", "#c75a15"],
    description="Pumpkin-like colors palette, vibrant version"
)

register_custom_colormap(
    name="blue_ocre_grey",
    colors=["#707071", "#5874b1", "#5890b0", "#b08458", "#b06f58"],
    description="Blue, ocre and grey colors palette. Elegant"
)

register_custom_colormap(
    name="blue_green_dark",
    colors=["#5276a7", "#345293", "#5890b0", "#58b09e", "#469285"],
    description="Blue and green colors palette, dark version"
)

register_custom_colormap(
    name="blue_green_vibrant",
    colors=["#38d508", "#50dc0f", "#04bd4e", "#2076cb", "#174ca8"],
    description="Blue and green colors palette, vibrant version"
)

register_custom_colormap(
    name="blue_green_light",
    colors=["#76a7c7", "#93b4c7", "#b0b4b0", "#b0e4d9", "#85c7b0"],
    description="Blue and green colors palette, light version"
)

register_custom_colormap(
    name="garden_with_flowers",
    colors=["#cba50c", "#19a850", "#1f907d", "#20a77c", "#c73d79"],
    description="Garden with flowers colors palette"
)

register_custom_colormap(
    name="sober_colors",
    colors=["#1f3263", "#a59475", "#685a4a", "#421331", "#11425c"],
    description="Sober colors palette, warm and elegant."
)

register_custom_colormap(
    name="colorful_palette",
    colors=["#dc9881", "#e0d081", "#1b80a8", "#d9bf6a", "#589bba"],
    description="Colorful colors palette, vibrant version"
)