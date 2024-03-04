"""
Main module of the program - this consists of the GUI and
various input and output screens.
"""
import pathlib
import sys
import tkinter as tk
from ctypes import windll
from tkinter import messagebox
from tkinter import ttk

import auto
import manual
import output


windll.shcore.SetProcessDpiAwareness(True) # Enhanced GUI quality.
TITLE = "Parkrun Data Scraper"
if hasattr(sys, "_MEIPASS"):
    # Executable
    ICON_PATH = pathlib.Path(sys._MEIPASS) / "icon.ico"
else:
    # Through Python.
    ICON_PATH = pathlib.Path(__file__).parent.parent / "icon.ico"


class ParkrunScraper(tk.Tk):
    """Parkrun data collection program GUI."""

    def __init__(self) -> None:
        super().__init__()
        self.title(TITLE)
        self.resizable(False, False)
        self.iconbitmap(ICON_PATH)
    
        self.notebook = ttk.Notebook(self)
        self.automatic_scraper = auto.AutomaticScraper(self.notebook)
        self.manual_scraper = manual.ManualScraper(self.notebook)
        self.output_screen = output.OutputScreen(self.notebook)
        self.automatic_scraper.pack(padx=10, pady=10)
        self.manual_scraper.pack(padx=10, pady=10)
        self.output_screen.pack(padx=10, pady=10)

        self.notebook.add(self.automatic_scraper, text="URL Input")
        self.notebook.add(self.manual_scraper, text="File Input")
        self.notebook.add(self.output_screen, text="Output")
        self.notebook.pack(padx=10, pady=10)
    
    def process_html(self, source: str) -> None:
        """
        Processes the HTML text, extracts relevant data, 
        and outputs the data onto the output screen.
        """
        try:
            try:
                self.output_screen.process(source)
                self.notebook.select(self.output_screen)
            except ZeroDivisionError:
                # Implies no data.
                raise RuntimeError(
                    "No historical data found for given Parkrun.")
        except Exception as e:
            messagebox.showerror(
                "Error",
                    "Unfortunately an error occurred "
                    f"while attempting to parse the HTML data: {e}")


def main() -> None:
    """Main procedure of the program."""
    parkrun_scraper = ParkrunScraper()
    parkrun_scraper.mainloop()


if __name__ == "__main__":
    main()
