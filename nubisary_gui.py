#!/usr/bin/env python3
"""GUI entry point for Nubisary."""

import sys
import tkinter as tk

# Set matplotlib backend before any matplotlib imports
# This must be done before importing any matplotlib modules
import matplotlib
matplotlib.use('TkAgg')

from gui.main import WordCloudGUI


def main():
    """Main entry point for GUI application."""
    try:
        root = tk.Tk()
        app = WordCloudGUI(root)
        root.mainloop()
    except Exception as e:
        # Show error dialog if GUI fails to start
        import tkinter.messagebox as msgbox
        root = tk.Tk()
        root.withdraw()  # Hide main window
        msgbox.showerror(
            "Error",
            f"Failed to start Nubisary GUI:\n{str(e)}"
        )
        sys.exit(1)


if __name__ == '__main__':
    main()

