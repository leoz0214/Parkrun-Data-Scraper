"""
Main module of the program - this consists of the GUI and
various input and output screens.
"""
import tkinter as tk
from ctypes import windll
from tkinter import messagebox
from tkinter import ttk

import auto
import manual


windll.shcore.SetProcessDpiAwareness(1) # Enhanced GUI quality.
TITLE = "Parkrun Data Scraper"


class ParkrunScraper(tk.Tk):
    """Parkrun data collection program GUI."""

    def __init__(self) -> None:
        super().__init__()
        self.title(TITLE)
    
        self.notebook = ttk.Notebook(self)
        self.automatic_scraper = auto.AutomaticScraper(self.notebook)
        self.manual_scraper = manual.ManualScraper(self.notebook)
        self.output_screen = OutputScreen(self.notebook)
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
            pass
        except Exception as e:
            messagebox.showerror(
                "Error",
                    "Unfortunately an error occurred "
                    f"while attempting to parse the HTML data: {e}")


class OutputScreen(tk.Frame):
    """Data output screen, including exportation facilities."""

    def __init__(self, master: ttk.Notebook) -> None:
        super().__init__(master)
        self.no_data_label = tk.Label(
            self, text="No data yet!\nInput a URL or file to get started.")
        self.no_data_label.pack(padx=25, pady=25)


def main() -> None:
    """Main procedure of the program."""
    parkrun_scraper = ParkrunScraper()
    parkrun_scraper.mainloop()


if __name__ == "__main__":
    main()
