"""Main GUI window for Nubisary."""

# Add parent directory to path if running directly (for development/testing)
# This must be done BEFORE importing src modules
import sys
from pathlib import Path
if __name__ == '__main__':
    parent_dir = Path(__file__).parent.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))

import customtkinter as ctk
import tkinter as tk  # Still needed for filedialog, messagebox, Menu, Canvas, Spinbox
from tkinter import filedialog, messagebox, scrolledtext, ttk  # ttk needed for Spinbox
from PIL import Image, ImageTk
import threading
import json
import locale
import os

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")  # User prefers dark theme
ctk.set_default_color_theme("blue")  # Default theme

try:
    from tkcolorpicker import askcolor as color_picker
except ImportError:
    # Fallback to native tkinter colorchooser if tkcolorpicker2 is not available
    from tkinter import colorchooser
    color_picker = colorchooser.askcolor

from src.wordcloud_service import process_text_to_frequencies, WordCloudServiceError
from src.wordcloud_generator import generate_word_cloud_from_frequencies
from src.config import WordCloudConfig, LANGUAGES_FOR_NLTK
from src.themes import get_theme, get_theme_names, Theme
from src.file_handlers import is_json_file, is_convertible_document, FileHandlerError
from src.custom_themes import load_custom_theme_from_json, save_theme_to_json, CustomThemeError
from src.custom_colormaps import register_custom_colormap, is_colormap_registered, CustomColormapError
from src.resource_loader import list_mask_files, get_mask_path, get_resource_path
from src.font_loader import list_font_files, get_font_path


class WordCloudGUI:
    """Main GUI window for Nubisary word cloud generator."""
    
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.setup_styles()  # Setup visual styles first
        self.setup_variables()
        self.setup_menu()
        self.create_widgets()
        
        # Store preview image reference
        self.preview_image = None
        self.generating = False
        self.generated_wordcloud = None  # Store generated WordCloud object
        self.temp_output_file = None  # Store temporary file path for preview
    
    def setup_window(self):
        """Configure main window properties."""
        self.root.title("Nubisary - Word Cloud Generator")
        
        # Set minimum window size to ensure all content is visible
        self.root.minsize(1200, 700)
        
        # Wider window for two-column layout (controls left, preview right)
        # Increased width to accommodate larger preview (650px minimum for preview column)
        initial_width = 1500
        initial_height = 850
        
        # Center window on screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (initial_width // 2)
        y = (screen_height // 2) - (initial_height // 2)
        
        # Set geometry with position
        self.root.geometry(f'{initial_width}x{initial_height}+{x}+{y}')
        
        # Ensure window is properly sized (update after widgets are created)
        self.root.after(100, self._ensure_window_size)
        
        # Clean up temporary files when window is closed
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Set favicon/icon
        try:
            icon_path = get_resource_path('favicon.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            # Try PNG for Linux
            try:
                icon_path = get_resource_path('favicon.png')
                if os.path.exists(icon_path):
                    icon = tk.PhotoImage(file=icon_path)
                    self.root.iconphoto(False, icon)
            except:
                pass  # Fallback: use default icon
    
    def setup_styles(self):
        """
        Configure visual styles for the GUI.
        CustomTkinter handles styling automatically, but we define custom colors for primary buttons.
        """
        # CustomTkinter uses global theme settings (configured in imports)
        # Store custom button colors for later use
        self.primary_green = '#5a8a5a'  # Desaturated green
        self.primary_green_hover = '#4a7a4a'
        self.secondary_blue = '#5a7a9a'  # Desaturated blue
        self.secondary_blue_hover = '#4a6a8a'
    
    def setup_menu(self):
        """Configure menu bar with Help menu."""
        menubar = tk.Menu(self.root)
        self.root.configure(menu=menubar)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="User Manual (English)", command=lambda: self.show_help('en'))
        help_menu.add_command(label="Manual de Usuario (Español)", command=lambda: self.show_help('es'))
        help_menu.add_separator()
        help_menu.add_command(label="About Nubisary...", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        # Bind F1 key to show help
        self.root.bind('<F1>', lambda e: self.show_help(self._detect_help_language()))
    
    def _detect_help_language(self) -> str:
        """Detect preferred help language based on system locale or GUI language setting."""
        try:
            # Try to get system locale
            system_lang, _ = locale.getdefaultlocale()
            if system_lang:
                lang_code = system_lang.split('_')[0].lower()
                if lang_code == 'es':
                    return 'es'
        except:
            pass
        
        # Fallback: use GUI language setting if Spanish
        if self.language.get().lower() == 'spanish':
            return 'es'
        
        # Default to English
        return 'en'
    
    def show_help(self, language: str = 'en'):
        """Open help window with user manual in specified language."""
        # Determine help file based on language
        if language == 'es':
            help_file = 'documentation/GUI_HELP_ES.md'
            window_title = "Manual de Usuario - Nubisary"
        else:
            help_file = 'documentation/GUI_HELP_EN.md'
            window_title = "Nubisary - User Manual"
        
        # Get resource path (works in dev and PyInstaller)
        help_path = get_resource_path(help_file)
        
        # Create help window
        help_window = tk.Toplevel(self.root)
        help_window.title(window_title)
        help_window.geometry("900x700")
        
        # Center window on screen
        help_window.update_idletasks()
        width = help_window.winfo_width()
        height = help_window.winfo_height()
        x = (help_window.winfo_screenwidth() // 2) - (width // 2)
        y = (help_window.winfo_screenheight() // 2) - (height // 2)
        help_window.geometry(f'{width}x{height}+{x}+{y}')
        
        # Main frame with padding
        main_frame = ctk.CTkFrame(help_window)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Text widget with scrollbar
        text_frame = ctk.CTkFrame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ctk.CTkScrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        help_text = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            font=("TkDefaultFont", 10),
            padx=10,
            pady=10
        )
        help_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.configure(command=help_text.yview)
        
        # Load help content
        try:
            if os.path.exists(help_path):
                with open(help_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                # Simple markdown to plain text conversion (remove # headers, keep structure)
                # For now, just display as-is (markdown is readable enough)
                help_text.insert('1.0', content)
            else:
                error_msg = f"Help file not found: {help_path}\n\n"
                if language == 'es':
                    error_msg += "Por favor, consulta la documentación en el directorio 'documentation/'."
                else:
                    error_msg += "Please consult the documentation in the 'documentation/' directory."
                help_text.insert('1.0', error_msg)
        except Exception as e:
            error_msg = f"Error loading help file: {str(e)}\n\n"
            if language == 'es':
                error_msg += "Por favor, consulta la documentación en el directorio 'documentation/'."
            else:
                error_msg += "Please consult the documentation in the 'documentation/' directory."
            help_text.insert('1.0', error_msg)
        
        help_text.configure(state=tk.DISABLED)  # Make read-only
        
        # Close button
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        if language == 'es':
            close_text = "Cerrar"
        else:
            close_text = "Close"
        
        ctk.CTkButton(button_frame, text=close_text, command=help_window.destroy).pack()
    
    def show_about(self):
        """Show about dialog."""
        about_text = (
            "Nubisary - Word Cloud Generator\n\n"
            "Version: 1.0\n"
            "Created with Python and Tkinter\n\n"
            "A powerful tool for creating beautiful word clouds\n"
            "from text, PDF, DOCX, and JSON files.\n\n"
            "For more information, visit the project repository."
        )
        messagebox.showinfo("About Nubisary", about_text)
    
    def setup_variables(self):
        """Initialize Tkinter variables."""
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.language = tk.StringVar(value="spanish")
        self.theme = tk.StringVar(value="spring")
        
        # Processing options
        self.include_stopwords = tk.BooleanVar(value=False)
        self.case_sensitive = tk.BooleanVar(value=False)
        self.collocations = tk.BooleanVar(value=False)
        self.normalize_plurals = tk.BooleanVar(value=False)
        self.include_numbers = tk.BooleanVar(value=False)
        self.min_word_length = tk.IntVar(value=0)
        self.max_words = tk.IntVar(value=200)
        
        # Visual options
        self.canvas_width = tk.IntVar(value=800)
        self.canvas_height = tk.IntVar(value=600)
        self.relative_scaling = tk.DoubleVar(value=0.5)
        self.prefer_horizontal = tk.DoubleVar(value=0.9)
        
        # Custom theme creator options
        self.use_custom_theme_creator = tk.BooleanVar(value=False)
        self.custom_theme_background = tk.StringVar(value="#FFFFFF")
        self.custom_theme_colormap_colors = [
            tk.StringVar(value="#FF0000"),  # Color 1
            tk.StringVar(value="#00FF00"),  # Color 2
            tk.StringVar(value="#0000FF"),  # Color 3
            tk.StringVar(value="#FFFF00"),  # Color 4
            tk.StringVar(value="#FF00FF")   # Color 5
        ]
        self.custom_theme_name = tk.StringVar(value="my-custom-theme")
        
        # Advanced options (no longer includes custom colors - use Custom Theme Creator instead)
        self.mask_file = tk.StringVar(value="")
        self.preset_mask = tk.StringVar(value="")  # Selected preset mask filename
        self.contour_width = tk.DoubleVar(value=0.0)
        self.contour_color = tk.StringVar(value="")
        self.preset_font = tk.StringVar(value="Default")
        self.font_path = tk.StringVar(value="")
        
        # Export options
        self.export_stats = tk.BooleanVar(value=False)
        self.stats_top_n = tk.StringVar(value="")
        
        # Status
        self.status_text = tk.StringVar(value="Ready")
    
    def create_widgets(self):
        """Create and layout all GUI widgets in a two-column layout."""
        # Main container
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left column: Controls (scrollable)
        left_column = ctk.CTkFrame(main_frame)
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Create scrollable canvas for left column
        canvas = tk.Canvas(left_column, bg="#212325")  # Dark theme background
        scrollbar = ctk.CTkScrollbar(left_column, orientation="vertical", command=canvas.yview)
        scrollable_frame = ctk.CTkFrame(canvas)
        
        def update_scroll_region(event=None):
            """Update scroll region when content changes."""
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Make sure canvas width matches scrollable_frame width
            canvas_width = event.width if event else canvas.winfo_width()
            if canvas_width > 1:
                canvas.itemconfig(canvas.find_all()[0], width=canvas_width)
        
        scrollable_frame.bind("<Configure>", update_scroll_region)
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        def on_canvas_configure(event):
            """Adjust scrollable_frame width to match canvas width."""
            canvas_width = event.width
            canvas.itemconfig(canvas_window, width=canvas_width)
        
        canvas.bind("<Configure>", on_canvas_configure)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas (only when hovering over left column)
        def _on_mousewheel(event):
            # Only scroll if mouse is over the canvas or scrollable_frame
            widget = event.widget
            if widget == canvas or str(widget).startswith(str(canvas)):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Right column: Preview (fixed, no scroll) - Larger preview area
        right_column = ctk.CTkFrame(main_frame)
        # Set minimum width for preview column (larger preview area)
        # This ensures the preview column is at least 650px wide
        right_column.configure(width=650)
        right_column.pack(side="right", fill="both", expand=True, padx=(5, 0))
        # Store reference for later use
        self.right_column = right_column
        
        # 1. Input Section
        input_frame = ctk.CTkFrame(scrollable_frame)
        input_frame.pack(fill=tk.X, padx=5, pady=(5, 0))
        ctk.CTkLabel(input_frame, text="Input File", font=("TkDefaultFont", 10, "bold")).pack(padx=10, pady=(10, 5))
        
        # File selection row
        file_select_frame = ctk.CTkFrame(input_frame)
        file_select_frame.pack(fill=tk.X, pady=(0, 10))
        ctk.CTkButton(file_select_frame, text="Select Input File", command=self.on_select_file).pack(side=tk.LEFT, padx=5)
        # Reduce width to prevent hiding language selector
        file_label = ctk.CTkLabel(file_select_frame, text="", width=40)
        file_label.pack(side=tk.LEFT, padx=5)
        self.file_label = file_label  # Store reference to update text
        self.file_type_label = ctk.CTkLabel(file_select_frame, text="", text_color="gray")
        self.file_type_label.pack(side=tk.LEFT, padx=5)
        
        # Language selector row (always visible, below file selection with clear separation)
        lang_frame = ctk.CTkFrame(input_frame)
        lang_frame.pack(fill=tk.X, pady=(5, 0))
        ctk.CTkLabel(lang_frame, text="Language:", font=("TkDefaultFont", 9, "bold")).pack(side=tk.LEFT, padx=5)
        self.language_combo = ctk.CTkOptionMenu(lang_frame, variable=self.language, values=LANGUAGES_FOR_NLTK, width=140)
        self.language_combo.pack(side=tk.LEFT, padx=5)
        
        # 2. Processing Options Section
        proc_frame = ctk.CTkFrame(scrollable_frame)
        proc_frame.pack(fill=tk.X, padx=5, pady=(5, 0))
        ctk.CTkLabel(proc_frame, text="Processing Options", font=("TkDefaultFont", 10, "bold")).pack(padx=10, pady=(10, 5))
        
        # Checkboxes row 1
        cb_frame1 = ctk.CTkFrame(proc_frame)
        cb_frame1.pack(fill=tk.X, pady=2)
        ctk.CTkCheckBox(cb_frame1, text="Include stopwords", variable=self.include_stopwords).pack(side=tk.LEFT, padx=5)
        ctk.CTkCheckBox(cb_frame1, text="Case sensitive", variable=self.case_sensitive).pack(side=tk.LEFT, padx=5)
        ctk.CTkCheckBox(cb_frame1, text="Collocations", variable=self.collocations).pack(side=tk.LEFT, padx=5)
        
        # Checkboxes row 2
        cb_frame2 = ctk.CTkFrame(proc_frame)
        cb_frame2.pack(fill=tk.X, pady=2)
        ctk.CTkCheckBox(cb_frame2, text="Normalize plurals", variable=self.normalize_plurals).pack(side=tk.LEFT, padx=5)
        ctk.CTkCheckBox(cb_frame2, text="Include numbers", variable=self.include_numbers).pack(side=tk.LEFT, padx=5)
        
        # Numeric inputs
        num_frame = ctk.CTkFrame(proc_frame)
        num_frame.pack(fill=tk.X, pady=5)
        ctk.CTkLabel(num_frame, text="Min word length:").pack(side=tk.LEFT, padx=5)
        ttk.Spinbox(num_frame, from_=0, to=20, textvariable=self.min_word_length, width=10).pack(side=tk.LEFT, padx=5)
        ctk.CTkLabel(num_frame, text="Max words:").pack(side=tk.LEFT, padx=5)
        ttk.Spinbox(num_frame, from_=1, to=1000, textvariable=self.max_words, width=10).pack(side=tk.LEFT, padx=5)
        
        # 3. Visual Customization Section
        vis_frame = ctk.CTkFrame(scrollable_frame)
        vis_frame.pack(fill=tk.X, padx=5, pady=(5, 0))
        ctk.CTkLabel(vis_frame, text="Visual Customization", font=("TkDefaultFont", 10, "bold")).pack(padx=10, pady=(10, 5))
        vis_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Theme selector
        theme_frame = ctk.CTkFrame(vis_frame)
        theme_frame.pack(fill=tk.X, pady=5)
        ctk.CTkLabel(theme_frame, text="Theme:").pack(side=tk.LEFT, padx=5)
        theme_names = get_theme_names()
        self.theme_combo = ctk.CTkOptionMenu(theme_frame, variable=self.theme, values=theme_names, width=140)
        self.theme_combo.pack(side=tk.LEFT, padx=5)
        
        # Canvas size
        size_frame = ctk.CTkFrame(vis_frame)
        size_frame.pack(fill=tk.X, pady=5)
        ctk.CTkLabel(size_frame, text="Canvas size:").pack(side=tk.LEFT, padx=5)
        ttk.Spinbox(size_frame, from_=100, to=4000, textvariable=self.canvas_width, width=10).pack(side=tk.LEFT, padx=5)
        ctk.CTkLabel(size_frame, text="x").pack(side=tk.LEFT)
        ttk.Spinbox(size_frame, from_=100, to=4000, textvariable=self.canvas_height, width=10).pack(side=tk.LEFT, padx=5)
        
        # Sliders
        scale_frame = ctk.CTkFrame(vis_frame)
        scale_frame.pack(fill=tk.X, pady=5)
        ctk.CTkLabel(scale_frame, text="Relative scaling:").pack(side=tk.LEFT, padx=5)
        scale_slider = ctk.CTkSlider(scale_frame, from_=0.0, to=1.0, variable=self.relative_scaling, width=200)
        scale_slider.pack(side=tk.LEFT, padx=5)
        scale_label = ctk.CTkLabel(scale_frame, text="0.50", width=5)
        scale_label.pack(side=tk.LEFT, padx=5)
        self.relative_scaling.trace_add("write", lambda *args: scale_label.configure(text=f"{self.relative_scaling.get():.2f}"))
        
        horiz_frame = ctk.CTkFrame(vis_frame)
        horiz_frame.pack(fill=tk.X, pady=5)
        ctk.CTkLabel(horiz_frame, text="Prefer horizontal:").pack(side=tk.LEFT, padx=5)
        horiz_slider = ctk.CTkSlider(horiz_frame, from_=0.0, to=1.0, variable=self.prefer_horizontal, width=200)
        horiz_slider.pack(side=tk.LEFT, padx=5)
        horiz_label = ctk.CTkLabel(horiz_frame, text="0.90", width=5)
        horiz_label.pack(side=tk.LEFT, padx=5)
        self.prefer_horizontal.trace_add("write", lambda *args: horiz_label.configure(text=f"{self.prefer_horizontal.get():.2f}"))
        
        # Custom Theme Creator Section (expandable)
        self.custom_theme_checkbox = ctk.CTkCheckBox(
            vis_frame, 
            text="Create Custom Theme", 
            variable=self.use_custom_theme_creator,
            command=self._toggle_custom_theme_panel
        )
        self.custom_theme_checkbox.pack(fill=tk.X, pady=5)
        
        # Custom theme creator panel (initially hidden)
        self.custom_theme_panel = ctk.CTkFrame(vis_frame)
        ctk.CTkLabel(self.custom_theme_panel, text="Custom Theme Creator", font=("TkDefaultFont", 10, "bold")).pack(padx=10, pady=(10, 5))
        self._create_custom_theme_panel()
        # Panel is created but not packed initially (hidden by default)
        # _toggle_custom_theme_panel will show/hide it based on checkbox state
        
        # 4. Advanced Options (Collapsible)
        self.advanced_frame = ctk.CTkFrame(scrollable_frame)
        self.advanced_frame.pack(fill=tk.X, padx=5, pady=(5, 0))
        ctk.CTkLabel(self.advanced_frame, text="Advanced Options", font=("TkDefaultFont", 10, "bold")).pack(padx=10, pady=(10, 5))
        
        # Note: Custom colors are now handled by Custom Theme Creator in Visual Customization section
        
        # Mask selection (preset masks + custom file)
        mask_label_frame = ctk.CTkFrame(self.advanced_frame)
        mask_label_frame.pack(fill=tk.X, pady=5)
        ctk.CTkLabel(mask_label_frame, text="Mask:", font=("TkDefaultFont", 9, "bold")).pack(side=tk.LEFT, padx=5)
        
        # Preset masks dropdown
        preset_mask_frame = ctk.CTkFrame(self.advanced_frame)
        preset_mask_frame.pack(fill=tk.X, pady=2)
        ctk.CTkLabel(preset_mask_frame, text="Preset mask:").pack(side=tk.LEFT, padx=5)
        
        # Get available preset masks (without .png extension for display)
        preset_masks = list_mask_files(without_extension=True)
        preset_mask_values = ["None"] + preset_masks + ["Custom..."]
        
        self.preset_mask_combo = ctk.CTkOptionMenu(
            preset_mask_frame, 
            variable=self.preset_mask, 
            values=preset_mask_values, 
            
            width=140)
        self.preset_mask_combo.pack(side=tk.LEFT, padx=5)
        self.preset_mask_combo.set("None")
        self.preset_mask_combo.configure(command=self._on_preset_mask_selected)
        
        # Custom mask file selection
        mask_custom_frame = ctk.CTkFrame(self.advanced_frame)
        mask_custom_frame.pack(fill=tk.X, pady=2)
        ctk.CTkButton(mask_custom_frame, text="Select Custom Mask Image", command=self.on_select_mask).pack(side=tk.LEFT, padx=5)
        mask_file_label = ctk.CTkLabel(mask_custom_frame, text="", width=40, text_color="gray")
        mask_file_label.pack(side=tk.LEFT, padx=5)
        self.mask_file_label = mask_file_label  # Store reference
        
        # Contour options (if mask selected)
        contour_frame = ctk.CTkFrame(self.advanced_frame)
        contour_frame.pack(fill=tk.X, pady=5)
        ctk.CTkLabel(contour_frame, text="Contour width:").pack(side=tk.LEFT, padx=5)
        ttk.Spinbox(contour_frame, from_=0.0, to=10.0, textvariable=self.contour_width, width=10, increment=0.5).pack(side=tk.LEFT, padx=5)
        ctk.CTkLabel(contour_frame, text="Contour color:").pack(side=tk.LEFT, padx=5)
        ctk.CTkEntry(contour_frame, textvariable=self.contour_color, width=15).pack(side=tk.LEFT, padx=5)
        
        # Font selection (preset fonts + custom file)
        font_label_frame = ctk.CTkFrame(self.advanced_frame)
        font_label_frame.pack(fill=tk.X, pady=5)
        ctk.CTkLabel(font_label_frame, text="Font:", font=("TkDefaultFont", 9, "bold")).pack(side=tk.LEFT, padx=5)
        
        # Preset fonts dropdown
        preset_font_frame = ctk.CTkFrame(self.advanced_frame)
        preset_font_frame.pack(fill=tk.X, pady=2)
        ctk.CTkLabel(preset_font_frame, text="Preset font:").pack(side=tk.LEFT, padx=5)
        
        # Get available preset fonts (with friendly display names)
        preset_fonts = list_font_files(without_extension=True, with_display_names=True)
        preset_font_values = ["Default"] + preset_fonts + ["Custom..."]
        
        self.preset_font_combo = ctk.CTkOptionMenu(
            preset_font_frame, 
            variable=self.preset_font, 
            values=preset_font_values, 
            
            width=140)
        self.preset_font_combo.pack(side=tk.LEFT, padx=5)
        self.preset_font_combo.set("Default")
        self.preset_font_combo.configure(command=self._on_preset_font_selected)
        
        # Custom font file selection
        font_custom_frame = ctk.CTkFrame(self.advanced_frame)
        font_custom_frame.pack(fill=tk.X, pady=2)
        ctk.CTkButton(font_custom_frame, text="Select Custom Font", command=self.on_select_font).pack(side=tk.LEFT, padx=5)
        font_path_label = ctk.CTkLabel(font_custom_frame, text="", width=40, text_color="gray")
        font_path_label.pack(side=tk.LEFT, padx=5)
        self.font_path_label = font_path_label  # Store reference
        
        # Export statistics
        export_frame = ctk.CTkFrame(self.advanced_frame)
        export_frame.pack(fill=tk.X, pady=5)
        ctk.CTkCheckBox(export_frame, text="Export statistics (JSON/CSV)", variable=self.export_stats).pack(side=tk.LEFT, padx=5)
        ctk.CTkLabel(export_frame, text="Top N words:").pack(side=tk.LEFT, padx=5)
        ctk.CTkEntry(export_frame, textvariable=self.stats_top_n, width=10).pack(side=tk.LEFT, padx=5)
        
        # Status bar (at bottom of left column)
        status_frame = ctk.CTkFrame(scrollable_frame)
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        ctk.CTkLabel(status_frame, text="Status:").pack(side=tk.LEFT, padx=5)
        status_label = ctk.CTkLabel(status_frame, text="Ready", text_color="blue")
        status_label.pack(side=tk.LEFT, padx=5)
        self.status_label = status_label  # Store reference
        
        # Right column: Preview Section (always visible, no scroll)
        preview_frame = ctk.CTkFrame(right_column)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        ctk.CTkLabel(preview_frame, text="Preview", font=("TkDefaultFont", 10, "bold")).pack(padx=10, pady=(10, 5))
        
        # Action Buttons moved to right column (preview area) for better visibility
        action_frame = ctk.CTkFrame(preview_frame)
        action_frame.pack(fill=tk.X, pady=(0, 10))  # At top of preview area
        
        self.generate_button = ctk.CTkButton(action_frame, text="Generate Word Cloud", command=self.on_generate, fg_color=self.primary_green, hover_color=self.primary_green_hover)
        self.generate_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.save_button = ctk.CTkButton(action_frame, text="Save As...", command=self.on_select_output, fg_color=self.secondary_blue, hover_color=self.secondary_blue_hover)
        self.save_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.output_label = ctk.CTkLabel(preview_frame, text="", text_color="gray")
        self.output_label.pack(fill=tk.X, pady=5)
        
        # Preview image area
        preview_container = ctk.CTkFrame(preview_frame)
        preview_container.pack(fill=tk.BOTH, expand=True)
        
        self.preview_label = ctk.CTkLabel(preview_container, text="No preview available")
        self.preview_label.pack(fill=tk.BOTH, expand=True)
    
    def _create_custom_theme_panel(self):
        """Create the custom theme creator panel with color selectors."""
        # Theme name entry
        name_frame = ctk.CTkFrame(self.custom_theme_panel)
        name_frame.pack(fill=tk.X, pady=5)
        ctk.CTkLabel(name_frame, text="Theme name:").pack(side=tk.LEFT, padx=5)
        ctk.CTkEntry(name_frame, textvariable=self.custom_theme_name, width=140).pack(side=tk.LEFT, padx=5)
        
        # Background color selector
        bg_frame = ctk.CTkFrame(self.custom_theme_panel)
        bg_frame.pack(fill=tk.X, pady=5)
        ctk.CTkLabel(bg_frame, text="Background Color:").pack(side=tk.LEFT, padx=5)
        
        # Color preview button and hex entry
        self.bg_color_button = tk.Button(
            bg_frame, 
            text="  ", 
            width=3, 
            bg=self.custom_theme_background.get(),
            command=lambda: self._open_color_picker(self.custom_theme_background, "Background")
        )
        self.bg_color_button.pack(side=tk.LEFT, padx=5)
        bg_entry = ctk.CTkEntry(bg_frame, textvariable=self.custom_theme_background, width=10)
        bg_entry.pack(side=tk.LEFT, padx=5)
        self.custom_theme_background.trace_add("write", lambda *args: self._update_color_button(self.bg_color_button, self.custom_theme_background.get()))
        
        # Colormap colors (5 colors)
        colormap_label = ctk.CTkLabel(self.custom_theme_panel, text="Colormap Colors (5 colors):", font=("TkDefaultFont", 9, "bold"))
        colormap_label.pack(pady=(10, 5), padx=5)
        
        self.colormap_buttons = []
        for i, color_var in enumerate(self.custom_theme_colormap_colors, 1):
            color_row = ctk.CTkFrame(self.custom_theme_panel)
            color_row.pack(fill=tk.X, pady=2, padx=5)
            ctk.CTkLabel(color_row, text=f"Color {i}:").pack(side=tk.LEFT, padx=5)
            
            color_btn = tk.Button(
                color_row,
                text="  ",
                width=3,
                bg=color_var.get(),
                command=lambda var=color_var, idx=i: self._open_color_picker(var, f"Colormap Color {idx}")
            )
            color_btn.pack(side=tk.LEFT, padx=5)
            self.colormap_buttons.append(color_btn)
            
            color_entry = ctk.CTkEntry(color_row, textvariable=color_var, width=10)
            color_entry.pack(side=tk.LEFT, padx=5)
            
            # Update button color when entry changes
            color_var.trace_add("write", lambda *args, btn=color_btn, var=color_var: self._update_color_button(btn, var.get()))
        
        # Action buttons (Save/Load)
        action_frame = ctk.CTkFrame(self.custom_theme_panel)
        action_frame.pack(fill=tk.X, pady=(10, 5))
        ctk.CTkButton(action_frame, text="Save Theme as JSON...", command=self._save_custom_theme).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(action_frame, text="Load Theme from JSON...", command=self._load_custom_theme).pack(side=tk.LEFT, padx=5)
    
    def _toggle_custom_theme_panel(self):
        """Show or hide the custom theme creator panel based on checkbox state."""
        if self.use_custom_theme_creator.get():
            self.custom_theme_panel.pack(fill=tk.X, padx=5, pady=5)
            # Disable theme selector when using custom theme creator
            self.theme_combo.configure(state="disabled")
        else:
            self.custom_theme_panel.pack_forget()
            # Re-enable theme selector
            self.theme_combo.configure(state="normal")
    
    def _open_color_picker(self, color_var: tk.StringVar, color_name: str):
        """Open color picker dialog and update color variable using tkcolorpicker2."""
        current_color = color_var.get() if color_var.get() else "#FFFFFF"
        # Use tkcolorpicker2 which provides HSV/HSL interface (more user-friendly)
        # Returns ((r, g, b), '#hex') or (None, None) if cancelled
        try:
            color = color_picker(
                color=current_color,
                parent=self.root,
                title=f"Select {color_name}",
                alpha=False  # Don't use alpha channel for word clouds
            )
            if color and color[1]:  # If user didn't cancel (returns hex string)
                color_var.set(color[1])
        except Exception as e:
            # Fallback to native colorchooser if tkcolorpicker2 fails
            import warnings
            warnings.warn(f"tkcolorpicker2 failed, using fallback: {e}")
            from tkinter import colorchooser
            color = colorchooser.askcolor(
                initialcolor=current_color,
                title=f"Select {color_name}"
            )
            if color and color[1]:
                color_var.set(color[1])
    
    def _update_color_button(self, button: tk.Button, color_hex: str):
        """Update button background color based on hex value."""
        try:
            button.configure(bg=color_hex)
        except tk.TclError:
            # Invalid color, keep current
            pass
    
    def _save_custom_theme(self):
        """Save custom theme to JSON file."""
        try:
            # Validate theme name
            theme_name = self.custom_theme_name.get().strip()
            if not theme_name:
                messagebox.showerror("Error", "Theme name cannot be empty.")
                return
            
            # Validate background color
            bg_color = self.custom_theme_background.get().strip()
            if not bg_color:
                messagebox.showerror("Error", "Background color cannot be empty.")
                return
            
            # Collect colormap colors
            colormap_colors = [color_var.get().strip() for color_var in self.custom_theme_colormap_colors]
            # Remove empty colors
            colormap_colors = [c for c in colormap_colors if c]
            
            if len(colormap_colors) < 2:
                messagebox.showerror("Error", "At least 2 colormap colors are required.")
                return
            
            # Generate colormap name from theme name
            colormap_name = f"{theme_name.lower().replace(' ', '_')}_colormap"
            
            # Create Theme object
            theme = Theme(
                name=theme_name,
                background_color=bg_color,
                colormap=colormap_name,  # Use custom colormap name
                font_color=None,
                relative_scaling=self.relative_scaling.get(),
                prefer_horizontal=self.prefer_horizontal.get(),
                description=f"Custom theme created in GUI: {theme_name}"
            )
            
            # Create colormap config dict
            custom_colormap = {
                "name": colormap_name,
                "colors": colormap_colors,
                "description": f"Custom colormap for theme {theme_name}"
            }
            
            # Ask user for save location
            filename = filedialog.asksaveasfilename(
                title="Save Custom Theme",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialfile=f"{theme_name.lower().replace(' ', '_')}_theme.json"
            )
            
            if filename:
                # Save theme to JSON
                saved_path = save_theme_to_json(theme, custom_colormap, filename)
                messagebox.showinfo("Success", f"Theme saved successfully to:\n{saved_path}")
                
        except (CustomThemeError, FileHandlerError) as e:
            messagebox.showerror("Error", f"Failed to save theme: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")
    
    def _load_custom_theme(self):
        """Load custom theme from JSON file and populate the custom theme creator."""
        try:
            filename = filedialog.askopenfilename(
                title="Load Custom Theme",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if not filename:
                return
            
            # Read JSON file directly to get colormap colors
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except json.JSONDecodeError as e:
                messagebox.showerror("Error", f"Invalid JSON file: {str(e)}")
                return
            except Exception as e:
                messagebox.showerror("Error", f"Error reading file: {str(e)}")
                return
            
            # Load theme to validate it
            theme = load_custom_theme_from_json(filename)
            
            # Update UI with loaded theme
            self.custom_theme_name.set(theme.name)
            self.custom_theme_background.set(theme.background_color)
            self.relative_scaling.set(theme.relative_scaling)
            self.prefer_horizontal.set(theme.prefer_horizontal)
            
            # Extract colormap colors from JSON if available
            if 'custom_colormaps' in data and isinstance(data['custom_colormaps'], list):
                for cmap_data in data['custom_colormaps']:
                    if cmap_data.get('name') == theme.colormap:
                        colors = cmap_data.get('colors', [])
                        # Update color variables with loaded colors (up to 5)
                        for i, color in enumerate(colors[:5]):
                            if i < len(self.custom_theme_colormap_colors):
                                self.custom_theme_colormap_colors[i].set(color)
                        break
            
            # Enable custom theme creator if not already enabled
            if not self.use_custom_theme_creator.get():
                self.use_custom_theme_creator.set(True)
                self._toggle_custom_theme_panel()
            
            messagebox.showinfo("Success", f"Theme '{theme.name}' loaded successfully!")
            
        except (CustomThemeError, FileHandlerError) as e:
            messagebox.showerror("Error", f"Failed to load theme: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")
    
    def on_select_file(self):
        """Handle file selection button click."""
        # Use format compatible with both Windows and Linux/WSL
        filetypes = [
            ("All supported files", "*.txt *.pdf *.docx *.json"),
            ("Text files", "*.txt"),
            ("PDF files", "*.pdf"),
            ("DOCX files", "*.docx"),
            ("JSON files", "*.json"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Input File",
            filetypes=filetypes,
            defaultextension=""
        )
        
        if filename:
            self.input_file.set(filename)
            # Update label text
            self.file_label.configure(text=filename)
            self._update_file_type_label()
            # Clear output file (user will save after generating and previewing)
            self.output_file.set("")
            self.output_label.configure(text="No word cloud generated yet", text_color="gray")
            # Clear any previously generated word cloud
            self.generated_wordcloud = None
            if self.temp_output_file and Path(self.temp_output_file).exists():
                try:
                    Path(self.temp_output_file).unlink()  # Delete temp file
                except:
                    pass
            self.temp_output_file = None
    
    def _update_file_type_label(self):
        """Update file type label based on selected file."""
        file_path = self.input_file.get()
        if not file_path:
            self.file_type_label.configure(text="")
            return
        
        if is_json_file(file_path):
            self.file_type_label.configure(text="[JSON]", text_color="blue")
            self.language_combo.configure(state="disabled")
        elif is_convertible_document(file_path):
            self.file_type_label.configure(text="[PDF/DOCX]", text_color="green")
            self.language_combo.configure(state="normal")
        else:
            self.file_type_label.configure(text="[TEXT]", text_color="black")
            self.language_combo.configure(state="normal")
    
    def on_select_output(self):
        """Handle saving the generated word cloud using Save As dialog."""
        # Check if there's a generated word cloud to save
        if self.generated_wordcloud is None or self.temp_output_file is None:
            messagebox.showwarning(
                "No Word Cloud Generated",
                "Please generate a word cloud first before saving."
            )
            return
        
        # Suggest a default filename based on input file if available
        initial_file = ""
        if self.input_file.get():
            input_path = Path(self.input_file.get())
            initial_file = str(input_path.parent / f"{input_path.stem}_wordcloud.png")
        else:
            initial_file = "wordcloud.png"
        
        filename = filedialog.asksaveasfilename(
            title="Save Word Cloud As...",
            defaultextension=".png",
            initialfile=initial_file,
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                # Save the generated word cloud to the selected location
                self.generated_wordcloud.to_file(filename)
                self.output_file.set(filename)
                self.output_label.configure(text=f"Saved: {Path(filename).name}")
                self.status_text.set(f"Word cloud saved to: {filename}")
                self.status_label.configure(text=f"Word cloud saved to: {filename}")
                messagebox.showinfo(
                    "Success",
                    f"Word cloud saved successfully!\n\nSaved to:\n{filename}"
                )
            except Exception as e:
                messagebox.showerror(
                    "Save Error",
                    f"Failed to save word cloud:\n{str(e)}"
                )
    
    def _update_preset_mask_list(self):
        """Update the preset mask combobox with current available masks (without extension)."""
        preset_masks = list_mask_files(without_extension=True)
        preset_mask_values = ["None"] + preset_masks + ["Custom..."]
        self.preset_mask_combo.configure(values=preset_mask_values)
    
    def _on_preset_mask_selected(self, value):
        """Handle preset mask selection change."""
        selected = self.preset_mask.get()
        
        if selected == "None":
            # Clear both preset and custom mask
            self.mask_file.set("")
        elif selected == "Custom...":
            # Open file dialog for custom mask
            self.on_select_mask()
            # Reset combobox to show selected file name if a file was chosen
            if self.mask_file.get():
                # Keep "Custom..." selected to show we're using a custom file
                pass
            else:
                # User cancelled, reset to None
                self.preset_mask.set("None")
        else:
            # Preset mask selected - clear custom mask file
            self.mask_file.set("")
            self.mask_file_label.configure(text="")
            # Verify the preset mask exists
            mask_path = get_mask_path(selected)
            if not mask_path:
                messagebox.showwarning(
                    "Mask Not Found",
                    f"Preset mask '{selected}' not found. Please check that masks are properly bundled."
                )
                self.preset_mask.set("None")
    
    def on_select_mask(self):
        """Handle custom mask file selection."""
        filetypes = [
            ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.webp"),
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg *.jpeg"),
            ("All files", "*.*")
        ]
        filename = filedialog.askopenfilename(
            title="Select Mask Image",
            filetypes=filetypes
        )
        
        if filename:
            self.mask_file.set(filename)
            # Update preset mask combo to show we're using a custom file
            self.preset_mask.set("Custom...")
            # Update the values to ensure "Custom..." is available
            self._update_preset_mask_list()
            self.preset_mask.set("Custom...")
    
    def _update_preset_font_list(self):
        """Update the preset font combobox with current available fonts (with friendly display names)."""
        preset_fonts = list_font_files(without_extension=True, with_display_names=True)
        preset_font_values = ["Default"] + preset_fonts + ["Custom..."]
        self.preset_font_combo.configure(values=preset_font_values)
    
    def _on_preset_font_selected(self, value):
        """Handle preset font selection change."""
        selected = self.preset_font.get()
        
        if selected == "Default":
            # Clear both preset and custom font
            self.font_path.set("")
        elif selected == "Custom...":
            # Open file dialog for custom font
            self.on_select_font()
            # Reset combobox to show selected file name if a file was chosen
            if self.font_path.get():
                # Keep "Custom..." selected to show we're using a custom file
                pass
            else:
                # User cancelled, reset to Default
                self.preset_font.set("Default")
        else:
            # Preset font selected - get the font path
            font_path = get_font_path(selected)
            if font_path:
                self.font_path.set(font_path)
            else:
                # Font not found, reset to Default
                self.preset_font.set("Default")
                self.font_path.set("")
                self.font_path_label.configure(text="")
                messagebox.showerror("Error", f"Font '{selected}' not found.")
    
    def on_select_font(self):
        """Handle custom font file selection."""
        filetypes = [
            ("Font files", "*.ttf *.otf"),
            ("TTF files", "*.ttf"),
            ("OTF files", "*.otf"),
            ("All files", "*.*")
        ]
        filename = filedialog.askopenfilename(
            title="Select Font File",
            filetypes=filetypes
        )
        
        if filename:
            self.font_path.set(filename)
            # Update preset font combobox to show we're using a custom file
            self.preset_font.set("Custom...")
            # Update the values to ensure "Custom..." is available
            self._update_preset_font_list()
            self.preset_font.set("Custom...")
    
    def on_generate(self):
        """Handle generate button click."""
        if self.generating:
            messagebox.showwarning("Warning", "Word cloud generation is already in progress.")
            return
        
        # Validate input file
        if not self.input_file.get():
            messagebox.showerror("Error", "Please select an input file.")
            return
        
        # Disable generate button
        self.generate_button.configure(state="disabled")
        self.generating = True
        self.status_text.set("Generating word cloud...")
        self.status_label.configure(text="Generating word cloud...")
        
        # Start generation in separate thread
        thread = threading.Thread(target=self._generate_wordcloud, daemon=True)
        thread.start()
    
    def _generate_wordcloud(self):
        """Internal method to generate word cloud (runs in thread)."""
        try:
            # Get theme or use custom colors
            config = WordCloudConfig()
            
            # Check if using custom theme creator
            if self.use_custom_theme_creator.get():
                # Use custom theme creator settings
                bg_color = self.custom_theme_background.get().strip()
                if not bg_color:
                    self.root.after(0, self._generation_complete, False, "Error: Background color is required for custom theme.")
                    return
                
                # Collect colormap colors
                colormap_colors = [color_var.get().strip() for color_var in self.custom_theme_colormap_colors]
                colormap_colors = [c for c in colormap_colors if c]  # Remove empty
                
                if len(colormap_colors) < 2:
                    self.root.after(0, self._generation_complete, False, "Error: At least 2 colormap colors are required.")
                    return
                
                # Generate unique colormap name for this session
                import time
                colormap_name = f"gui_custom_{int(time.time())}"
                
                # Register custom colormap temporarily
                try:
                    register_custom_colormap(
                        name=colormap_name,
                        colors=colormap_colors,
                        description="Temporary colormap created in GUI"
                    )
                except CustomColormapError:
                    # If colormap already exists, try with different name
                    colormap_name = f"gui_custom_{int(time.time() * 1000)}"
                    register_custom_colormap(
                        name=colormap_name,
                        colors=colormap_colors,
                        description="Temporary colormap created in GUI"
                    )
                
                config.background_color = bg_color
                config.colormap = colormap_name
                config.font_color = None  # Colormap takes precedence
            else:
                # Apply built-in theme
                theme_name = self.theme.get()
                theme = get_theme(theme_name)
                if not theme:
                    self.root.after(0, self._generation_complete, False, f"Error: Theme '{theme_name}' not found.")
                    return
                config.background_color = theme.background_color
                config.font_color = theme.font_color
                config.colormap = theme.colormap
            
            # Set canvas size
            config.canvas_width = self.canvas_width.get()
            config.canvas_height = self.canvas_height.get()
            
            # Set word processing options
            config.max_words = self.max_words.get()
            config.min_word_length = self.min_word_length.get()
            config.include_stopwords = self.include_stopwords.get()
            config.case_sensitive = self.case_sensitive.get()
            config.collocations = self.collocations.get()
            config.normalize_plurals = self.normalize_plurals.get()
            config.include_numbers = self.include_numbers.get()
            
            # Set visual options
            config.relative_scaling = self.relative_scaling.get()
            config.prefer_horizontal = self.prefer_horizontal.get()
            
            # Advanced options - Mask selection (preset or custom)
            mask_file = None
            preset_mask = self.preset_mask.get().strip()
            
            if preset_mask and preset_mask not in ["None", "Custom..."]:
                # Use preset mask
                mask_path = get_mask_path(preset_mask)
                if mask_path:
                    mask_file = mask_path
                else:
                    self.root.after(0, self._generation_complete, False, f"Error: Preset mask '{preset_mask}' not found.")
                    return
            elif preset_mask == "Custom...":
                # Use custom mask file
                mask_file = self.mask_file.get().strip() or None
            # else: preset_mask == "None" -> mask_file remains None
            
            config.mask = mask_file
            config.contour_width = self.contour_width.get()
            contour_color = self.contour_color.get().strip() or None
            config.contour_color = contour_color if contour_color else None
            font_path = self.font_path.get().strip() or None
            config.font_path = font_path if font_path else None
            
            # Language (only for text files, not JSON)
            language = self.language.get() if not is_json_file(self.input_file.get()) else "english"
            
            # Clean up previous temporary file if exists
            if self.temp_output_file and Path(self.temp_output_file).exists():
                try:
                    Path(self.temp_output_file).unlink()
                except:
                    pass
            
            # Process text to get frequencies (without generating image yet)
            frequencies = process_text_to_frequencies(
                input_file=self.input_file.get(),
                language=language,
                config=config,
                clean_text=True
            )
            
            # Generate word cloud to a temporary file for preview
            import tempfile
            import os
            temp_fd, temp_path = tempfile.mkstemp(suffix='.png', prefix='wordcloud_', dir=None)
            os.close(temp_fd)  # Close file descriptor, we'll use the path
            
            # Generate word cloud and save to temp file for preview
            self.generated_wordcloud = generate_word_cloud_from_frequencies(
                frequencies=frequencies,
                config=config,
                output_file=temp_path,
                show=False  # Don't show matplotlib window in GUI
            )
            
            self.temp_output_file = temp_path
            
            # Export stats if requested (only if user had selected output file before)
            # We'll skip stats export during preview generation
            
            # Update preview in main thread
            self.root.after(0, self._update_preview, temp_path)
            # Update output label to show preview is ready
            self.root.after(0, lambda: self.output_label.configure(text="Preview ready - Click 'Save As...' to save", text_color="green"))
            self.root.after(0, self._generation_complete, True, "Word cloud generated successfully! Preview ready.")
            
        except Exception as e:
            # Show error in main thread
            self.root.after(0, self._generation_complete, False, f"Error: {str(e)}")
    
    def _generation_complete(self, success, message):
        """Called when generation completes (in main thread)."""
        self.generating = False
        self.generate_button.configure(state="normal")
        self.status_text.set(message)
        self.status_label.configure(text=message)
        
        if not success:
            messagebox.showerror("Error", message)
        # Don't show success message box - user can see preview and save when ready
    
    def _update_preview(self, image_path):
        """Update the preview area with generated image."""
        try:
            if not image_path:
                self.preview_label.configure(image="", text="Preview not available (no path)")
                return
            
            if not Path(image_path).exists():
                self.preview_label.configure(image="", text=f"Preview not available (file not found: {image_path})")
                return
            
            # Load and resize image for preview (larger preview area)
            img = Image.open(image_path)
            # Resize to fit preview area - larger size for better visibility
            # Default to 700x550 (larger than before) but try to get actual container size
            max_width, max_height = 700, 550  # Default larger size
            
            try:
                # Try to get actual preview container size after window is rendered
                self.preview_label.update_idletasks()
                container_width = self.preview_label.winfo_width()
                container_height = self.preview_label.winfo_height()
                if container_width > 50 and container_height > 50:  # Valid size
                    # Leave some padding (30px on each side)
                    max_width = container_width - 30
                    max_height = container_height - 30
            except:
                pass  # Use defaults if can't get size
            
            # Ensure minimum size for preview
            max_width = max(max_width, 600)
            max_height = max(max_height, 450)
            
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            # Use CTkImage for better compatibility with CustomTkinter
            img_ctk = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
            
            # Update label
            self.preview_label.configure(image=img_ctk, text="")
            self.preview_label.image = img_ctk  # Keep a reference
            self.preview_image = img_ctk
            
        except Exception as e:
            import traceback
            error_msg = f"Error loading preview: {str(e)}"
            print(f"DEBUG _update_preview error: {error_msg}")
            print(traceback.format_exc())
            self.preview_label.configure(image="", text=error_msg)
    
    def _ensure_window_size(self):
        """Ensure window has proper size after widgets are created."""
        # Force minimum size if window is too small
        current_width = self.root.winfo_width()
        current_height = self.root.winfo_height()
        
        if current_width < 1200 or current_height < 700:
            # Window is too small, resize it
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            width = max(1200, min(1500, screen_width - 100))
            height = max(700, min(850, screen_height - 100))
            x = (screen_width // 2) - (width // 2)
            y = (screen_height // 2) - (height // 2)
            self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def _on_closing(self):
        """Handle window closing event - clean up temporary files."""
        # Clean up temporary file if exists
        if self.temp_output_file and Path(self.temp_output_file).exists():
            try:
                Path(self.temp_output_file).unlink()
            except:
                pass
        self.root.destroy()


def main():
    """Entry point for GUI application."""
    root = ctk.CTk()
    app = WordCloudGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
