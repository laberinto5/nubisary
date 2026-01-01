"""Main GUI window for Nubisary."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from PIL import Image, ImageTk
import threading

from src.wordcloud_service import generate_wordcloud, WordCloudServiceError
from src.config import WordCloudConfig, LANGUAGES_FOR_NLTK
from src.themes import get_theme, get_theme_names
from src.file_handlers import is_json_file, is_convertible_document


class WordCloudGUI:
    """Main GUI window for Nubisary word cloud generator."""
    
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.setup_variables()
        self.create_widgets()
        
        # Store preview image reference
        self.preview_image = None
        self.generating = False
    
    def setup_window(self):
        """Configure main window properties."""
        self.root.title("Nubisary - Word Cloud Generator")
        self.root.geometry("900x1000")
        # Center window on screen
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_variables(self):
        """Initialize Tkinter variables."""
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.language = tk.StringVar(value="english")
        self.theme = tk.StringVar(value="classic")
        
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
        
        # Advanced options
        self.use_custom_colors = tk.BooleanVar(value=False)
        self.background_color = tk.StringVar(value="")
        self.font_color = tk.StringVar(value="")
        self.colormap = tk.StringVar(value="")
        self.mask_file = tk.StringVar(value="")
        self.contour_width = tk.DoubleVar(value=0.0)
        self.contour_color = tk.StringVar(value="")
        self.font_path = tk.StringVar(value="")
        
        # Export options
        self.export_stats = tk.BooleanVar(value=False)
        self.stats_top_n = tk.StringVar(value="")
        
        # Status
        self.status_text = tk.StringVar(value="Ready")
    
    def create_widgets(self):
        """Create and layout all GUI widgets."""
        # Main container with scrollbar
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create scrollable canvas
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # 1. Input Section
        input_frame = ttk.LabelFrame(scrollable_frame, text="Input File", padding="10")
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(input_frame, text="Select Input File", command=self.on_select_file).pack(side=tk.LEFT, padx=5)
        ttk.Label(input_frame, textvariable=self.input_file, width=50).pack(side=tk.LEFT, padx=5)
        
        self.file_type_label = ttk.Label(input_frame, text="", foreground="gray")
        self.file_type_label.pack(side=tk.LEFT, padx=5)
        
        # Language selector (only for text files)
        lang_frame = ttk.Frame(input_frame)
        lang_frame.pack(fill=tk.X, pady=5)
        ttk.Label(lang_frame, text="Language:").pack(side=tk.LEFT, padx=5)
        self.language_combo = ttk.Combobox(lang_frame, textvariable=self.language, values=LANGUAGES_FOR_NLTK, state="readonly", width=20)
        self.language_combo.pack(side=tk.LEFT, padx=5)
        
        # 2. Processing Options Section
        proc_frame = ttk.LabelFrame(scrollable_frame, text="Processing Options", padding="10")
        proc_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Checkboxes row 1
        cb_frame1 = ttk.Frame(proc_frame)
        cb_frame1.pack(fill=tk.X, pady=2)
        ttk.Checkbutton(cb_frame1, text="Include stopwords", variable=self.include_stopwords).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(cb_frame1, text="Case sensitive", variable=self.case_sensitive).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(cb_frame1, text="Collocations", variable=self.collocations).pack(side=tk.LEFT, padx=5)
        
        # Checkboxes row 2
        cb_frame2 = ttk.Frame(proc_frame)
        cb_frame2.pack(fill=tk.X, pady=2)
        ttk.Checkbutton(cb_frame2, text="Normalize plurals", variable=self.normalize_plurals).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(cb_frame2, text="Include numbers", variable=self.include_numbers).pack(side=tk.LEFT, padx=5)
        
        # Numeric inputs
        num_frame = ttk.Frame(proc_frame)
        num_frame.pack(fill=tk.X, pady=5)
        ttk.Label(num_frame, text="Min word length:").pack(side=tk.LEFT, padx=5)
        ttk.Spinbox(num_frame, from_=0, to=20, textvariable=self.min_word_length, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(num_frame, text="Max words:").pack(side=tk.LEFT, padx=5)
        ttk.Spinbox(num_frame, from_=1, to=1000, textvariable=self.max_words, width=10).pack(side=tk.LEFT, padx=5)
        
        # 3. Visual Customization Section
        vis_frame = ttk.LabelFrame(scrollable_frame, text="Visual Customization", padding="10")
        vis_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Theme selector
        theme_frame = ttk.Frame(vis_frame)
        theme_frame.pack(fill=tk.X, pady=5)
        ttk.Label(theme_frame, text="Theme:").pack(side=tk.LEFT, padx=5)
        theme_names = get_theme_names()
        self.theme_combo = ttk.Combobox(theme_frame, textvariable=self.theme, values=theme_names, state="readonly", width=30)
        self.theme_combo.pack(side=tk.LEFT, padx=5)
        
        # Canvas size
        size_frame = ttk.Frame(vis_frame)
        size_frame.pack(fill=tk.X, pady=5)
        ttk.Label(size_frame, text="Canvas size:").pack(side=tk.LEFT, padx=5)
        ttk.Spinbox(size_frame, from_=100, to=4000, textvariable=self.canvas_width, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(size_frame, text="x").pack(side=tk.LEFT)
        ttk.Spinbox(size_frame, from_=100, to=4000, textvariable=self.canvas_height, width=10).pack(side=tk.LEFT, padx=5)
        
        # Sliders
        scale_frame = ttk.Frame(vis_frame)
        scale_frame.pack(fill=tk.X, pady=5)
        ttk.Label(scale_frame, text="Relative scaling:").pack(side=tk.LEFT, padx=5)
        scale_slider = ttk.Scale(scale_frame, from_=0.0, to=1.0, variable=self.relative_scaling, orient=tk.HORIZONTAL, length=200)
        scale_slider.pack(side=tk.LEFT, padx=5)
        scale_label = ttk.Label(scale_frame, textvariable=self.relative_scaling, width=5)
        scale_label.pack(side=tk.LEFT, padx=5)
        self.relative_scaling.trace_add("write", lambda *args: scale_label.config(text=f"{self.relative_scaling.get():.2f}"))
        
        horiz_frame = ttk.Frame(vis_frame)
        horiz_frame.pack(fill=tk.X, pady=5)
        ttk.Label(horiz_frame, text="Prefer horizontal:").pack(side=tk.LEFT, padx=5)
        horiz_slider = ttk.Scale(horiz_frame, from_=0.0, to=1.0, variable=self.prefer_horizontal, orient=tk.HORIZONTAL, length=200)
        horiz_slider.pack(side=tk.LEFT, padx=5)
        horiz_label = ttk.Label(horiz_frame, textvariable=self.prefer_horizontal, width=5)
        horiz_label.pack(side=tk.LEFT, padx=5)
        self.prefer_horizontal.trace_add("write", lambda *args: horiz_label.config(text=f"{self.prefer_horizontal.get():.2f}"))
        
        # 4. Advanced Options (Collapsible)
        self.advanced_frame = ttk.LabelFrame(scrollable_frame, text="Advanced Options", padding="10")
        self.advanced_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Custom colors
        color_frame = ttk.Frame(self.advanced_frame)
        color_frame.pack(fill=tk.X, pady=5)
        ttk.Checkbutton(color_frame, text="Use custom colors (overrides theme)", variable=self.use_custom_colors).pack(side=tk.LEFT, padx=5)
        
        custom_color_frame = ttk.Frame(self.advanced_frame)
        custom_color_frame.pack(fill=tk.X, pady=5)
        ttk.Label(custom_color_frame, text="Background:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(custom_color_frame, textvariable=self.background_color, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Label(custom_color_frame, text="Font:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(custom_color_frame, textvariable=self.font_color, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Label(custom_color_frame, text="Colormap:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(custom_color_frame, textvariable=self.colormap, width=15).pack(side=tk.LEFT, padx=5)
        
        # Mask file
        mask_frame = ttk.Frame(self.advanced_frame)
        mask_frame.pack(fill=tk.X, pady=5)
        ttk.Button(mask_frame, text="Select Mask Image", command=self.on_select_mask).pack(side=tk.LEFT, padx=5)
        ttk.Label(mask_frame, textvariable=self.mask_file, width=40).pack(side=tk.LEFT, padx=5)
        
        # Contour options (if mask selected)
        contour_frame = ttk.Frame(self.advanced_frame)
        contour_frame.pack(fill=tk.X, pady=5)
        ttk.Label(contour_frame, text="Contour width:").pack(side=tk.LEFT, padx=5)
        ttk.Spinbox(contour_frame, from_=0.0, to=10.0, textvariable=self.contour_width, width=10, increment=0.5).pack(side=tk.LEFT, padx=5)
        ttk.Label(contour_frame, text="Contour color:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(contour_frame, textvariable=self.contour_color, width=15).pack(side=tk.LEFT, padx=5)
        
        # Font path
        font_frame = ttk.Frame(self.advanced_frame)
        font_frame.pack(fill=tk.X, pady=5)
        ttk.Button(font_frame, text="Select Custom Font", command=self.on_select_font).pack(side=tk.LEFT, padx=5)
        ttk.Label(font_frame, textvariable=self.font_path, width=40).pack(side=tk.LEFT, padx=5)
        
        # Export statistics
        export_frame = ttk.Frame(self.advanced_frame)
        export_frame.pack(fill=tk.X, pady=5)
        ttk.Checkbutton(export_frame, text="Export statistics (JSON/CSV)", variable=self.export_stats).pack(side=tk.LEFT, padx=5)
        ttk.Label(export_frame, text="Top N words:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(export_frame, textvariable=self.stats_top_n, width=10).pack(side=tk.LEFT, padx=5)
        
        # 5. Action Buttons
        action_frame = ttk.Frame(scrollable_frame)
        action_frame.pack(fill=tk.X, padx=5, pady=10)
        
        self.generate_button = ttk.Button(action_frame, text="Generate Word Cloud", command=self.on_generate, style="Accent.TButton")
        self.generate_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(action_frame, text="Select Output File", command=self.on_select_output).pack(side=tk.LEFT, padx=5)
        
        # Status bar
        status_frame = ttk.Frame(scrollable_frame)
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(status_frame, text="Status:").pack(side=tk.LEFT, padx=5)
        ttk.Label(status_frame, textvariable=self.status_text, foreground="blue").pack(side=tk.LEFT, padx=5)
        
        # 6. Output Preview Section
        output_frame = ttk.LabelFrame(scrollable_frame, text="Preview", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.output_label = ttk.Label(output_frame, textvariable=self.output_file, foreground="gray")
        self.output_label.pack(anchor=tk.W, pady=5)
        
        # Preview image area
        preview_container = ttk.Frame(output_frame)
        preview_container.pack(fill=tk.BOTH, expand=True)
        
        self.preview_label = ttk.Label(preview_container, text="No preview available", anchor=tk.CENTER)
        self.preview_label.pack(fill=tk.BOTH, expand=True)
    
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
            self._update_file_type_label()
            # Auto-generate output filename
            input_path = Path(filename)
            output_path = input_path.parent / f"{input_path.stem}_wordcloud.png"
            self.output_file.set(str(output_path))
            self.output_label.config(text=f"Output: {self.output_file.get()}")
    
    def _update_file_type_label(self):
        """Update file type label based on selected file."""
        file_path = self.input_file.get()
        if not file_path:
            self.file_type_label.config(text="")
            return
        
        if is_json_file(file_path):
            self.file_type_label.config(text="[JSON]", foreground="blue")
            self.language_combo.config(state="disabled")
        elif is_convertible_document(file_path):
            self.file_type_label.config(text="[PDF/DOCX]", foreground="green")
            self.language_combo.config(state="readonly")
        else:
            self.file_type_label.config(text="[TEXT]", foreground="black")
            self.language_combo.config(state="readonly")
    
    def on_select_output(self):
        """Handle output file selection."""
        filename = filedialog.asksaveasfilename(
            title="Save Word Cloud As",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if filename:
            self.output_file.set(filename)
            self.output_label.config(text=f"Output: {self.output_file.get()}")
    
    def on_select_mask(self):
        """Handle mask file selection."""
        filetypes = [
            ("Image files", "*.png *.jpg *.jpeg"),
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
    
    def on_select_font(self):
        """Handle font file selection."""
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
    
    def on_generate(self):
        """Handle generate button click."""
        if self.generating:
            messagebox.showwarning("Warning", "Word cloud generation is already in progress.")
            return
        
        # Validate input file
        if not self.input_file.get():
            messagebox.showerror("Error", "Please select an input file.")
            return
        
        # Validate output file
        if not self.output_file.get():
            messagebox.showerror("Error", "Please select an output file.")
            return
        
        # Disable generate button
        self.generate_button.config(state="disabled")
        self.generating = True
        self.status_text.set("Generating word cloud...")
        
        # Start generation in separate thread
        thread = threading.Thread(target=self._generate_wordcloud, daemon=True)
        thread.start()
    
    def _generate_wordcloud(self):
        """Internal method to generate word cloud (runs in thread)."""
        try:
            # Get theme or use custom colors
            config = WordCloudConfig()
            
            # Apply theme if not using custom colors
            if not self.use_custom_colors.get():
                theme_name = self.theme.get()
                theme = get_theme(theme_name)
                config.background_color = theme.background_color
                config.font_color = theme.font_color
                config.colormap = theme.colormap
            else:
                # Use custom colors
                bg_color = self.background_color.get().strip() or None
                font_color = self.font_color.get().strip() or None
                colormap = self.colormap.get().strip() or None
                config.background_color = bg_color if bg_color else None
                config.font_color = font_color if font_color else None
                config.colormap = colormap if colormap else None
            
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
            
            # Advanced options
            mask_file = self.mask_file.get().strip() or None
            config.mask = mask_file
            config.contour_width = self.contour_width.get()
            contour_color = self.contour_color.get().strip() or None
            config.contour_color = contour_color if contour_color else None
            font_path = self.font_path.get().strip() or None
            config.font_path = font_path if font_path else None
            
            # Language (only for text files, not JSON)
            language = self.language.get() if not is_json_file(self.input_file.get()) else "english"
            
            # Export stats
            export_stats = self.export_stats.get()
            stats_top_n = None
            if export_stats and self.stats_top_n.get().strip():
                try:
                    stats_top_n = int(self.stats_top_n.get().strip())
                except ValueError:
                    stats_top_n = None
            
            # Generate word cloud
            generate_wordcloud(
                input_file=self.input_file.get(),
                language=language,
                output_file=self.output_file.get(),
                config=config,
                show=False,  # Don't show matplotlib window in GUI
                clean_text=True,
                export_stats=export_stats,
                stats_output=None,  # Auto-generate from output_file
                stats_top_n=stats_top_n
            )
            
            # Update preview in main thread
            self.root.after(0, self._update_preview, self.output_file.get())
            self.root.after(0, self._generation_complete, True, "Word cloud generated successfully!")
            
        except Exception as e:
            # Show error in main thread
            self.root.after(0, self._generation_complete, False, f"Error: {str(e)}")
    
    def _generation_complete(self, success, message):
        """Called when generation completes (in main thread)."""
        self.generating = False
        self.generate_button.config(state="normal")
        self.status_text.set(message)
        
        if not success:
            messagebox.showerror("Error", message)
    
    def _update_preview(self, image_path):
        """Update the preview area with generated image."""
        try:
            if not image_path or not Path(image_path).exists():
                self.preview_label.config(image="", text="Preview not available")
                return
            
            # Load and resize image for preview
            img = Image.open(image_path)
            # Resize to fit preview area (max 600x400)
            img.thumbnail((600, 400), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            
            # Update label
            self.preview_label.config(image=img_tk, text="")
            self.preview_label.image = img_tk  # Keep a reference
            self.preview_image = img_tk
            
        except Exception as e:
            self.preview_label.config(image="", text=f"Error loading preview: {str(e)}")


def main():
    """Entry point for GUI application."""
    root = tk.Tk()
    app = WordCloudGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
